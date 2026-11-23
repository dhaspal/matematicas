import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ejercicios, laboratorio, jefe

app = FastAPI(title="MathQuest API", version="1.0.0")

frontend_urls = os.getenv("FRONTEND_URL", "")
allowed_origins = ["http://localhost:5173"]
if frontend_urls:
    allowed_origins.extend(
        url.strip().rstrip("/") for url in frontend_urls.split(",") if url.strip()
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ejercicios.router)
app.include_router(laboratorio.router)
app.include_router(jefe.router)


@app.get("/api/salud")
def salud():
    return {"estado": "ok", "mensaje": "MathQuest está listo"}
