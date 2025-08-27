import os

environment = os.environ.get("DJANGO_ENV", "dev")

print("os.environ", f"[{environment}]", os.environ)

if environment == "prod":
    from .prod import *
elif environment == "dev":
    from .dev import *
else:
    raise ValueError(f"Invalid environment: {environment}")
