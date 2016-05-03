DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
SECRET_KEY = "secret_key_for_testing"
INSTALLED_APPS = ['django.contrib.sessions', 'django_zappa']
MIDDLEWARE_CLASSES = ['django.contrib.sessions.middleware.SessionMiddleware']
ROOT_URLCONF = 'django_zappa.urls'
TIME_ZONE = 'UTC'
ALLOWED_HOSTS = ["*"]
DEBUG = True
AUTH_USER_MODEL = None
SCRIPT_NAME = '/test'

ZAPPA_SETTINGS = {
    'test': {
        's3_bucket': 'zappa-test-bucket',
        'settings_file': 'test_settings.py'
    },
    's3': {
        's3_bucket': 'zappa-test-bucket',
        'settings_file': 's3://zappa-test-bucket:test_settings.py'
    }
}
BASE_DIR = ''
LETS_ENCRYPT_CHALLENGE_PATH = 'KkI_AMwzmQxlMDtaitt7eZMWEDn0t0Fsl5HjkJSPxyz'
LETS_ENCRYPT_CHALLENGE_CONTENT = "KkI_AMwzmQxlMDtaitt7eZMWEDn0t0Fsl5HjkJSPxyz.ABC5hET2fxMsBLCsQLlAVA5MLvYUna8gEAYaXN0xI4Y"
