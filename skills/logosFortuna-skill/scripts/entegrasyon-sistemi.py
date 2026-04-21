#!/usr/bin/env python3
"""
LogosFortuna Entegrasyon Sistemi
GitHub, Slack, CI/CD sistemleri ile entegrasyon sağlar.
"""

import argparse
import json
import os
import requests
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import threading
import queue
from urllib.parse import urlparse


class GitHubIntegrationError(RuntimeError):
    """Raised when a GitHub API operation cannot be completed."""

class EntegrasyonYoneticisi:
    def __init__(self, config_file: str = None):
        if config_file:
            self.config_file = Path(config_file)
        else:
            self.config_file = Path.home() / ".logosfortuna" / "integrations.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        self.config = self._load_config()
        self.notification_queue = queue.Queue()
        self.webhook_threads = {}

        # Notification worker thread
        self.worker_thread = threading.Thread(target=self._notification_worker, daemon=True)
        self.worker_thread.start()

    def _load_config(self) -> Dict[str, Any]:
        """Entegrasyon yapılandırmasını yükle"""
        default_config = {
            "github": {
                "enabled": False,
                "token": "",
                "repositories": [],
                "webhooks": [],
                "api_base_url": "https://api.github.com"
            },
            "slack": {
                "enabled": False,
                "webhook_url": "",
                "channel": "#logosfortuna",
                "username": "LogosFortuna Bot"
            },
            "discord": {
                "enabled": False,
                "webhook_url": "",
                "username": "LogosFortuna"
            },
            "jenkins": {
                "enabled": False,
                "url": "",
                "username": "",
                "api_token": "",
                "jobs": []
            },
            "gitlab": {
                "enabled": False,
                "url": "",
                "token": "",
                "projects": []
            },
            "webhooks": {
                "custom_webhooks": [],
                "retry_attempts": 3,
                "timeout": 30
            },
            "notifications": {
                "enabled_events": [
                    "analysis_complete",
                    "error_detected",
                    "quality_improved",
                    "deployment_success",
                    "security_alert"
                ],
                "quiet_hours": {
                    "enabled": False,
                    "start": "22:00",
                    "end": "08:00"
                },
                "batch_notifications": {
                    "enabled": True,
                    "max_delay": 300  # 5 dakika
                }
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self._merge_configs(default_config, loaded_config)
            except (json.JSONDecodeError, OSError, ValueError):
                pass

        return default_config

    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]):
        """Yapılandırma güncellemelerini birleştir"""
        def merge_dict(target, source):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    merge_dict(target[key], value)
                else:
                    target[key] = value

        merge_dict(default, loaded)

    def save_config(self):
        """Yapılandırmayı kaydet"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def configure_github(self, token: str, repositories: List[str], api_base_url: str = "https://api.github.com") -> bool:
        """GitHub entegrasyonunu yapılandır"""
        try:
            self.config["github"].update({
                "enabled": True,
                "token": token,
                "repositories": repositories,
                "api_base_url": api_base_url.rstrip("/")
            })
            self.save_config()
            return True
        except (OSError, KeyError, TypeError) as e:
            print(f"GitHub configuration error: {e}", file=sys.stderr)
            return False

    def _get_github_token(self) -> str:
        token = self.config["github"].get("token") or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        if not token:
            raise GitHubIntegrationError("GitHub token bulunamadi. Konfigürasyon veya GITHUB_TOKEN gerekli.")
        return token

    def _get_github_api_base_url(self) -> str:
        return self.config["github"].get("api_base_url") or "https://api.github.com"

    def _resolve_github_repository(self, repository: Optional[str] = None) -> str:
        repo = repository or (self.config["github"].get("repositories") or [None])[0]
        if not repo:
            raise GitHubIntegrationError("GitHub repository belirtilmedi. --github-repo kullanin veya konfigurasyonda repos tanimlayin.")
        if "/" not in repo or repo.count("/") != 1:
            raise GitHubIntegrationError(f"Gecersiz GitHub repository formati: {repo}")
        return repo

    def _github_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._get_github_token()}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "LogosFortuna/1.0"
        }

    def _github_api_request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Any:
        base_url = self._get_github_api_base_url().rstrip("/")
        url = f"{base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(
                method,
                url,
                headers=self._github_headers(),
                params=params,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise GitHubIntegrationError(f"GitHub API hatasi: {exc}") from exc

        if response.status_code == 204 or not response.content:
            return {}

        try:
            return response.json()
        except ValueError as exc:
            raise GitHubIntegrationError("GitHub API JSON olmayan bir cevap dondurdu.") from exc

    def get_github_connection_status(self) -> Dict[str, Any]:
        """GitHub token ve API baglantisini dogrula."""
        user_payload = self._github_api_request("GET", "/user")
        return {
            "enabled": self.config["github"]["enabled"],
            "authenticated": True,
            "viewer": user_payload.get("login"),
            "name": user_payload.get("name"),
            "api_base_url": self._get_github_api_base_url(),
            "repositories": list(self.config["github"].get("repositories", [])),
        }

    def list_github_pull_requests(
        self,
        repository: Optional[str] = None,
        *,
        state: str = "open",
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Configure edilen repo icin pull request listesini al."""
        repo = self._resolve_github_repository(repository)
        items = self._github_api_request(
            "GET",
            f"/repos/{repo}/pulls",
            params={"state": state, "per_page": limit},
        )
        pulls = [
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": item.get("state"),
                "draft": item.get("draft", False),
                "author": (item.get("user") or {}).get("login"),
                "branch": (item.get("head") or {}).get("ref"),
                "url": item.get("html_url"),
                "created_at": item.get("created_at"),
            }
            for item in items
        ]
        return {"repository": repo, "state": state, "count": len(pulls), "items": pulls}

    def list_github_issues(
        self,
        repository: Optional[str] = None,
        *,
        state: str = "open",
        limit: int = 20,
        include_pull_requests: bool = False,
    ) -> Dict[str, Any]:
        """Configure edilen repo icin issue listesini al."""
        repo = self._resolve_github_repository(repository)
        items = self._github_api_request(
            "GET",
            f"/repos/{repo}/issues",
            params={"state": state, "per_page": limit},
        )

        filtered_items = []
        for item in items:
            if not include_pull_requests and "pull_request" in item:
                continue
            filtered_items.append(
                {
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "state": item.get("state"),
                    "author": (item.get("user") or {}).get("login"),
                    "labels": [label.get("name") for label in item.get("labels", [])],
                    "url": item.get("html_url"),
                    "created_at": item.get("created_at"),
                }
            )

        return {"repository": repo, "state": state, "count": len(filtered_items), "items": filtered_items}

    def create_github_issue(
        self,
        title: str,
        body: str = "",
        *,
        repository: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """GitHub issue olustur."""
        repo = self._resolve_github_repository(repository)
        payload = self._github_api_request(
            "POST",
            f"/repos/{repo}/issues",
            payload={
                "title": title,
                "body": body,
                "labels": labels or [],
            },
        )
        return {
            "repository": repo,
            "number": payload.get("number"),
            "title": payload.get("title"),
            "state": payload.get("state"),
            "url": payload.get("html_url"),
            "labels": [label.get("name") for label in payload.get("labels", [])],
        }

    def comment_on_github_pull_request(
        self,
        pull_number: int,
        body: str,
        *,
        repository: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Bir pull request'e issue comment ekle."""
        repo = self._resolve_github_repository(repository)
        payload = self._github_api_request(
            "POST",
            f"/repos/{repo}/issues/{pull_number}/comments",
            payload={"body": body},
        )
        return {
            "repository": repo,
            "pull_number": pull_number,
            "comment_id": payload.get("id"),
            "url": payload.get("html_url"),
            "body": payload.get("body"),
        }

    def configure_slack(self, webhook_url: str, channel: str = "#logosfortuna") -> bool:
        """Slack entegrasyonunu yapılandır"""
        try:
            self.config["slack"].update({
                "enabled": True,
                "webhook_url": webhook_url,
                "channel": channel
            })
            self.save_config()
            return True
        except (OSError, KeyError, TypeError) as e:
            print(f"Slack configuration error: {e}", file=sys.stderr)
            return False

    def configure_discord(self, webhook_url: str) -> bool:
        """Discord entegrasyonunu yapılandır"""
        try:
            self.config["discord"].update({
                "enabled": True,
                "webhook_url": webhook_url
            })
            self.save_config()
            return True
        except (OSError, KeyError, TypeError) as e:
            print(f"Discord configuration error: {e}", file=sys.stderr)
            return False

    def add_custom_webhook(self, url: str, events: List[str], name: str = None) -> bool:
        """Özel webhook ekle"""
        try:
            webhook = {
                "name": name or f"webhook_{len(self.config['webhooks']['custom_webhooks'])}",
                "url": url,
                "events": events,
                "enabled": True,
                "created_at": datetime.now().isoformat()
            }

            self.config["webhooks"]["custom_webhooks"].append(webhook)
            self.save_config()
            return True
        except (OSError, KeyError, TypeError) as e:
            print(f"Webhook configuration error: {e}", file=sys.stderr)
            return False

    def send_notification(self, event_type: str, data: Dict[str, Any], priority: str = "normal"):
        """Bildirim gönder"""
        if event_type not in self.config["notifications"]["enabled_events"]:
            return

        notification = {
            "event_type": event_type,
            "data": data,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "id": f"{event_type}_{int(time.time())}"
        }

        self.notification_queue.put(notification)

    def _notification_worker(self):
        """Bildirim işleme worker thread"""
        batch_notifications = []
        last_batch_time = time.time()

        while True:
            try:
                # Queue'dan bildirim al (timeout ile)
                notification = self.notification_queue.get(timeout=1)

                current_time = time.time()

                # Batch processing
                if self.config["notifications"]["batch_notifications"]["enabled"]:
                    batch_notifications.append(notification)

                    # Batch delay süresi dolduysa gönder
                    if current_time - last_batch_time >= self.config["notifications"]["batch_notifications"]["max_delay"]:
                        self._send_batch_notifications(batch_notifications)
                        batch_notifications = []
                        last_batch_time = current_time
                else:
                    # Immediate sending
                    self._send_notification(notification)

                self.notification_queue.task_done()

            except queue.Empty:
                # Batch varsa gönder
                if batch_notifications:
                    self._send_batch_notifications(batch_notifications)
                    batch_notifications = []
                    last_batch_time = time.time()
                continue

    def _send_batch_notifications(self, notifications: List[Dict[str, Any]]):
        """Batch bildirim gönder"""
        if not notifications:
            return

        # Grupla
        grouped = {}
        for notification in notifications:
            event_type = notification["event_type"]
            if event_type not in grouped:
                grouped[event_type] = []
            grouped[event_type].append(notification)

        # Her grup için özet bildirim gönder
        for event_type, group_notifications in grouped.items():
            summary_data = {
                "event_type": f"batch_{event_type}",
                "count": len(group_notifications),
                "summary": f"{len(group_notifications)} {event_type} olayları",
                "first_event": group_notifications[0]["timestamp"],
                "last_event": group_notifications[-1]["timestamp"]
            }

            notification = {
                "event_type": f"batch_{event_type}",
                "data": summary_data,
                "priority": "normal",
                "timestamp": datetime.now().isoformat()
            }

            self._send_notification(notification)

    def _send_notification(self, notification: Dict[str, Any]):
        """Tek bildirim gönder"""
        # Quiet hours kontrolü
        if self._is_quiet_hours():
            return

        # Slack
        if self.config["slack"]["enabled"]:
            self._send_slack_notification(notification)

        # Discord
        if self.config["discord"]["enabled"]:
            self._send_discord_notification(notification)

        # Custom webhooks
        for webhook in self.config["webhooks"]["custom_webhooks"]:
            if notification["event_type"] in webhook["events"] and webhook["enabled"]:
                self._send_custom_webhook(webhook, notification)

    def _send_slack_notification(self, notification: Dict[str, Any]):
        """Slack bildirim gönder"""
        try:
            webhook_url = self.config["slack"]["webhook_url"]
            if not webhook_url:
                return

            # Slack message format
            message = {
                "channel": self.config["slack"]["channel"],
                "username": self.config["slack"]["username"],
                "icon_emoji": ":robot_face:",
                "attachments": [{
                    "color": self._get_priority_color(notification["priority"]),
                    "title": self._format_event_title(notification["event_type"]),
                    "text": self._format_notification_text(notification),
                    "footer": "LogosFortuna",
                    "ts": int(time.time())
                }]
            }

            response = requests.post(webhook_url, json=message, timeout=10)
            response.raise_for_status()

        except Exception as e:
            print(f"Slack notification error: {e}")

    def _send_discord_notification(self, notification: Dict[str, Any]):
        """Discord bildirim gönder"""
        try:
            webhook_url = self.config["discord"]["webhook_url"]
            if not webhook_url:
                return

            # Discord message format
            message = {
                "username": self.config["discord"]["username"],
                "embeds": [{
                    "color": self._get_priority_color_discord(notification["priority"]),
                    "title": self._format_event_title(notification["event_type"]),
                    "description": self._format_notification_text(notification),
                    "footer": {
                        "text": "LogosFortuna"
                    },
                    "timestamp": notification["timestamp"]
                }]
            }

            response = requests.post(webhook_url, json=message, timeout=10)
            response.raise_for_status()

        except Exception as e:
            print(f"Discord notification error: {e}")

    def _send_custom_webhook(self, webhook_config: Dict[str, Any], notification: Dict[str, Any]):
        """Özel webhook gönder"""
        try:
            url = webhook_config["url"]
            if not url:
                return

            payload = {
                "webhook_name": webhook_config["name"],
                "notification": notification,
                "source": "LogosFortuna"
            }

            # Retry logic
            max_retries = self.config["webhooks"]["retry_attempts"]
            timeout = self.config["webhooks"]["timeout"]

            for attempt in range(max_retries):
                try:
                    response = requests.post(url, json=payload, timeout=timeout)
                    response.raise_for_status()
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"Webhook error after {max_retries} attempts: {e}")
                    else:
                        time.sleep(2 ** attempt)  # Exponential backoff

        except Exception as e:
            print(f"Custom webhook error: {e}")

    def _is_quiet_hours(self) -> bool:
        """Sessiz saatler kontrolü"""
        if not self.config["notifications"]["quiet_hours"]["enabled"]:
            return False

        now = datetime.now().time()
        start = datetime.strptime(self.config["notifications"]["quiet_hours"]["start"], "%H:%M").time()
        end = datetime.strptime(self.config["notifications"]["quiet_hours"]["end"], "%H:%M").time()

        if start <= end:
            return start <= now <= end
        else:  # Gece yarısını kapsayan durum
            return now >= start or now <= end

    def _get_priority_color(self, priority: str) -> str:
        """Slack için priority renk kodu"""
        colors = {
            "low": "good",
            "normal": "warning",
            "high": "danger",
            "critical": "#FF0000"
        }
        return colors.get(priority, "warning")

    def _get_priority_color_discord(self, priority: str) -> int:
        """Discord için priority renk kodu"""
        colors = {
            "low": 0x00FF00,      # Yeşil
            "normal": 0xFFFF00,   # Sarı
            "high": 0xFF8800,     # Turuncu
            "critical": 0xFF0000  # Kırmızı
        }
        return colors.get(priority, 0xFFFF00)

    def _format_event_title(self, event_type: str) -> str:
        """Event tipini başlık formatına çevir"""
        titles = {
            "analysis_complete": "Kod Analizi Tamamlandı",
            "error_detected": "Hata Tespit Edildi",
            "quality_improved": "Kalite İyileştirildi",
            "deployment_success": "Deployment Başarılı",
            "security_alert": "Güvenlik Uyarısı",
            "batch_analysis_complete": "Çoklu Analiz Tamamlandı",
            "batch_error_detected": "Çoklu Hata Tespit Edildi"
        }
        return titles.get(event_type, event_type.replace("_", " ").title())

    def _format_notification_text(self, notification: Dict[str, Any]) -> str:
        """Bildirim metnini formatla"""
        event_type = notification["event_type"]
        data = notification["data"]

        if event_type.startswith("batch_"):
            return f"{data['count']} adet {event_type.replace('batch_', '').replace('_', ' ')} olayı tespit edildi."

        if event_type == "analysis_complete":
            return f"Proje analizi tamamlandı. Kalite skoru: {data.get('quality_score', 'N/A')}"

        if event_type == "error_detected":
            return f"Hata tespit edildi: {data.get('error_message', 'Detay yok')}"

        if event_type == "quality_improved":
            return f"Kalite skoru {data.get('improvement', 0)} puan arttı!"

        if event_type == "deployment_success":
            return f"{data.get('environment', 'production')} ortamına deployment başarılı."

        if event_type == "security_alert":
            return f"Güvenlik açığı tespit edildi: {data.get('vulnerability', 'Detay yok')}"

        return json.dumps(data, indent=2, ensure_ascii=False)

    def get_integration_status(self) -> Dict[str, Any]:
        """Entegrasyon durumunu döndür"""
        status = {
            "github": self.config["github"]["enabled"],
            "github_repository_count": len(self.config["github"].get("repositories", [])),
            "github_api_base_url": self._get_github_api_base_url(),
            "slack": self.config["slack"]["enabled"],
            "discord": self.config["discord"]["enabled"],
            "jenkins": self.config["jenkins"]["enabled"],
            "gitlab": self.config["gitlab"]["enabled"],
            "custom_webhooks": len([w for w in self.config["webhooks"]["custom_webhooks"] if w["enabled"]]),
            "queue_size": self.notification_queue.qsize()
        }
        return status

# Global instance
_integration_manager = None

def get_integration_manager() -> EntegrasyonYoneticisi:
    """Global entegrasyon yöneticisi instance"""
    global _integration_manager
    if _integration_manager is None:
        _integration_manager = EntegrasyonYoneticisi()
    return _integration_manager

# Convenience functions
def send_notification(event_type: str, data: Dict[str, Any], priority: str = "normal"):
    """Bildirim gönder"""
    get_integration_manager().send_notification(event_type, data, priority)

def configure_github(token: str, repositories: List[str]) -> bool:
    """GitHub yapılandır"""
    return get_integration_manager().configure_github(token, repositories)


def get_github_connection_status() -> Dict[str, Any]:
    """GitHub baglanti durumunu dondur."""
    return get_integration_manager().get_github_connection_status()


def list_github_pull_requests(
    repository: Optional[str] = None,
    *,
    state: str = "open",
    limit: int = 20,
) -> Dict[str, Any]:
    """GitHub pull request akisini dondur."""
    return get_integration_manager().list_github_pull_requests(repository, state=state, limit=limit)


def list_github_issues(
    repository: Optional[str] = None,
    *,
    state: str = "open",
    limit: int = 20,
    include_pull_requests: bool = False,
) -> Dict[str, Any]:
    """GitHub issue akisini dondur."""
    return get_integration_manager().list_github_issues(
        repository,
        state=state,
        limit=limit,
        include_pull_requests=include_pull_requests,
    )


def create_github_issue(
    title: str,
    body: str = "",
    *,
    repository: Optional[str] = None,
    labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """GitHub issue olustur."""
    return get_integration_manager().create_github_issue(title, body, repository=repository, labels=labels)


def comment_on_github_pull_request(
    pull_number: int,
    body: str,
    *,
    repository: Optional[str] = None,
) -> Dict[str, Any]:
    """GitHub pull request yorum akisi."""
    return get_integration_manager().comment_on_github_pull_request(
        pull_number,
        body,
        repository=repository,
    )

def configure_slack(webhook_url: str, channel: str = "#logosfortuna") -> bool:
    """Slack yapılandır"""
    return get_integration_manager().configure_slack(webhook_url, channel)

def configure_discord(webhook_url: str) -> bool:
    """Discord yapılandır"""
    return get_integration_manager().configure_discord(webhook_url)

def get_integration_status() -> Dict[str, Any]:
    """Entegrasyon durumu"""
    return get_integration_manager().get_integration_status()


def _parse_repositories(value: str) -> List[str]:
    """Virgulle ayrilmis repo listesini temizle."""
    return [repo.strip() for repo in value.split(",") if repo.strip()]


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="LogosFortuna entegrasyon sistemi icin kurulum ve test yardimcisi"
    )
    parser.add_argument("--config", help="Alternatif config dosyasi yolu")
    parser.add_argument("--setup", action="store_true", help="Mevcut config durumunu yazdir")
    parser.add_argument("--status", action="store_true", help="Etkin entegrasyon durumunu yazdir")
    parser.add_argument("--test-notifications", action="store_true", help="Ornek bildirimler gonder")

    parser.add_argument("--configure-github", action="store_true", help="GitHub entegrasyonunu yapilandir")
    parser.add_argument("--token", help="GitHub veya diger servisler icin token")
    parser.add_argument("--repos", help="Virgulle ayrilmis repo listesi")
    parser.add_argument("--github-api-url", default="https://api.github.com", help="GitHub API taban adresi")
    parser.add_argument("--github-repo", help="GitHub repository (owner/repo)")
    parser.add_argument("--github-connection", action="store_true", help="GitHub baglanti durumunu sorgula")
    parser.add_argument("--github-list-pulls", action="store_true", help="GitHub pull request listesini getir")
    parser.add_argument("--github-list-issues", action="store_true", help="GitHub issue listesini getir")
    parser.add_argument("--github-create-issue", action="store_true", help="GitHub issue olustur")
    parser.add_argument("--github-comment-pr", action="store_true", help="GitHub pull request yorum ekle")
    parser.add_argument("--state", choices=["open", "closed", "all"], default="open", help="GitHub issue/pull state filtresi")
    parser.add_argument("--limit", type=int, default=20, help="GitHub listesi icin max kayit sayisi")
    parser.add_argument("--title", help="Issue basligi")
    parser.add_argument("--body", help="Issue veya yorum govdesi")
    parser.add_argument("--labels", help="Virgulle ayrilmis label listesi")
    parser.add_argument("--pull-number", type=int, help="Pull request numarasi")

    parser.add_argument("--configure-slack", action="store_true", help="Slack entegrasyonunu yapilandir")
    parser.add_argument("--configure-discord", action="store_true", help="Discord entegrasyonunu yapilandir")
    parser.add_argument("--webhook", help="Slack, Discord veya custom webhook URL")
    parser.add_argument("--channel", default="#logosfortuna", help="Slack kanali")

    parser.add_argument("--add-custom-webhook", action="store_true", help="Ozel webhook ekle")
    parser.add_argument("--events", help="Virgulle ayrilmis olay listesi")
    parser.add_argument("--name", help="Webhook adi")
    return parser


def _print_json(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _run_test_notifications(manager: EntegrasyonYoneticisi) -> int:
    test_notifications = [
        {
            "event_type": "analysis_complete",
            "data": {"quality_score": 85, "project": "test-project"},
            "priority": "normal"
        },
        {
            "event_type": "error_detected",
            "data": {"error_message": "Syntax error in main.py", "line": 42},
            "priority": "high"
        },
        {
            "event_type": "security_alert",
            "data": {"vulnerability": "SQL Injection risk", "severity": "high"},
            "priority": "critical"
        }
    ]

    print("Entegrasyon testi baslatiliyor...")
    print("Not: webhook'lar yalnizca yapilandirilmissa gercek gonderim denenir.")

    for notification in test_notifications:
        print(f"Bildirim gonderiliyor: {notification['event_type']}")
        manager.send_notification(
            notification["event_type"],
            notification["data"],
            notification["priority"]
        )
        time.sleep(1)

    time.sleep(2)
    _print_json(manager.get_integration_status())
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_argument_parser()
    args = parser.parse_args(argv)
    manager = EntegrasyonYoneticisi(config_file=args.config)

    action_taken = False

    if args.configure_github:
        if not args.token or not args.repos:
            parser.error("--configure-github icin --token ve --repos gerekli")
        repositories = _parse_repositories(args.repos)
        success = manager.configure_github(args.token, repositories, api_base_url=args.github_api_url)
        _print_json({
            "action": "configure_github",
            "success": success,
            "repositories": repositories,
            "api_base_url": args.github_api_url,
        })
        action_taken = True

    if args.github_connection:
        _print_json(manager.get_github_connection_status())
        action_taken = True

    if args.github_list_pulls:
        _print_json(
            manager.list_github_pull_requests(
                repository=args.github_repo,
                state=args.state,
                limit=args.limit,
            )
        )
        action_taken = True

    if args.github_list_issues:
        _print_json(
            manager.list_github_issues(
                repository=args.github_repo,
                state=args.state,
                limit=args.limit,
            )
        )
        action_taken = True

    if args.github_create_issue:
        if not args.title:
            parser.error("--github-create-issue icin --title gerekli")
        labels = _parse_repositories(args.labels) if args.labels else []
        _print_json(
            manager.create_github_issue(
                args.title,
                args.body or "",
                repository=args.github_repo,
                labels=labels,
            )
        )
        action_taken = True

    if args.github_comment_pr:
        if not args.pull_number or not args.body:
            parser.error("--github-comment-pr icin --pull-number ve --body gerekli")
        _print_json(
            manager.comment_on_github_pull_request(
                args.pull_number,
                args.body,
                repository=args.github_repo,
            )
        )
        action_taken = True

    if args.configure_slack:
        if not args.webhook:
            parser.error("--configure-slack icin --webhook gerekli")
        success = manager.configure_slack(args.webhook, args.channel)
        _print_json({"action": "configure_slack", "success": success, "channel": args.channel})
        action_taken = True

    if args.configure_discord:
        if not args.webhook:
            parser.error("--configure-discord icin --webhook gerekli")
        success = manager.configure_discord(args.webhook)
        _print_json({"action": "configure_discord", "success": success})
        action_taken = True

    if args.add_custom_webhook:
        if not args.webhook or not args.events:
            parser.error("--add-custom-webhook icin --webhook ve --events gerekli")
        events = _parse_repositories(args.events)
        success = manager.add_custom_webhook(args.webhook, events, args.name)
        _print_json({"action": "add_custom_webhook", "success": success, "events": events})
        action_taken = True

    if args.setup:
        _print_json({
            "config_file": str(manager.config_file),
            "status": manager.get_integration_status(),
            "enabled_events": manager.config["notifications"]["enabled_events"]
        })
        action_taken = True

    if args.status:
        _print_json(manager.get_integration_status())
        action_taken = True

    if args.test_notifications:
        return _run_test_notifications(manager)

    if not action_taken:
        parser.print_help()

    return 0

if __name__ == "__main__":
    sys.exit(main())