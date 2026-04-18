#!/usr/bin/env python3
"""
LogosFortuna Kişiselleştirme ve UX Sistemi
Kullanıcı deneyimini optimize eden akıllı sistem.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import hashlib

class KullaniciProfili:
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.profile_path = Path.home() / ".logosfortuna" / "profiles" / f"{user_id}.json"
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)

        self.profile = self._load_profile()
        self.session_data = {
            "start_time": datetime.now(),
            "commands_used": [],
            "errors_encountered": [],
            "features_used": [],
            "time_spent": {}
        }

    def _load_profile(self) -> Dict[str, Any]:
        """Kullanıcı profilini yükle"""
        default_profile = {
            "user_id": self.user_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "experience_level": "beginner",  # beginner, intermediate, advanced, expert
            "preferred_language": "tr",
            "communication_style": "balanced",  # concise, balanced, detailed
            "visual_preferences": {
                "theme": "auto",  # light, dark, auto
                "animations": "moderate",  # minimal, moderate, rich
                "layout": "standard"  # compact, standard, spacious
            },
            "work_patterns": {
                "peak_hours": [],  # En aktif saatler
                "preferred_days": [],  # En aktif günler
                "session_duration": 0,  # Ortalama oturum süresi (dakika)
                "project_types": []  # Sık çalıştığı proje türleri
            },
            "command_history": {
                "most_used": [],  # En sık kullanılan komutlar
                "recent": [],  # Son kullanılan komutlar
                "favorites": []  # Favori komutlar
            },
            "learning_progress": {
                "skills_learned": [],
                "difficult_topics": [],
                "preferred_learning_style": "practical"  # theoretical, practical, visual
            },
            "gamification": {
                "level": 1,
                "points": 0,
                "achievements": [],
                "current_streak": 0,
                "best_streak": 0
            },
            "adaptive_features": {
                "shortcut_suggestions": [],
                "command_predictions": [],
                "ui_customizations": {},
                "notification_preferences": {
                    "frequency": "moderate",  # minimal, moderate, detailed
                    "types": ["errors", "success", "progress"]
                }
            }
        }

        if self.profile_path.exists():
            try:
                with open(self.profile_path, 'r', encoding='utf-8') as f:
                    loaded_profile = json.load(f)
                    # Default değerlerle birleştir
                    self._merge_profiles(default_profile, loaded_profile)
                    return default_profile
            except (json.JSONDecodeError, OSError, ValueError):
                pass

        return default_profile

    def _merge_profiles(self, default: Dict[str, Any], loaded: Dict[str, Any]):
        """Profil güncellemelerini birleştir"""
        def merge_dict(target, source):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    merge_dict(target[key], value)
                else:
                    target[key] = value

        merge_dict(default, loaded)

    def save_profile(self):
        """Profili kaydet"""
        self.profile["last_updated"] = datetime.now().isoformat()

        with open(self.profile_path, 'w', encoding='utf-8') as f:
            json.dump(self.profile, f, indent=2, ensure_ascii=False)

    def update_experience_level(self):
        """Deneyim seviyesini güncelle"""
        points = self.profile["gamification"]["points"]
        achievements = len(self.profile["achievements"])

        if points >= 1000 and achievements >= 10:
            self.profile["experience_level"] = "expert"
        elif points >= 500 and achievements >= 5:
            self.profile["experience_level"] = "advanced"
        elif points >= 100 and achievements >= 2:
            self.profile["experience_level"] = "intermediate"
        else:
            self.profile["experience_level"] = "beginner"

    def add_command_usage(self, command: str, success: bool = True):
        """Komut kullanımını kaydet"""
        self.session_data["commands_used"].append({
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "success": success
        })

        # Komut geçmişini güncelle
        recent_commands = self.profile["command_history"]["recent"]
        recent_commands.insert(0, command)
        recent_commands[:] = recent_commands[:10]  # Son 10 komutu tut

        # En sık kullanılanları güncelle
        all_commands = [cmd["command"] for cmd in self.session_data["commands_used"]]
        most_common = Counter(all_commands).most_common(5)
        self.profile["command_history"]["most_used"] = [cmd for cmd, _ in most_common]

    def add_error(self, error_type: str, context: str = ""):
        """Hata kullanımını kaydet"""
        self.session_data["errors_encountered"].append({
            "type": error_type,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })

        # Zor konular listesini güncelle
        difficult_topics = self.profile["learning_progress"]["difficult_topics"]
        if error_type not in difficult_topics:
            difficult_topics.append(error_type)

    def add_achievement(self, achievement_id: str, name: str, points: int):
        """Başarı ekle"""
        if achievement_id not in [a["id"] for a in self.profile["gamification"]["achievements"]]:
            achievement = {
                "id": achievement_id,
                "name": name,
                "points": points,
                "unlocked_at": datetime.now().isoformat()
            }

            self.profile["gamification"]["achievements"].append(achievement)
            self.profile["gamification"]["points"] += points
            self.update_experience_level()

            return True
        return False

    def get_personalized_suggestions(self) -> Dict[str, Any]:
        """Kişiselleştirilmiş öneriler"""
        suggestions = {
            "recommended_commands": [],
            "ui_improvements": {},
            "learning_resources": [],
            "productivity_tips": []
        }

        # Önerilen komutlar
        most_used = self.profile["command_history"]["most_used"][:3]
        suggestions["recommended_commands"] = most_used

        # UI iyileştirmeleri
        experience_level = self.profile["experience_level"]
        if experience_level == "beginner":
            suggestions["ui_improvements"] = {
                "show_tooltips": True,
                "simplified_mode": True,
                "extra_guidance": True
            }
        elif experience_level == "expert":
            suggestions["ui_improvements"] = {
                "keyboard_shortcuts": True,
                "advanced_features": True,
                "compact_layout": True
            }

        # Öğrenme kaynakları
        difficult_topics = self.profile["learning_progress"]["difficult_topics"]
        if difficult_topics:
            suggestions["learning_resources"] = [
                f"{topic} hakkında daha fazla bilgi"
                for topic in difficult_topics[:2]
            ]

        # Verimlilik ipuçları
        current_hour = datetime.now().hour
        peak_hours = self.profile["work_patterns"]["peak_hours"]

        if peak_hours and current_hour not in peak_hours:
            suggestions["productivity_tips"].append(
                f"En verimli olduğun saatler: {', '.join(map(str, peak_hours))}"
            )

        return suggestions

    def get_adaptive_ui_settings(self) -> Dict[str, Any]:
        """Adaptive UI ayarları"""
        experience_level = self.profile["experience_level"]
        communication_style = self.profile["communication_style"]

        settings = {
            "layout": "standard",
            "detail_level": "balanced",
            "interaction_style": "standard",
            "feedback_level": "moderate"
        }

        # Deneyim seviyesine göre
        if experience_level == "beginner":
            settings.update({
                "layout": "guided",
                "detail_level": "detailed",
                "interaction_style": "assisted",
                "feedback_level": "high"
            })
        elif experience_level == "expert":
            settings.update({
                "layout": "compact",
                "detail_level": "concise",
                "interaction_style": "efficient",
                "feedback_level": "minimal"
            })

        # İletişim tarzına göre
        if communication_style == "concise":
            settings["detail_level"] = "concise"
        elif communication_style == "detailed":
            settings["detail_level"] = "detailed"

        return settings

    def analyze_session(self) -> Dict[str, Any]:
        """Oturum analizi"""
        session_duration = (datetime.now() - self.session_data["start_time"]).total_seconds() / 60

        analysis = {
            "duration_minutes": round(session_duration, 1),
            "commands_used": len(self.session_data["commands_used"]),
            "errors_count": len(self.session_data["errors_encountered"]),
            "success_rate": 0.0,
            "most_used_command": None,
            "productivity_score": 0
        }

        # Başarı oranı
        if analysis["commands_used"] > 0:
            successful_commands = sum(1 for cmd in self.session_data["commands_used"] if cmd["success"])
            analysis["success_rate"] = round(successful_commands / analysis["commands_used"] * 100, 1)

        # En çok kullanılan komut
        if self.session_data["commands_used"]:
            commands = [cmd["command"] for cmd in self.session_data["commands_used"]]
            analysis["most_used_command"] = Counter(commands).most_common(1)[0][0]

        # Verimlilik skoru (basit hesaplama)
        base_score = 50
        base_score += min(analysis["success_rate"], 100) * 0.3
        base_score += min(analysis["commands_used"] * 2, 30)  # Aktivite bonusu
        base_score -= analysis["errors_count"] * 5  # Hata cezası

        analysis["productivity_score"] = max(0, min(100, round(base_score)))

        return analysis

    def end_session(self):
        """Oturumu sonlandır ve profili güncelle"""
        session_analysis = self.analyze_session()

        # Çalışma paternlerini güncelle
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()

        work_patterns = self.profile["work_patterns"]
        work_patterns["peak_hours"].append(current_hour)
        work_patterns["preferred_days"].append(current_day)

        # Tekrarları sınırla
        work_patterns["peak_hours"] = list(set(work_patterns["peak_hours"][-10:]))
        work_patterns["preferred_days"] = list(set(work_patterns["preferred_days"][-7:]))

        # Oturum süresini güncelle
        sessions_count = len([s for s in work_patterns.get("sessions", [])])
        current_avg = work_patterns["session_duration"]
        new_avg = (current_avg * sessions_count + session_analysis["duration_minutes"]) / (sessions_count + 1)
        work_patterns["session_duration"] = round(new_avg, 1)

        # Gamification güncellemeleri
        points_earned = session_analysis["productivity_score"] // 10
        self.profile["gamification"]["points"] += points_earned

        # Streak güncellemeleri
        if session_analysis["productivity_score"] >= 70:
            self.profile["gamification"]["current_streak"] += 1
            self.profile["gamification"]["best_streak"] = max(
                self.profile["gamification"]["best_streak"],
                self.profile["gamification"]["current_streak"]
            )
        else:
            self.profile["gamification"]["current_streak"] = 0

        # Başarı kontrolü
        self._check_achievements(session_analysis)

        # Profili kaydet
        self.save_profile()

    def _check_achievements(self, session_analysis: Dict[str, Any]):
        """Yeni başarıları kontrol et"""
        achievements_to_check = [
            ("first_session", "İlk Oturum", 10, lambda: True),
            ("productive_session", "Verimli Oturum", 25, lambda: session_analysis["productivity_score"] >= 80),
            ("error_free", "Hatasız Oturum", 30, lambda: session_analysis["errors_count"] == 0),
            ("speed_demon", "Hız Şampiyonu", 20, lambda: session_analysis["duration_minutes"] < 30),
            ("consistent_worker", "Düzenli Çalışan", 50, lambda: self.profile["gamification"]["current_streak"] >= 5),
        ]

        for achievement_id, name, points, condition in achievements_to_check:
            if condition() and self.add_achievement(achievement_id, name, points):
                print(f"🎉 Yeni başarı: {name} (+{points} puan)")

class SesliKomutSistemi:
    def __init__(self):
        self.commands = {
            "tr": {
                "analiz_et": ["analiz et", "kod analiz et", "çalıştır analiz"],
                "test_et": ["test et", "çalıştır test", "testleri başlat"],
                "dogrula": ["doğrula", "kontrol et", "geçerli mi"],
                "yardim": ["yardım", "nasıl yapılır", "anlamadım"],
                "dur": ["dur", "durdur", "bitir"],
                "devam_et": ["devam et", "ilerle", "sonraki"]
            },
            "en": {
                "analyze": ["analyze", "check code", "run analysis"],
                "test": ["test", "run tests", "start testing"],
                "validate": ["validate", "check", "verify"],
                "help": ["help", "how to", "i don't understand"],
                "stop": ["stop", "halt", "finish"],
                "continue": ["continue", "proceed", "next"]
            }
        }

        self.wake_words = ["logos", "fortuna", "hey assistant", "merhaba"]

    def process_voice_command(self, audio_text: str, language: str = "tr") -> Optional[str]:
        """Sesli komutu işle"""
        text = audio_text.lower().strip()

        # Wake word kontrolü
        if not any(wake_word in text for wake_word in self.wake_words):
            return None

        # Komut çıkarımı
        for command, variations in self.commands.get(language, {}).items():
            if any(variation in text for variation in variations):
                return command

        return None

    def get_voice_feedback(self, action: str, language: str = "tr") -> str:
        """Sesli geri bildirim"""
        feedback = {
            "tr": {
                "analyzing": "Kod analiz ediliyor",
                "testing": "Testler çalıştırılıyor",
                "validating": "Doğrulama yapılıyor",
                "completed": "İşlem tamamlandı",
                "error": "Bir hata oluştu",
                "help": "Size nasıl yardımcı olabilirim?"
            },
            "en": {
                "analyzing": "Analyzing code",
                "testing": "Running tests",
                "validating": "Validating",
                "completed": "Operation completed",
                "error": "An error occurred",
                "help": "How can I help you?"
            }
        }

        return feedback.get(language, feedback["en"]).get(action, "")

# Global instances
_user_profile = None
_voice_system = None

def get_user_profile(user_id: str = "default") -> KullaniciProfili:
    """Global kullanıcı profili instance"""
    global _user_profile
    if _user_profile is None or _user_profile.user_id != user_id:
        _user_profile = KullaniciProfili(user_id)
    return _user_profile

def get_voice_system() -> SesliKomutSistemi:
    """Global sesli komut sistemi instance"""
    global _voice_system
    if _voice_system is None:
        _voice_system = SesliKomutSistemi()
    return _voice_system

if __name__ == "__main__":
    # Test kodu
    profile = get_user_profile()

    # Komut kullanımı simülasyonu
    profile.add_command_usage("analyze_code", True)
    profile.add_command_usage("run_tests", False)
    profile.add_error("syntax_error", "missing semicolon")

    # Başarı ekleme
    profile.add_achievement("first_udiv", "İlk UDIV", 100)

    # Öneriler
    suggestions = profile.get_personalized_suggestions()
    print("Kişiselleştirilmiş öneriler:")
    print(json.dumps(suggestions, indent=2, ensure_ascii=False))

    # Adaptive UI
    ui_settings = profile.get_adaptive_ui_settings()
    print("\nAdaptive UI ayarları:")
    print(json.dumps(ui_settings, indent=2, ensure_ascii=False))

    # Oturum analizi
    analysis = profile.analyze_session()
    print("\nOturum analizi:")
    print(json.dumps(analysis, indent=2, ensure_ascii=False))

    # Oturumu sonlandır
    profile.end_session()

    # Sesli komut testi
    voice_system = get_voice_system()
    test_commands = [
        "logos analiz et",
        "hey assistant run tests",
        "fortuna yardım et"
    ]

    print("\nSesli komut testi:")
    for cmd in test_commands:
        result = voice_system.process_voice_command(cmd, "tr")
        print(f"'{cmd}' -> {result}")