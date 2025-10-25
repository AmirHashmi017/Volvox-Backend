from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, researchWork

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Volvox Backend API with Authentication"
)

# CORS: If using credentials with wildcard origins, browsers block the response.
# To support any origin while using credentials (cookies, auth), use a regex
# that echoes back the request origin instead of '*'.
_allow_origins = [o for o in settings.ALLOWED_ORIGINS if o != "*"]
_allow_origin_regex = ".*" if ("*" in settings.ALLOWED_ORIGINS) else None

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_origin_regex=_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(researchWork.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Volvox Backend API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}
