from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from src.infrastructure.web.limiter import limiter
from src.infrastructure.web.auth import router as auth_router
from src.infrastructure.web.lojas import router as lojas_router
from src.infrastructure.web.produtos import router as produtos_router
from src.infrastructure.web.clientes import router as clientes_router
from src.infrastructure.web.fornecedores import router as fornecedores_router
from src.infrastructure.web.estoque import router as estoque_router

app = FastAPI(
    title="Gerenciador de Lojas SaaS - API",
    description="API de retaguarda multi-tenant para gerenciamento de lojas e estoque.",
    version="1.0.0",
)

# Configura o limiter na instância da aplicação
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Registra os roteadores da aplicação
app.include_router(auth_router)
app.include_router(lojas_router)
app.include_router(produtos_router)
app.include_router(clientes_router)
app.include_router(fornecedores_router)
app.include_router(estoque_router)


# Configuração de CORS (ajustar para produção posteriormente)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Monitoramento"])
def health_check() -> dict[str, str]:
    """
    Endpoint simples de monitoramento para verificar se a API está online.
    """
    return {
        "status": "healthy",
        "message": "Gerenciador de Lojas SaaS API operacional"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
