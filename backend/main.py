from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router


app = FastAPI(
    title="AZ Turf Pro API",
    version="1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)




@app.get("/")
def accueil():
    return {
        "message": "AZ Turf Pro API en ligne",
        "status": "OK"
    }


@app.get("/health")
def health():
    return {
        "service": "AZ Turf Pro",
        "status": "running"
    }
