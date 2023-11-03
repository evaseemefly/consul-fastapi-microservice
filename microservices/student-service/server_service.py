import json
import uvicorn
from fastapi import FastAPI, APIRouter
from time import sleep
import logging

import consul
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
    """
        将向 consul 注册服务添加至 fastapi 的 startup 事件中
        本 fastapi 启动时向 consul 注册服务
    :return:
    """
    # register_to_consul()
    # register_to_consul()
    server = ConsulRegisterServer('127.0.0.1', 8000, '128.5.9.79', 8500, 'student-service')
    server.register()
    pass


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


class ConsulRegisterServer:
    """
        与 start_up 事件绑定并触发实现注册服务
    """

    # 新建服务时，需要指定consul服务的 主机，端口，所启动的 服务的 主机 端口 以及 restful http 服务 类
    def __init__(self, service_host, service_port, consul_host, consul_port, app_name):
        """

        :param service_host: 127.0.0.1  当前服务的实际ip地址
        :param service_port: 8000
        :param consul_host: 128.5.9.79   consul 地址
        :param consul_port: 8500
        :param app_name: 注册的服务名称
        """
        self.service_port = service_port
        self.service_host = service_host
        # self.app = appClass(host=host, port=port)
        # self.appname = self.app.appname
        self.app_name = app_name
        self.consul_host = consul_host
        self.consul_port = consul_port

    def register(self):
        """
            基于 self.service_host:self.service_port 注册至 self.consul_host:self.consul_port

        :return:
        """
        client = ConsulClient(host=self.consul_host, port=self.consul_port)
        service_id = self.app_name + self.service_host + ':' + str(self.service_port)
        # 暂时不用
        httpcheck = 'http://' + self.service_host + ':' + str(self.service_port) + '/check'
        # TODO:[*] 23-11-02 注意此处的 check 有错误，无法实现心跳检测
        # 注意心跳检测 check 的 host 应为 consul 的地址，改为consul的地址
        client.register(self.app_name, service_id=service_id, address=self.service_host, port=self.service_port,
                        tags=['master'],
                        interval='30s',
                        httpcheck=consul.Check().tcp(self.consul_host, self.consul_port, '5s', '30s', '30s'))  # 注册服务
        # self.app.run()  # 启动服务
        # uvicorn.run(app=app, host=self.host, port=self.port)


app.include_router(router)
