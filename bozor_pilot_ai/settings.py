import json
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CLAUDE_CONFIG_PATH = BASE_DIR / "config_claude.json"


def load_claude_config():
    if not CLAUDE_CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CLAUDE_CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


CLAUDE_CONFIG = load_claude_config()
CLAUDE_SETTINGS = CLAUDE_CONFIG.get("claude_settings", {}) if isinstance(CLAUDE_CONFIG, dict) else {}

SECRET_KEY = "django-insecure-bozor-pilot-ai-demo-key"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.core",
    "apps.accounts",
    "apps.consumer",
    "apps.business",
    "apps.analytics_app",
    "apps.integrations",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "bozor_pilot_ai.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.global_navigation",
            ],
        },
    }
]

WSGI_APPLICATION = "bozor_pilot_ai.wsgi.application"
ASGI_APPLICATION = "bozor_pilot_ai.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:router"
LOGOUT_REDIRECT_URL = "core:landing"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
SHOP_API_BASE_URL = os.getenv("SHOP_API_BASE_URL", "http://127.0.0.1:8001")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or CLAUDE_CONFIG.get("api_key", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL") or CLAUDE_SETTINGS.get("model", "claude-3-5-sonnet-latest")
ANTHROPIC_API_URL = CLAUDE_SETTINGS.get("api_url", "https://api.anthropic.com/v1/messages")
ANTHROPIC_API_VERSION = CLAUDE_SETTINGS.get("api_version", "2023-06-01")
ANTHROPIC_MAX_TOKENS = int(CLAUDE_SETTINGS.get("max_tokens", 300))
