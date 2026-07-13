import os
from slowapi import Limiter
from slowapi.util import get_remote_address

# Detecta se estamos rodando na suíte de testes unitários ou integração
is_testing = os.getenv("TESTING", "False") == "True"


if is_testing:
    storage_uri = "memory://"
else:
    # Dentro da rede do Docker Compose, o hostname do Redis é 'redis'
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")
    storage_uri = f"redis://{REDIS_HOST}:{REDIS_PORT}"

# Instanciação do limitador global
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=storage_uri,
    storage_options={"socket_connect_timeout": 3},
    enabled=not is_testing
)

