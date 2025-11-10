from http import HTTPStatus

from fastapi import FastAPI

from app.routers.auth import auth
from app.routers.users import users
from app.schemas import Message

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def root():
    return {'message': 'Service online!'}
