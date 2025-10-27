from fastapi import FastAPI
from app.api.v1.routes import portfolios, simulations, taxlots
from app.database.connection import engine
from app.database.models import portfolio, tax_lot, price

app = FastAPI(title="Position Tracker API - Local Prototype")

# This function will create the database tables on startup
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        # Use this for local dev to create tables. For production, use Alembic.
        await conn.run_sync(portfolio.Base.metadata.create_all)
        await conn.run_sync(tax_lot.Base.metadata.create_all)
        await conn.run_sync(price.Base.metadata.create_all)

# Your existing portfolio router
app.include_router(portfolios.router, prefix="/api/v1/portfolios", tags=["Portfolios"])

# Add the new simulation router
app.include_router(simulations.router, prefix="/api/v1/simulate", tags=["Simulations (Local Only)"])
app.include_router(taxlots.router, prefix="/api/v1/taxlots", tags=["Tax Lots"])

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "service": "Position Tracker API"}

@app.get("/health", tags=["Health Check"])
async def health_check():
    """Health check endpoint for Docker and load balancers"""
    try:
        # Test database connection
        async with engine.begin() as conn:
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "service": "Position Tracker API",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Position Tracker API",
            "database": "disconnected",
            "error": str(e)
        }