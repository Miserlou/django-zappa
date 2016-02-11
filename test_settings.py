DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
SECRET_KEY = "secret_key_for_testing"
INSTALLED_APPS = ['django.contrib.sessions', 'django_zappa']
MIDDLEWARE_CLASSES = ['django.contrib.sessions.middleware.SessionMiddleware', 'django_zappa.middleware.ZappaMiddleware']
ROOT_URLCONF = 'django_zappa.urls'
TIME_ZONE = 'UTC'
ALLOWED_HOSTS = ["*"]
DEBUG = True
AUTH_USER_MODEL = None
SCRIPT_NAME = '/test'

LETS_ENCRYPT_CHALLENGE_PATH = 'KkI_AMwzmQxlMDtaitt7eZMWEDn0t0Fsl5HjkJSPxyz'
LETS_ENCRYPT_CHALLENGE_CONTENT = "KkI_AMwzmQxlMDtaitt7eZMWEDn0t0Fsl5HjkJSPxyz.ABC5hET2fxMsBLCsQLlAVA5MLvYUna8gEAYaXN0xI4Y"