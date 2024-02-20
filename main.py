from fastapi import FastAPI, Request

app = FastAPI()
@app.get("/")
def get_root(request: Request):
    return { 'msg' : "Hello, world"}
