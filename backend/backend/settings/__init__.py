import os

environment = os.environ.get("DJANGO_ENV", "dev")


if environment == "prod":
    from .prod import *
elif environment == "dev":
    from .dev import *

    print("os.environ", f"[{environment}]", os.environ)
else:
    raise ValueError(f"Invalid environment: {environment}")
