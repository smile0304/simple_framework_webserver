#coding:utf-8

import socket
import re
import sys


from multiprocessing import Process

# 设置静态文件跟目录
HTML_ROOT_DIR = "./html"
WSGI_PYTHON_DIR = "./wsgipython"
class HTTPServer(object):
    """"""
    def __init__(self,application):
        """构造函数,application指的是框架的app"""
        self.app = application
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def bind(self, port):
        self.server_socket.bind(("", port))

    def start(self):
        self.server_socket.listen(128)
        while True:
            client_socket, client_address = self.server_socket.accept()
            print("[%s:%s]用户连接上了" % client_address)
            handle_client_process = Process(target=self.handle_client, args=(client_socket,))
            handle_client_process.start()
            client_socket.close()

    def start_response(self,status,headers):
        server_headers = [
            ("Server" , "TT_Server")
        ]
        response_headers = "HTTP/1.1 " + status + "\r\n"
        for header in headers:
            response_headers += "%s: %s\r\n" % header
        self.response_headers = response_headers

    def handle_client(self,client_socket):
        """处理客户端请求"""
        # 获取客户端请求数据
        request_data = client_socket.recv(1024)
        #print("request_data:", request_data)
        request_lines = request_data.splitlines()
        for line in request_lines:
            #print(line)
            pass
        # 解析请求报文
        # GET /favicon.ico HTTP/1.1
        request_start_line = request_lines[0]
        print("request:%s" % request_start_line.decode("utf-8"))
        # 提取用户请求的文件
        file_name = re.match(r"\w+ +(/[^ ]*) ", request_start_line.decode("utf-8")).group(1)
        method = re.match(r"(\w+) +(/[^ ]*) ", request_start_line.decode("utf-8")).group(1)

        env = {
            "PATH_INFO" : file_name,
            "METHOD" : method
        }
        response_body = self.app(env,self.start_response)
        print("*****************************************************")
        print(response_body)
        response = self.response_headers + "\r\n" + response_body
        print(response)

        # 向客户端返回响应数据
        client_socket.send(bytes(response, "utf-8"))

        # 关闭客户端链接
        client_socket.close()

def main():
    sys.path.insert(1,WSGI_PYTHON_DIR)
    if len(sys.argv) < 2:
        sys.exit("python WebServer.py Moudle:app")
    #python WebServer.py TT_Framework:app
    module_name,app_name = sys.argv[1].split(":")
    #module_name = "TT_Framework"
    #app_name = "app"
    m = __import__(module_name)
    app = getattr(m,app_name)
    http_server = HTTPServer(app)
    http_server.bind(8000)
    http_server.start()


if __name__ =="__main__":
    main()
