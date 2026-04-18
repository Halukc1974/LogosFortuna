"""Import-friendly accessors for the legacy quality analyzer."""

from __future__ import annotations

from logosfortuna._module_loader import load_legacy_module


_quality_module = load_legacy_module(
    "logosfortuna_kod_kalitesi_analizoru",
    "kod-kalitesi-analizoru.py",
)

KodKalitesiAnalizoru = _quality_module.KodKalitesiAnalizoru
QualityAnalyzer = _quality_module.KodKalitesiAnalizoru
main = _quality_module.main
