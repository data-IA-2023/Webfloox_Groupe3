# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 10:16:34 2024

@author: naouf
"""

from fastapi import fastapi, Request
app = fastapi()
@app.get("/")
def get_root(request:Request):
    return{"msg":"Hello world"}
