"""Import-friendly accessors for the legacy security scanner."""

from __future__ import annotations

from logosfortuna._module_loader import load_legacy_module


_security_module = load_legacy_module(
    "logosfortuna_guvenlik_tarayici",
    "guvenlik-tarayici.py",
)

GuvenlikTarayici = _security_module.GuvenlikTarayici
SecurityScanner = _security_module.GuvenlikTarayici
main = _security_module.main
