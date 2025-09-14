from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES["default"].update({  # type: ignore[name-defined]
    "NAME": "ddt_dev",
    "USER": "postgres",
    "PASSWORD": "postgres",
    "HOST": "127.0.0.1",
})
