#!/usr/bin/env python3
"""
LogosFortuna Çoklu Dil Çeviri Sistemi
Otomatik dil algılama ve çeviri desteği sağlar.
"""

import re
import json
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import locale
import gettext

class CokluDilSistemi:
    def __init__(self, translations_dir: str = None):
        if translations_dir is None:
            # Default translations directory
            self.translations_dir = Path(__file__).parent / "translations"
        else:
            self.translations_dir = Path(translations_dir)

        self.translations_dir.mkdir(exist_ok=True)
        self.current_language = self._detect_system_language()
        self.translations = self._load_translations()

        # Dil algılama için n-gram modelleri
        self.language_models = self._build_language_models()

    def _detect_system_language(self) -> str:
        """Sistem dilini algıla"""
        try:
            # Sistem locale'ından dil kodunu al
            system_locale = locale.getlocale()[0]
            if system_locale:
                lang_code = system_locale.split('_')[0].lower()
                if lang_code in ['tr', 'en', 'de', 'fr']:
                    return lang_code
        except:
            pass

        # Varsayılan olarak Türkçe
        return 'tr'

    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Çeviri dosyalarını yükle"""
        translations = {
            'tr': {},
            'en': {},
            'de': {},
            'fr': {}
        }

        # Varsayılan çeviriler
        default_translations = {
            'tr': {
                'hello': 'merhaba',
                'goodbye': 'güle güle',
                'error': 'hata',
                'success': 'başarı',
                'warning': 'uyarı',
                'file_not_found': 'dosya bulunamadı',
                'operation_completed': 'işlem tamamlandı',
                'please_confirm': 'lütfen onaylayın',
                'continue': 'devam et',
                'cancel': 'iptal',
                'yes': 'evet',
                'no': 'hayır',
                'loading': 'yükleniyor',
                'processing': 'işleniyor',
                'analyzing': 'analiz ediliyor',
                'validating': 'doğrulanıyor',
                'testing': 'test ediliyor'
            },
            'en': {
                'hello': 'hello',
                'goodbye': 'goodbye',
                'error': 'error',
                'success': 'success',
                'warning': 'warning',
                'file_not_found': 'file not found',
                'operation_completed': 'operation completed',
                'please_confirm': 'please confirm',
                'continue': 'continue',
                'cancel': 'cancel',
                'yes': 'yes',
                'no': 'no',
                'loading': 'loading',
                'processing': 'processing',
                'analyzing': 'analyzing',
                'validating': 'validating',
                'testing': 'testing'
            },
            'de': {
                'hello': 'hallo',
                'goodbye': 'auf wiedersehen',
                'error': 'fehler',
                'success': 'erfolg',
                'warning': 'warnung',
                'file_not_found': 'datei nicht gefunden',
                'operation_completed': 'vorgang abgeschlossen',
                'please_confirm': 'bitte bestätigen',
                'continue': 'fortfahren',
                'cancel': 'abbrechen',
                'yes': 'ja',
                'no': 'nein',
                'loading': 'lädt',
                'processing': 'verarbeitet',
                'analyzing': 'analysiert',
                'validating': 'validiert',
                'testing': 'testet'
            },
            'fr': {
                'hello': 'bonjour',
                'goodbye': 'au revoir',
                'error': 'erreur',
                'success': 'succès',
                'warning': 'avertissement',
                'file_not_found': 'fichier non trouvé',
                'operation_completed': 'opération terminée',
                'please_confirm': 'veuillez confirmer',
                'continue': 'continuer',
                'cancel': 'annuler',
                'yes': 'oui',
                'no': 'non',
                'loading': 'chargement',
                'processing': 'traitement',
                'analyzing': 'analyse',
                'validating': 'validation',
                'testing': 'test'
            }
        }

        # Dosyadan çevirileri yükle (varsa)
        for lang in translations.keys():
            translation_file = self.translations_dir / f"{lang}.json"
            if translation_file.exists():
                try:
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        file_translations = json.load(f)
                        translations[lang].update(file_translations)
                except:
                    pass
            else:
                # Varsayılan çevirileri dosyaya kaydet
                with open(translation_file, 'w', encoding='utf-8') as f:
                    json.dump(default_translations[lang], f, indent=2, ensure_ascii=False)

        return translations

    def _build_language_models(self) -> Dict[str, Dict[str, float]]:
        """Dil algılama için n-gram modelleri oluştur"""
        models = {}

        # Basit karakter frequency modelleri
        language_chars = {
            'tr': 'abcçdefgğhıijklmnoöprsştuüvyz',
            'en': 'abcdefghijklmnopqrstuvwxyz',
            'de': 'abcädefghijklmnoöpqrsßtuüvwxyz',
            'fr': 'abcçdefghijklmnopqrstuvwxyzàâäéèêëïîôùûüÿ'
        }

        for lang, chars in language_chars.items():
            models[lang] = {}
            for char in chars:
                # Basit frequency (gerçek uygulamada training data kullanılmalı)
                models[lang][char] = 1.0 / len(chars)

        return models

    def detect_language(self, text: str) -> str:
        """Metnin dilini algıla"""
        if not text:
            return self.current_language

        text = text.lower()
        scores = {}

        for lang, model in self.language_models.items():
            score = 0
            char_count = 0

            for char in text:
                if char in model:
                    score += model[char]
                    char_count += 1

            if char_count > 0:
                scores[lang] = score / char_count
            else:
                scores[lang] = 0

        # En yüksek skora sahip dili döndür
        best_lang = max(scores, key=scores.get)
        return best_lang if scores[best_lang] > 0.1 else 'en'  # Threshold

    def translate(self, text: str, target_lang: str = None, source_lang: str = None) -> str:
        """Metni çevir"""
        if target_lang is None:
            target_lang = self.current_language

        if source_lang is None:
            source_lang = self.detect_language(text)

        if source_lang == target_lang:
            return text

        # Kelime bazlı çeviri
        words = re.findall(r'\b\w+\b', text.lower())
        translated_words = []

        for word in words:
            if word in self.translations[source_lang]:
                translated_word = self.translations[target_lang].get(
                    self.translations[source_lang][word],
                    word  # Fallback to original
                )
            else:
                translated_word = word  # No translation available

            translated_words.append(translated_word)

        # Orijinal metni koru, sadece çevirilebilir kelimeleri değiştir
        result = text
        for original, translated in zip(words, translated_words):
            if original != translated:
                # Case-sensitive replacement
                pattern = re.compile(re.escape(original), re.IGNORECASE)
                result = pattern.sub(translated, result, count=1)

        return result

    def set_language(self, lang: str) -> bool:
        """Aktif dili değiştir"""
        if lang in self.translations:
            self.current_language = lang
            return True
        return False

    def get_supported_languages(self) -> List[str]:
        """Desteklenen dilleri listele"""
        return list(self.translations.keys())

    def add_translation(self, key: str, translations: Dict[str, str]) -> bool:
        """Yeni çeviri ekle"""
        try:
            for lang, translation in translations.items():
                if lang in self.translations:
                    self.translations[lang][key] = translation

            # Dosyaları güncelle
            for lang in self.translations:
                translation_file = self.translations_dir / f"{lang}.json"
                with open(translation_file, 'w', encoding='utf-8') as f:
                    json.dump(self.translations[lang], f, indent=2, ensure_ascii=False)

            return True
        except:
            return False

    def format_date(self, date: datetime, lang: str = None) -> str:
        """Dile uygun tarih formatı"""
        if lang is None:
            lang = self.current_language

        formats = {
            'tr': '%d.%m.%Y',
            'en': '%m/%d/%Y',
            'de': '%d.%m.%Y',
            'fr': '%d/%m/%Y'
        }

        format_str = formats.get(lang, '%Y-%m-%d')
        return date.strftime(format_str)

    def format_datetime(self, dt: datetime, lang: str = None) -> str:
        """Dile uygun tarih-saat formatı"""
        if lang is None:
            lang = self.current_language

        formats = {
            'tr': '%d.%m.%Y %H:%M:%S',
            'en': '%m/%d/%Y %I:%M:%S %p',
            'de': '%d.%m.%Y %H:%M:%S',
            'fr': '%d/%m/%Y %H:%M:%S'
        }

        format_str = formats.get(lang, '%Y-%m-%d %H:%M:%S')
        return dt.strftime(format_str)

    def localize_message(self, key: str, lang: str = None, **kwargs) -> str:
        """Yerelleştirilmiş mesaj al"""
        if lang is None:
            lang = self.current_language

        message = self.translations.get(lang, {}).get(key, key)

        # Placeholder'ları doldur
        if kwargs:
            try:
                message = message.format(**kwargs)
            except:
                pass  # Format hatası olursa orijinal mesajı döndür

        return message

    def get_cultural_context(self, lang: str = None) -> Dict[str, str]:
        """Dile özel kültür bağlamı"""
        if lang is None:
            lang = self.current_language

        contexts = {
            'tr': {
                'naming_style': 'snake_case',
                'comment_style': 'turkish',
                'date_format': 'DD.MM.YYYY',
                'time_format': '24h',
                'decimal_separator': ',',
                'communication_style': 'direct'
            },
            'en': {
                'naming_style': 'snake_case/camelCase',
                'comment_style': 'english',
                'date_format': 'MM/DD/YYYY',
                'time_format': '12h',
                'decimal_separator': '.',
                'communication_style': 'professional'
            },
            'de': {
                'naming_style': 'snake_case',
                'comment_style': 'german',
                'date_format': 'DD.MM.YYYY',
                'time_format': '24h',
                'decimal_separator': ',',
                'communication_style': 'technical'
            },
            'fr': {
                'naming_style': 'snake_case',
                'comment_style': 'french',
                'date_format': 'DD/MM/YYYY',
                'time_format': '24h',
                'decimal_separator': ',',
                'communication_style': 'elegant'
            }
        }

        return contexts.get(lang, contexts['en'])

# Global instance
_translation_system = None

def get_translation_system() -> CokluDilSistemi:
    """Global çeviri sistemi instance"""
    global _translation_system
    if _translation_system is None:
        _translation_system = CokluDilSistemi()
    return _translation_system

# Convenience functions
def translate_text(text: str, target_lang: str = None) -> str:
    """Metni çevir"""
    return get_translation_system().translate(text, target_lang)

def detect_lang(text: str) -> str:
    """Dil algıla"""
    return get_translation_system().detect_language(text)

def set_lang(lang: str) -> bool:
    """Dil ayarla"""
    return get_translation_system().set_language(lang)

def localize(key: str, **kwargs) -> str:
    """Yerelleştirilmiş mesaj al"""
    return get_translation_system().localize_message(key, **kwargs)

def format_date_localized(date: datetime) -> str:
    """Yerelleştirilmiş tarih formatı"""
    return get_translation_system().format_date(date)

if __name__ == "__main__":
    # Test kodu
    ts = CokluDilSistemi()

    # Dil algılama testi
    test_texts = [
        "merhaba dünya",
        "hello world",
        "hallo welt",
        "bonjour monde"
    ]

    print("Dil Algılama Testi:")
    for text in test_texts:
        detected = ts.detect_language(text)
        print(f"'{text}' -> {detected}")

    # Çeviri testi
    print("\nÇeviri Testi:")
    text = "merhaba dünya"
    for lang in ['en', 'de', 'fr']:
        translated = ts.translate(text, lang, 'tr')
        print(f"TR '{text}' -> {lang.upper()} '{translated}'")

    # Yerelleştirme testi
    print("\nYerelleştirme Testi:")
    for lang in ['tr', 'en', 'de', 'fr']:
        ts.set_language(lang)
        message = ts.localize_message('hello')
        print(f"{lang.upper()}: {message}")

    # Kültür bağlamı
    print("\nKültür Bağlamı:")
    for lang in ['tr', 'en', 'de', 'fr']:
        context = ts.get_cultural_context(lang)
        print(f"{lang.upper()}: {context['naming_style']}, {context['communication_style']}")