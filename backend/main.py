from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api import router


app = FastAPI(
    title="AZ Turf Pro API",
    version="1.0"
)


app.include_router(router)


app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)


@app.get("/")
def accueil():
    return FileResponse("frontend/index.html")
