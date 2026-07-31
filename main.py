from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def accueil(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.get("/bonjour")
def bonjour():
    print("Bonjour Mattéo ! Bienvenue sur ton premier site Python.")
    return {
        "message": "Bonjour Mattéo ! Bienvenue sur ton premier site Python."
    }

@app.get("/test")
def test():
    print("Ceci est un test.")
    return {
        "message": "Ceci est un test."
    }
   