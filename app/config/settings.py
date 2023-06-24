import os
from pathlib import Path

from django.utils.log import DEFAULT_LOGGING

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"

allowed_hosts_env = os.getenv("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = allowed_hosts_env.split(",") if allowed_hosts_env else []

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "userauth",
    "core",
    "collections",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

cors_allowed_origins = os.getenv("DJANGO_CORS_ALLOWED_ORIGINS")
CORS_ALLOWED_ORIGINS = cors_allowed_origins.split(",") if cors_allowed_origins else []

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_USER_MODEL = "userauth.User"

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}
if os.getenv("DB_SSL", "false").lower() == "true":
    DATABASES["default"]["OPTIONS"] = {
        "sslmode": "verify-full",
        "sslrootcert": os.getenv("DB_CA_CERT_PATH"),
    }
CONN_MAX_AGE = 60

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ======================================================================================
# Redis
# ======================================================================================
REDIS_URL = os.getenv("REDIS_URL")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# ======================================================================================
# Email
# ======================================================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

# ======================================================================================
# Logging
# ======================================================================================

LOGGING = DEFAULT_LOGGING
loglevel = os.getenv("LOGLEVEL", "INFO")
debug_loggers = os.getenv("DEBUG_LOGGERS", "")
handlers_loglevel = loglevel if not debug_loggers else "DEBUG"

# Adding simple formatter
LOGGING["formatters"]["poukidex"] = {
    "format": "{asctime} [{name}] {levelname}: {message}",
    "style": "{",
}

# Setting default console log level by env variable
LOGGING["handlers"]["console"]["level"] = handlers_loglevel

# Adding console handler when debug is false
LOGGING["handlers"]["console_debug_false"] = {
    "level": handlers_loglevel,
    "filters": ["require_debug_false"],
    "class": "logging.StreamHandler",
}

# Adding console handler for poukidex
LOGGING["handlers"]["poukidex"] = {
    "level": handlers_loglevel,
    "class": "logging.StreamHandler",
    "formatter": "poukidex",
}

# Setting default logger log level by env variable
LOGGING["loggers"]["django"]["level"] = loglevel

# Make logger always log on console
LOGGING["loggers"]["django"]["handlers"] = ["console", "console_debug_false"]

# Override template logger so that it stops logging stacktrace on debug
LOGGING["loggers"]["django.template"] = {
    "handlers": ["console", "console_debug_false"],
    "level": loglevel if loglevel != "DEBUG" else "INFO",
}

# Set poukidex loggers like django ones
LOGGING["loggers"]["poukidex"] = {
    "handlers": ["poukidex"],
    "level": loglevel,
}

# Set specified loggers to DEBUG level
for logger in debug_loggers.split(",") if debug_loggers else []:
    if logger not in LOGGING["loggers"]:
        if logger.startswith("django.") or logger.startswith("poukidex."):
            LOGGING["loggers"][logger] = {}
        else:
            LOGGING["loggers"][logger] = {
                "handlers": ["console", "console_debug_false"],
                "propagate": False,
            }
    LOGGING["loggers"][logger]["level"] = "DEBUG"

# ======================================================================================
# JWT
# ======================================================================================

JWT_KEY = os.getenv("JWT_KEY")
if JWT_KEY is None:
    raise Exception("JWT_KEY shall be configured")

JWT_EXPIRES_IN = os.getenv("JWT_EXPIRES_IN")
if JWT_EXPIRES_IN is None:
    JWT_EXPIRES_IN = 3600

# ======================================================================================
# S3
# ======================================================================================

S3_ENV = os.getenv("S3_ENV", "mock")
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
GCP_SECRETS_PATH = os.getenv("GCP_SECRETS_PATH")

CREATION_TOKEN_PASSWORD = os.getenv("CREATION_TOKEN_PASSWORD")
if CREATION_TOKEN_PASSWORD is None:
    raise Exception("CREATION_TOKEN_PASSWORD shall be configured")
