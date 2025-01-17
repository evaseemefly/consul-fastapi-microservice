# coding=utf-8
# from consulate import Consul
import consul
from random import randint
import requests
import json


# TODO:[*] 23-11-01 参考文章
# https://gitee.com/aichinai/consul_flask/blob/master/ConsulFlask/consulclient.py

# consul 操作类
class ConsulClient:
    def __init__(self, host=None, port=None, token=None):  # 初始化，指定consul主机，端口，和token

        self.host = host  # consul 主机
        self.port = port  # consul 端口
        self.token = token
        self.consul = consul.Consul(host=host, port=port)

    def register(self, name, service_id, address, port, tags, interval, httpcheck):
        # 注册服务 注册服务的服务名  端口  以及 健康监测端口
        self.consul.agent.service.register(name, service_id=service_id, address=address, port=port, tags=tags,
                                           interval=interval, check=httpcheck)
        pass

    def getService(self, name):  # 负载均衡获取服务实例
        # client: 'http://127.5.9.79:8500/v1/catalog/service/student-service'

        # 尝试通过
        # self.consul.agent.services()
        # {ConnectionError}HTTPConnectionPool(host='127.5.9.79', port=8500): Max retries exceeded with url: /v1/agent/services (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001A9CD73BE48>: Failed to establish a new connection: [WinError 10061] 由于目标计算机积极拒绝，无法连接。'))
        url = 'http://' + self.host + ':' + str(self.port) + '/v1/catalog/service/' + name  # 获取 相应服务下的DataCenter

        requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数

        req = requests.session()
        req.keep_alive = False  # 关闭多余连接

        dataCenterResp = req.get(url)
        if dataCenterResp.status_code != 200:
            raise Exception('连接 consul 错误')
        listData = json.loads(dataCenterResp.text)
        dcset = set()  # DataCenter 集合 初始化
        for service in listData:
            dcset.add(service.get('Datacenter'))
        serviceList = []  # 服务列表 初始化
        for dc in dcset:
            if self.token:
                url = 'http://' + self.host + ':' + self.port + '/v1/health/service/' + name + '?dc=' + dc + '&token=' + self.token
            else:
                url = 'http://' + self.host + ':' + self.port + '/v1/health/service/' + name + '?dc=' + dc + '&token='
            resp = requests.get(url)
            if resp.status_code != 200:
                raise Exception('连接 consul 错误 ')
            text = resp.text
            serviceListData = json.loads(text)

            for serv in serviceListData:
                status = serv.get('Checks')[1].get('Status')
                if status == 'passing':  # 选取成功的节点
                    address = serv.get('Service').get('Address')
                    port = serv.get('Service').get('Port')
                    serviceList.append({'port': port, 'address': address})

        print("成功节点服务列表：", serviceList)
        if len(serviceList) == 0:
            raise Exception('没有服务可用')
            # print("没有服务可用")
        else:
            service = serviceList[randint(0, len(serviceList) - 1)]  # 随机获取一个可用的服务实例
            print("返回随机选取的节点", service['address'], int(service['port']))
            # return service['address'],int(service['port'])
            return service['address'], service['port']
