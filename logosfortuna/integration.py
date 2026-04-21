"""Import-friendly accessors for the legacy integration script."""

from __future__ import annotations

from logosfortuna._module_loader import load_legacy_module


_integration_module = load_legacy_module(
    "logosfortuna_entegrasyon_sistemi",
    "entegrasyon-sistemi.py",
)

EntegrasyonYoneticisi = _integration_module.EntegrasyonYoneticisi
GitHubIntegrationError = _integration_module.GitHubIntegrationError
configure_discord = _integration_module.configure_discord
configure_github = _integration_module.configure_github
configure_slack = _integration_module.configure_slack
create_github_issue = _integration_module.create_github_issue
comment_on_github_pull_request = _integration_module.comment_on_github_pull_request
get_github_connection_status = _integration_module.get_github_connection_status
get_integration_manager = _integration_module.get_integration_manager
get_integration_status = _integration_module.get_integration_status
list_github_issues = _integration_module.list_github_issues
list_github_pull_requests = _integration_module.list_github_pull_requests
main = _integration_module.main
send_notification = _integration_module.send_notification

if hasattr(_integration_module, "add_custom_webhook"):
    add_custom_webhook = _integration_module.add_custom_webhook
