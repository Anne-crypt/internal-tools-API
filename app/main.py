from fastapi import FastAPI
from app.api.v1.endpoints import tool

app = FastAPI(
    title="SaaS Tools Management API",
    description="API de gestion et d'optimisation des coûts des outils SaaS",
    version="1.0.0"
)

# Inclusion des routes avec le préfixe demandé /api/tools
app.include_router(tool.router, prefix="/api/tools", tags=["Tools"])

@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Welcome to SaaS Tools Management API"}