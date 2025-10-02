from fastapi import FastAPI
from http import HTTPStatus
from app.schemas import Message

app = FastAPI()


@app.get('/', status_code= HTTPStatus.OK, response_model= Message )
def root():
    return {'message': 'Hello World'}


@app.post('/Creat')
def creat():
    return{ 'message': 'Create funcionario'}