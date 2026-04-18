#!/usr/bin/env python3
"""
LogosFortuna Entegrasyon Test Sistemi
Tüm entegrasyon özelliklerini test eder.
"""

import json
import os
import sys
import time
from pathlib import Path
from scripts.entegrasyon_sistemi import get_integration_manager, send_notification

def test_basic_notifications():
    """Temel bildirim sistemini test et"""
    print("🔔 Temel bildirim sistemi test ediliyor...")

    manager = get_integration_manager()

    # Test bildirimleri
    test_cases = [
        {
            "event": "analysis_complete",
            "data": {"quality_score": 85, "project": "test-project"},
            "priority": "normal"
        },
        {
            "event": "error_detected",
            "data": {"error_message": "Syntax error in main.py", "line": 42},
            "priority": "high"
        },
        {
            "event": "security_alert",
            "data": {"vulnerability": "SQL Injection risk", "severity": "high"},
            "priority": "critical"
        },
        {
            "event": "quality_improved",
            "data": {"improvement": 15, "new_score": 90},
            "priority": "normal"
        },
        {
            "event": "deployment_success",
            "data": {"environment": "production", "version": "1.2.3"},
            "priority": "normal"
        }
    ]

    for test_case in test_cases:
        print(f"  Gönderiliyor: {test_case['event']} ({test_case['priority']})")
        send_notification(test_case["event"], test_case["data"], test_case["priority"])
        time.sleep(0.5)  # Rate limiting için

    print("✅ Temel bildirim testleri tamamlandı")
    return True

def test_configuration():
    """Yapılandırma sistemini test et"""
    print("⚙️ Yapılandırma sistemi test ediliyor...")

    manager = get_integration_manager()

    # Test yapılandırmaları (gerçek token/webhook olmadan)
    try:
        # GitHub yapılandırma testi
        result = manager.configure_github("test_token", ["test-repo1", "test-repo2"])
        print(f"  GitHub yapılandırma: {'✅' if result else '❌'}")

        # Slack yapılandırma testi
        result = manager.configure_slack("https://hooks.slack.com/test", "#test-channel")
        print(f"  Slack yapılandırma: {'✅' if result else '❌'}")

        # Discord yapılandırma testi
        result = manager.configure_discord("https://discord.com/api/webhooks/test")
        print(f"  Discord yapılandırma: {'✅' if result else '❌'}")

        # Özel webhook ekleme testi
        result = manager.add_custom_webhook(
            "https://test-webhook.com/notify",
            ["analysis_complete", "error_detected"],
            "test-webhook"
        )
        print(f"  Özel webhook ekleme: {'✅' if result else '❌'}")

        print("✅ Yapılandırma testleri tamamlandı")
        return True

    except Exception as e:
        print(f"❌ Yapılandırma testi hatası: {e}")
        return False

def test_batch_notifications():
    """Batch bildirim sistemini test et"""
    print("📦 Batch bildirim sistemi test ediliyor...")

    manager = get_integration_manager()

    # Çoklu benzer bildirim gönder
    for i in range(5):
        send_notification(
            "analysis_complete",
            {"quality_score": 70 + i, "project": f"batch-test-{i}"},
            "normal"
        )
        time.sleep(0.1)

    print("✅ Batch bildirim testleri tamamlandı")
    return True

def test_integration_status():
    """Entegrasyon durumunu test et"""
    print("📊 Entegrasyon durumu kontrol ediliyor...")

    manager = get_integration_manager()
    status = manager.get_integration_status()

    print("  Mevcut durum:")
    for key, value in status.items():
        status_icon = "✅" if value else "❌"
        if isinstance(value, int):
            status_icon = f"📊 {value}"
        print(f"    {key}: {status_icon}")

    print("✅ Entegrasyon durumu kontrolü tamamlandı")
    return True

def test_quiet_hours():
    """Sessiz saatler özelliğini test et"""
    print("🌙 Sessiz saatler testi...")

    manager = get_integration_manager()

    # Sessiz saatler ayarını test et
    config = manager.config
    original_quiet = config["notifications"]["quiet_hours"]["enabled"]

    # Sessiz saatleri etkinleştir
    config["notifications"]["quiet_hours"]["enabled"] = True
    config["notifications"]["quiet_hours"]["start"] = "22:00"
    config["notifications"]["quiet_hours"]["end"] = "08:00"

    # Şu anki zamanı kontrol et
    from datetime import datetime
    now = datetime.now().time()
    quiet_start = datetime.strptime("22:00", "%H:%M").time()
    quiet_end = datetime.strptime("08:00", "%H:%M").time()

    is_quiet_now = manager._is_quiet_hours()
    print(f"  Şu an sessiz saatlerde: {'✅' if is_quiet_now else '❌'}")

    # Test bildirim gönder (sessiz saatlerde gönderilmemeli)
    send_notification("test_quiet_hours", {"test": True}, "normal")

    # Ayarı geri al
    config["notifications"]["quiet_hours"]["enabled"] = original_quiet

    print("✅ Sessiz saatler testi tamamlandı")
    return True

def run_full_test():
    """Tüm testleri çalıştır"""
    print("🚀 LogosFortuna Entegrasyon Sistemi - Tam Test Başlatılıyor")
    print("=" * 60)

    tests = [
        test_basic_notifications,
        test_configuration,
        test_batch_notifications,
        test_integration_status,
        test_quiet_hours
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test hatası ({test.__name__}): {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"📈 Test Sonuçları: {passed} başarılı, {failed} başarısız")

    if failed == 0:
        print("🎉 Tüm entegrasyon testleri başarılı!")
        return True
    else:
        print("⚠️ Bazı testler başarısız oldu.")
        return False

def main():
    """Ana fonksiyon"""
    if len(sys.argv) > 1:
        test_name = sys.argv[1]

        if test_name == "basic":
            test_basic_notifications()
        elif test_name == "config":
            test_configuration()
        elif test_name == "batch":
            test_batch_notifications()
        elif test_name == "status":
            test_integration_status()
        elif test_name == "quiet":
            test_quiet_hours()
        else:
            print(f"Bilinmeyen test: {test_name}")
            print("Kullanım: python entegrasyon-test.py [basic|config|batch|status|quiet]")
    else:
        # Tüm testleri çalıştır
        success = run_full_test()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()