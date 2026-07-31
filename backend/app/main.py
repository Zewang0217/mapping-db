from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import sources, categories, mappings, dim_values, stats, export
from app.seed import seed_dimension_values


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_dimension_values()
    yield


app = FastAPI(title="Mapping DB", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sources.router, prefix="/api/sources", tags=["sources"])
app.include_router(categories.router, prefix="/api", tags=["categories"])
app.include_router(mappings.router, prefix="/api", tags=["mappings"])
app.include_router(dim_values.router, prefix="/api/dim-values", tags=["dim-values"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
