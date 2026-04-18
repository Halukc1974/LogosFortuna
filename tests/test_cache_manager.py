"""Tests for the cache manager (cache-manager.py)."""

import json
import time

from conftest import _load_skill_module

_mod = _load_skill_module("cache_manager", "cache-manager.py")
CacheManager = _mod.CacheManager


class TestCacheManager:
    def test_init_creates_cache_dir(self, tmp_path):
        cache_dir = tmp_path / "cache"
        manager = CacheManager(cache_dir=str(cache_dir))
        assert cache_dir.exists()

    def test_set_and_get(self, tmp_path):
        manager = CacheManager(cache_dir=str(tmp_path / "cache"))
        key_data = {"file_path": "test.py", "analysis_type": "syntax"}
        value = {"errors": [], "warnings": ["unused import"]}

        assert manager.set(key_data, value) is True

        result = manager.get(key_data)
        assert result == value

    def test_cache_miss(self, tmp_path):
        manager = CacheManager(cache_dir=str(tmp_path / "cache"))
        key_data = {"file_path": "nonexistent.py", "analysis_type": "syntax"}

        result = manager.get(key_data)
        assert result is None

    def test_cache_stats_hit(self, tmp_path):
        manager = CacheManager(cache_dir=str(tmp_path / "cache"))
        key_data = {"file_path": "test.py", "analysis_type": "syntax"}

        manager.set(key_data, "value")
        manager.get(key_data)  # hit
        manager.get({"file_path": "other.py", "analysis_type": "x"})  # miss

        stats = manager.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["sets"] == 1

    def test_cache_expiration(self, tmp_path):
        manager = CacheManager(cache_dir=str(tmp_path / "cache"), ttl_hours=0)
        # TTL of 0 means immediate expiration
        manager.ttl_seconds = 0

        key_data = {"file_path": "test.py", "analysis_type": "syntax"}
        manager.set(key_data, "value")

        time.sleep(0.1)
        result = manager.get(key_data)
        assert result is None

    def test_clear_all(self, tmp_path):
        manager = CacheManager(cache_dir=str(tmp_path / "cache"))

        for i in range(5):
            manager.set({"file_path": f"file{i}.py", "analysis_type": "x"}, f"value{i}")

        cleared = manager.clear()
        assert cleared == 5
        assert manager.get_stats()["total_files"] == 0

    def test_clear_expired(self, tmp_path):
        cache_dir = tmp_path / "cache"
        manager = CacheManager(cache_dir=str(cache_dir), ttl_hours=24)

        key_data = {"file_path": "test.py", "analysis_type": "syntax"}
        manager.set(key_data, "value")

        # Manually expire the cache entry
        cache_files = list(cache_dir.glob("*.json"))
        assert len(cache_files) == 1

        with open(cache_files[0], 'r') as f:
            data = json.load(f)
        data["timestamp"] = "2020-01-01T00:00:00"
        with open(cache_files[0], 'w') as f:
            json.dump(data, f)

        cleared = manager.clear_expired()
        assert cleared == 1

    def test_cleanup(self, tmp_path):
        manager = CacheManager(cache_dir=str(tmp_path / "cache"))
        manager.set({"file_path": "a.py", "analysis_type": "x"}, "v")
        manager.get({"file_path": "a.py", "analysis_type": "x"})

        manager.cleanup()
        stats = manager.get_stats()
        assert stats["hits"] == 0
        assert stats["sets"] == 0
        assert stats["total_files"] == 0

    def test_corrupted_cache_file(self, tmp_path):
        cache_dir = tmp_path / "cache"
        manager = CacheManager(cache_dir=str(cache_dir))

        key_data = {"file_path": "test.py", "analysis_type": "syntax"}
        manager.set(key_data, "value")

        # Corrupt the cache file
        cache_files = list(cache_dir.glob("*.json"))
        cache_files[0].write_text("not valid json{{{")

        result = manager.get(key_data)
        assert result is None  # Should handle gracefully

    def test_hit_rate_calculation(self, tmp_path):
        manager = CacheManager(cache_dir=str(tmp_path / "cache"))
        key = {"file_path": "t.py", "analysis_type": "x"}

        manager.set(key, "v")
        manager.get(key)  # hit
        manager.get(key)  # hit
        manager.get({"file_path": "z.py", "analysis_type": "x"})  # miss

        stats = manager.get_stats()
        assert stats["hit_rate_percent"] == pytest.approx(66.67, abs=0.1)


# Need pytest for approx
import pytest
