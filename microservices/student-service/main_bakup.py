import json
import uvicorn
from fastapi import FastAPI, APIRouter
from time import sleep
import logging

from config import Config
from consul_client import ConsulClient
from utils import register_to_consul
import typer

# from register_service import register as register_to_consul

configuration = Config()

shell_app = typer.Typer()

router = APIRouter()

# app = create_app()
app = FastAPI(title="student-service")

fake_dbs = [
    {'name': 'Bilal', 'class': 'V', 'school_id': 1},
    {'name': 'Ganta', 'class': 'IX', 'school_id': 1},
    {'name': 'Azril', 'class': 'IV', 'school_id': 2}
]


@router.on_event("startup")
def startup_event():
    # register_to_consul()
    register_to_consul()


@router.get("/")
async def list_students():
    return fake_dbs


@router.get("/health")
async def health_status():
    return {"status": "healthy"}


@router.get("/register-service")
async def register():
    # return register_to_consul()
    register_to_consul()


@router.get("/name/{name}")
async def get_student(name: str):
    return filter(lambda x: x.get('name') == name, fake_dbs)


@router.get("/school/{school_id}")
async def filter_student_by_school(school_id: int):
    return filter(lambda x: x.get("school_id") == school_id, fake_dbs)


class HttpServer:
    # 新建服务时，需要指定consul服务的 主机，端口，所启动的 服务的 主机 端口 以及 restful http 服务 类
    def __init__(self, host, port, consulhost, consulport, app_name):
        self.port = port
        self.host = host
        # self.app = appClass(host=host, port=port)
        # self.appname = self.app.appname
        self.appname = app_name
        self.consulhost = consulhost
        self.consulport = consulport

    def startServer(self):
        client = ConsulClient(host=self.consulhost, port=self.consulport)
        service_id = self.appname + self.host + ':' + str(self.port)
        httpcheck = 'http://' + self.host + ':' + str(self.port) + '/check'
        client.register(self.appname, service_id=service_id, address=self.host, port=self.port, tags=['master'],
                        interval='30s', httpcheck=httpcheck)  # 注册服务
        # self.app.run()  # 启动服务
        uvicorn.run(app=app, host=self.host, port=self.port)


app.include_router(router)

if __name__ == '__main__':
    server = HttpServer('127.0.0.3', 8000, '127.0.0.1', 8500, 'student-service')
    server.startServer()
