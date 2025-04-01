from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router

app = FastAPI(
    title="DataStream Pro",
    description="Platform analitik inovatif untuk penelitian lingkungan",
    version="1.0.0"
)

# Konfigurasi CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Menambahkan router
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Selamat datang di DataStream Pro",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "data_collection": "operational",
            "analysis": "operational",
            "visualization": "operational"
        }
    } 