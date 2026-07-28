from pathlib import Path
import os

# -----------------------------------------
# Base Directory
# -----------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------
# Security Settings
# -----------------------------------------
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-b(gb5d$4f2o*i*_1a+c4#_(#v%9at(7()r#m+s4x3y0npmbf$h'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    'farmease-env.eba-i4ddempf.us-east-1.elasticbeanstalk.com',
    '2fa585ea017c4fb39d37df0427b9400d.vfs.cloud9.us-east-1.amazonaws.com',
    'localhost',
    '127.0.0.1'
]  # Allow all for now (Elastic Beanstalk will assign a domain)
CSRF_TRUSTED_ORIGINS = [
    'https://*.elasticbeanstalk.com',
    'http://farmease-env.eba-i4ddempf.us-east-1.elasticbeanstalk.com',
    'https://2fa585ea017c4fb39d37df0427b9400d.vfs.cloud9.us-east-1.amazonaws.com'
]

# -----------------------------------------
# Installed Apps
# -----------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
]

# -----------------------------------------
# Middleware
# -----------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'farmease.urls'

# -----------------------------------------
# Templates
# -----------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Global templates folder (optional)
        ],
        'APP_DIRS': True,  # Looks inside each app's "templates" folder
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Required for "request" in templates
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'farmease.wsgi.application'

# -----------------------------------------
# Database (SQLite by default)
# -----------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Optional: You can later switch to RDS (PostgreSQL) by uncommenting below:
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('RDS_DB_NAME', ''),
        'USER': os.environ.get('RDS_USERNAME', ''),
        'PASSWORD': os.environ.get('RDS_PASSWORD', ''),
        'HOST': os.environ.get('RDS_HOSTNAME', ''),
        'PORT': os.environ.get('RDS_PORT', '5432'),
    }
}
"""

# -----------------------------------------
# Password Validation
# -----------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -----------------------------------------
# Internationalization
# -----------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -----------------------------------------
# Static & Media Files
# -----------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]  # Local static folder
STATIC_ROOT = BASE_DIR / "staticfiles"    # For production (Elastic Beanstalk)

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -----------------------------------------
# Default Primary Key
# -----------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AWS_REGION = "us-east-1"
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:028971169403:farmease-crop-updates"

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False