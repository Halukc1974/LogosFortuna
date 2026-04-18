#!/usr/bin/env python3
"""
LogosFortuna Cache Manager
Sık kullanılan analiz sonuçlarını cache'ler ve performans optimizasyonu sağlar.
"""

import json
import os
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self, cache_dir: str = None, ttl_hours: int = 24):
        if cache_dir is None:
            # Default cache directory
            home = os.path.expanduser("~")
            cache_dir = os.path.join(home, ".logosfortuna", "cache")

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_hours * 3600

        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "clears": 0
        }

    def _generate_key(self, data: Dict[str, Any]) -> str:
        """Cache key oluştur"""
        # Dosya yolu + analiz türü + dosya hash kombinasyonu
        key_data = {
            "file_path": data.get("file_path", ""),
            "analysis_type": data.get("analysis_type", ""),
            "content_hash": data.get("content_hash", "")
        }

        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]

    def _get_cache_path(self, key: str) -> Path:
        """Cache dosya yolu"""
        return self.cache_dir / f"{key}.json"

    def _is_expired(self, cache_data: Dict[str, Any]) -> bool:
        """Cache süresi dolmuş mu kontrol et"""
        if "timestamp" not in cache_data:
            return True

        cache_time = datetime.fromisoformat(cache_data["timestamp"])
        expiry_time = cache_time + timedelta(seconds=self.ttl_seconds)

        return datetime.now() > expiry_time

    def get(self, key_data: Dict[str, Any]) -> Optional[Any]:
        """Cache'den veri al"""
        key = self._generate_key(key_data)
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            self.stats["misses"] += 1
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            if self._is_expired(cache_data):
                # Süresi dolmuş cache'i sil
                cache_path.unlink()
                self.stats["misses"] += 1
                return None

            self.stats["hits"] += 1
            return cache_data.get("data")

        except (json.JSONDecodeError, KeyError, OSError):
            # Bozuk cache dosyasını sil
            if cache_path.exists():
                cache_path.unlink()
            self.stats["misses"] += 1
            return None

    def set(self, key_data: Dict[str, Any], value: Any, custom_ttl: int = None) -> bool:
        """Cache'e veri kaydet"""
        key = self._generate_key(key_data)
        cache_path = self._get_cache_path(key)

        ttl = custom_ttl or self.ttl_seconds

        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "ttl_seconds": ttl,
            "key_data": key_data,
            "data": value
        }

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

            self.stats["sets"] += 1
            return True

        except OSError:
            return False

    def clear(self, pattern: str = None) -> int:
        """Cache temizle"""
        cleared_count = 0

        if pattern:
            # Pattern'e göre temizle
            for cache_file in self.cache_dir.glob(f"*{pattern}*.json"):
                try:
                    cache_file.unlink()
                    cleared_count += 1
                except OSError:
                    pass
        else:
            # Tüm cache'i temizle
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                    cleared_count += 1
                except OSError:
                    pass

        self.stats["clears"] += cleared_count
        return cleared_count

    def clear_expired(self) -> int:
        """Süresi dolmuş cache'leri temizle"""
        cleared_count = 0

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                if self._is_expired(cache_data):
                    cache_file.unlink()
                    cleared_count += 1

            except (json.JSONDecodeError, OSError):
                # Bozuk dosyaları da sil
                try:
                    cache_file.unlink()
                    cleared_count += 1
                except OSError:
                    pass

        return cleared_count

    def get_stats(self) -> Dict[str, int]:
        """Cache istatistikleri"""
        total_files = len(list(self.cache_dir.glob("*.json")))
        hit_rate = 0.0

        total_requests = self.stats["hits"] + self.stats["misses"]
        if total_requests > 0:
            hit_rate = (self.stats["hits"] / total_requests) * 100

        return {
            **self.stats,
            "total_files": total_files,
            "hit_rate_percent": round(hit_rate, 2)
        }

    def cleanup(self):
        """Cache dizinini temizle ve istatistikleri sıfırla"""
        self.clear()
        self.stats = {k: 0 for k in self.stats}

# Global cache instance
_cache_instance = None

def get_cache_manager() -> CacheManager:
    """Global cache manager instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager()
    return _cache_instance

# Convenience functions
def cache_get(key_data: Dict[str, Any]) -> Optional[Any]:
    """Cache'den veri al"""
    return get_cache_manager().get(key_data)

def cache_set(key_data: Dict[str, Any], value: Any, ttl_hours: int = None) -> bool:
    """Cache'e veri kaydet"""
    return get_cache_manager().set(key_data, value, ttl_hours * 3600 if ttl_hours else None)

def cache_clear(pattern: str = None) -> int:
    """Cache temizle"""
    return get_cache_manager().clear(pattern)

def cache_stats() -> Dict[str, int]:
    """Cache istatistikleri"""
    return get_cache_manager().get_stats()

if __name__ == "__main__":
    # Test kodu
    cache = CacheManager()

    # Test verisi
    test_key = {"file_path": "test.py", "analysis_type": "syntax_check"}
    test_value = {"errors": [], "warnings": ["Unused import"]}

    # Cache'e kaydet
    print("Cache'e kaydediliyor...")
    cache.set(test_key, test_value)

    # Cache'den oku
    print("Cache'den okunuyor...")
    result = cache.get(test_key)
    print(f"Sonuç: {result}")

    # İstatistikler
    print(f"İstatistikler: {cache.get_stats()}")

    # Temizle
    print(f"Temizlenen dosya sayısı: {cache.clear()}")