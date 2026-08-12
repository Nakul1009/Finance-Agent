import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi import Request

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api import health, documents, transactions, analytics, chat, reports, agent
from app.models.models import Document, Transaction
from app.sample_data.demo_generator import generate_synthetic_transactions
from app.categorization.rules import CategorizationRulesEngine
from app.categorization.merchant_normalizer import MerchantNormalizer

# Create DB tables if not existing
Base.metadata.create_all(bind=engine, checkfirst=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Professional Financial Document Intelligence Agent powered by Hybrid Rules & NVIDIA Nemotron LLM."
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred while processing your request.", "error": str(exc)}
    )

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router, prefix=settings.API_PREFIX, tags=["Health"])
app.include_router(documents.router, prefix=f"{settings.API_PREFIX}/documents", tags=["Documents"])
app.include_router(transactions.router, prefix=f"{settings.API_PREFIX}/transactions", tags=["Transactions"])
app.include_router(analytics.router, prefix=f"{settings.API_PREFIX}/analytics", tags=["Analytics"])
app.include_router(chat.router, prefix=f"{settings.API_PREFIX}/chat", tags=["AI Assistant"])
app.include_router(reports.router, prefix=f"{settings.API_PREFIX}/reports", tags=["Reports"])
app.include_router(agent.router, prefix=f"{settings.API_PREFIX}/agent", tags=["AI Agent Console"])


# Static files mounting for built frontend (HF Spaces)
frontend_static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(frontend_static_dir):
    assets_dir = os.path.join(frontend_static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api"):
            return None
        file_p = os.path.join(frontend_static_dir, full_path)
        if os.path.exists(file_p) and os.path.isfile(file_p):
            return FileResponse(file_p)
        return FileResponse(os.path.join(frontend_static_dir, "index.html"))

