from fastapi import FastAPI, Request

app = FastAPI()
@app.get("/")
def get_root(request: Request):
    return {'m':{ 'msg1' : "Hello, world"},'k':{ 'msg2' : "Hello, world"}}
