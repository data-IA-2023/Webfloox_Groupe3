


from fastapi import FastAPI,Request,Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates




      


app = FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static")
templates = Jinja2Templates(directory="templates")

"""

@app.get("/")
def root(x: int = 10):
    return {"msg": f"Hello World ,x={x}"}



@app.get("/test/{value}")
def get_test(value:str):
    return {"msg_test": f"Test value={value}"}



taches = [{"id": 0, "titre": "Acheter du lait"}, {"id": 1, "titre": "Réviser FastAPI"}]



@app.get("/page")
def liste(request:Request):
    return templates.TemplateResponse(
        request=request, name="page.html",context={"taches":taches,"tache":"rien"})



@app.post("/page")
def submit_form(request:Request,id: int = Form(), titre: str = Form()):
    taches.append({"id":id,"titre":titre})
    return templates.TemplateResponse(
        request=request, name="page.html",context={"taches":taches})



@app.get("/page2")
def recherche_form(request: Request, id: int):
    return templates.TemplateResponse(
        request=request, name="page.html",context={"tache":taches[id]["titre"],"taches":taches })


"""















"""
@app.post("/page")
def submit_form(request: Request, id: int = Form(...), titre: str = Form(...)):
    taches.append({"id": id, "titre": titre})
    return templates.TemplateResponse(
        "page.html",
        {"request": request, "taches": taches}
    )
"""
"""
@app.post("/page/{id}/{titre}")
def updateliste(request:Request,id:int,titre:str):
    
    taches.append({"id":id,"titre":titre})
    return taches

"""