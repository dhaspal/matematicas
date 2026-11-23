from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ejercicios, laboratorio, jefe

app = FastAPI(title="MathQuest API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
