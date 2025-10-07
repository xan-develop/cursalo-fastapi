from fastapi import FastAPI 
from contextlib import asynccontextmanager
from db import client
from config.consolelog import logger
from routes.auth_routes import router as auth_router
from models import rebuild_models
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicación nuevo logger")
    await client.init()
    yield
    # Cerrar conexiones u otros recursos si es necesario

app = FastAPI(lifespan=lifespan)
# Reconstruir modelos al iniciar la aplicación
rebuild_models()
app.include_router(auth_router)

@app.get("/")
async def root():
    logger.debug("Root endpoint called")
    return {"message": "Hello World"}