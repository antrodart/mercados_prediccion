ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'predictmarket',
        'USER': 'predictmarket',
	    'PASSWORD': 'predictmarket',
        'HOST': 'predictmarket',
        'PORT': '5432',
    }
}

# number of bits for the key, all auths should use the same number of bits
KEYBITS = 256