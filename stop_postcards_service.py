import xmlrpc.client
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

HOST_IP = config.get('main', 'host')
HOST_PORT = config.get('main', 'port')

print(f'http://{HOST_IP}:{HOST_PORT}')


def run():
    server = xmlrpc.client.ServerProxy(f'http://{HOST_IP}:{HOST_PORT}')
    server.stop_service()


if __name__ == '__main__':
    run()
