import json
import pathlib
import sys
import tempfile
import unittest
from datetime import date


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

import radar_cli
from collab_utils import dump_db_to_jsonl, sync_db_from_jsonl
from persona_and_freshness import compute_freshness, enrich_all_signals
from signal_time import source_day, source_time


class SignalTimeTest(unittest.TestCase):
    def test_time_requires_date_or_explicit_offset(self):
        self.assertEqual(source_time("2026-11-24"), ("2026-11-24", "date"))
        self.assertEqual(source_time("2026-11-24T08:00:00Z"), ("2026-11-24T08:00:00+00:00", "timestamp"))
        for value in ("", "2026-02-30", "2026-11-24T08:00:00"):
            with self.subTest(value=value):
                self.assertEqual(source_time(value), ("", "unknown"))

    def test_source_day_is_consistent_across_offsets(self):
        ref = date(2026, 11, 24)
        self.assertEqual(source_day("2026-11-23T17:00:00Z"), "2026-11-24")
        self.assertEqual(source_day("2026-11-24T01:00:00+08:00"), "2026-11-24")
        self.assertEqual(compute_freshness("2026-11-17", ref)[0], "7d_hot")
        self.assertEqual(compute_freshness("2026-11-16", ref)[0], "30d_active")
        self.assertEqual(compute_freshness("2026-11-25", ref)[0], "recent_unverified")

    def test_collecting_old_content_today_does_not_make_it_recent(self):
        conn = radar_cli.get_conn(pathlib.Path(":memory:"))
        radar_cli.init_db(conn)
        defaults = dict.fromkeys(("source_tier", "category", "query_term", "content", "author_or_app",
                                 "metric_primary", "metric_secondary", "rating_or_price", "source_url"), "")
        for title, source in (("已核实旧帖", "2024-01-01"), ("旧版未核实", ""), ("今天有日期", "2026-11-24")):
            radar_cli.insert_signal(conn, "测试", title=title, published_at="2026-11-24",
                                    source_published_at=source, **defaults)
        enrich_all_signals(conn, "2026-11-24")
        self.assertEqual(
            {r["title"]: (r["freshness_tier"], r["published_at"]) for r in conn.execute("SELECT * FROM raw_signals")},
            {"已核实旧帖": ("stale_archive", "2026-11-24"),
             "旧版未核实": ("recent_unverified", "2026-11-24"),
             "今天有日期": ("7d_hot", "2026-11-24")},
        )
        conn.close()

    def test_legacy_migration_and_archive_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            archive = root / "data/signals/signals_master.jsonl"
            archive.parent.mkdir(parents=True)
            old = {
                "id": 42, "channel": "App Store", "title": "旧线索", "content": "原文",
                "published_at": "2024-01-01", "collected_at": "2024-01-15 12:00:00",
                "first_seen": "2024-01-15", "last_seen": "2024-01-16",
                "source_url": "https://example.test/old",
            }
            archive.write_text(json.dumps(old) + "\n", encoding="utf-8")
            conn = radar_cli.get_conn(root / "radar.db")
            radar_cli.init_db(conn)
            conn.execute("ALTER TABLE raw_signals DROP COLUMN source_published_at")
            radar_cli.init_db(conn)
            radar_cli.init_db(conn)
            self.assertEqual(sync_db_from_jsonl(conn, root, radar_cli.insert_signal), 1)
            self.assertEqual(sync_db_from_jsonl(conn, root, radar_cli.insert_signal), 0)
            new = {
                **old, "id": 71, "title": "新资料", "source_published_at": "2026-11-24T16:00:00+08:00",
                "published_time_source": "测试来源", "observed_at": "2026-11-24T08:30:00+00:00",
            }
            with archive.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(new) + "\n")
            self.assertEqual(sync_db_from_jsonl(conn, root, radar_cli.insert_signal), 1)
            dump_db_to_jsonl(conn, root)
            conn.close()
            restored = radar_cli.get_conn(root / "restored.db")
            radar_cli.init_db(restored)
            self.assertEqual(sync_db_from_jsonl(restored, root, radar_cli.insert_signal), 2)
            rows = {r["id"]: dict(r) for r in restored.execute("SELECT * FROM raw_signals")}
            restored.close()
            for field in ("content", "published_at", "collected_at", "first_seen", "last_seen", "source_url"):
                self.assertEqual(rows[42][field], old[field])
            self.assertEqual(rows[42]["observed_at"], "")
            self.assertEqual(rows[71]["source_published_at"], new["source_published_at"])
            self.assertEqual(rows[71]["published_time_precision"], "timestamp")
            self.assertEqual(rows[71]["observed_at"], new["observed_at"])

    def test_existing_rows_restore_missing_dates_before_rearchiving(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = pathlib.Path(folder.name)
        archive = root / "data/signals/signals_master.jsonl"
        archive.parent.mkdir(parents=True)
        archived = {
            "id": 42, "channel": "B站", "title": "旧线索",
            "first_seen": "2026-11-18", "last_seen": "2026-11-24",
            "observed_at": "2026-11-24T08:30:00+00:00",
        }
        archive.write_text(json.dumps(archived) + "\n", encoding="utf-8")
        conn = radar_cli.get_conn(root / "radar.db")
        self.addCleanup(conn.close)
        radar_cli.init_db(conn)
        conn.execute(
            """INSERT INTO raw_signals (id, channel, source_tier, category,
                  query_term, title, content, collected_at) VALUES (?, ?, '', '', '', ?, '', ?)""",
            (42, archived["channel"], archived["title"], "2026-11-18 12:00:00"),
        )
        self.assertEqual(sync_db_from_jsonl(conn, root, radar_cli.insert_signal), 0)
        archive.write_text(json.dumps({**archived, "last_seen": "2026-11-25"}) + "\n", encoding="utf-8")
        self.assertEqual(sync_db_from_jsonl(conn, root, radar_cli.insert_signal), 0)
        dump_db_to_jsonl(conn, root)
        snapshot = json.loads(archive.read_text(encoding="utf-8"))
        restored = conn.execute("SELECT * FROM raw_signals").fetchone()
        for field in ("id", "first_seen", "last_seen", "observed_at"):
            self.assertEqual(snapshot[field], archived[field])
            self.assertEqual(restored[field], archived[field])


if __name__ == "__main__":
    unittest.main()
