from time import sleep
from config import Config
import consul


configuration = Config()

def register():
    # TODO:[*] 23-11-02 此处心跳检测不成功，怀疑是 url 地址错误引起的

    check_http = consul.Check.http(
        'http://student_service:8000/health', interval='10s'
    )
    client = consul.Consul(
        host=configuration.CONSUL_HOST, port=configuration.CONSUL_PORT
    )

    while True:
        try:
            client.agent.service.register(
                'student', address='student', port=8000, check=check_http
            )
            break
        except consul.ConsulException:
            print("Retrying to connect to consul ...")
            sleep(0.5)

