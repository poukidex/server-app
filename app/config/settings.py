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
DEBUG = os.getenv("DJANGO_DEBUG", "").lower() == "true"

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
    "userauth",
    "index",
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

DJANGORESIZED_DEFAULT_SIZE = [200, 200]
DJANGORESIZED_DEFAULT_QUALITY = 75
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_FORCE_FORMAT = "PNG"
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {"PNG": ".png"}
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True

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
#                                        Logging
# ======================================================================================

LOGGING = DEFAULT_LOGGING
loglevel = os.getenv("LOGLEVEL", "INFO")
debug_loggers = os.getenv("DEBUG_LOGGERS", "")
handlers_loglevel = loglevel if not debug_loggers else "DEBUG"

# Adding simple formatter
LOGGING["formatters"]["index"] = {
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

# Adding console handler for index
LOGGING["handlers"]["index"] = {
    "level": handlers_loglevel,
    "class": "logging.StreamHandler",
    "formatter": "index",
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

# Set index loggers like django ones
LOGGING["loggers"]["index"] = {
    "handlers": ["index"],
    "level": loglevel,
}

# Set specified loggers to DEBUG level
for logger in debug_loggers.split(",") if debug_loggers else []:
    if logger not in LOGGING["loggers"]:
        if logger.startswith("django.") or logger.startswith("index."):
            LOGGING["loggers"][logger] = {}
        else:
            LOGGING["loggers"][logger] = {
                "handlers": ["console", "console_debug_false"],
                "propagate": False,
            }
    LOGGING["loggers"][logger]["level"] = "DEBUG"

JWT_KEY = os.getenv("JWT_KEY")
if JWT_KEY is None:
    raise Exception("JWT_KEY shall be configured")

JWT_EXPIRES_IN = os.getenv("JWT_EXPIRES_IN")
if JWT_EXPIRES_IN is None:
    JWT_EXPIRES_IN = 3600

S3_ENV = os.getenv("S3_ENV", "mock")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")

CREATION_TOKEN_PASSWORD = os.getenv("CREATION_TOKEN_PASSWORD")
if CREATION_TOKEN_PASSWORD is None:
    raise Exception("CREATION_TOKEN_PASSWORD shall be configured")
