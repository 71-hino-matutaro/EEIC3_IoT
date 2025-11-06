#! /usr/bin/env python
# coding:utf-8
# tcp_server

import socket
import threading

#IPアドレスとポートを指定
bind_ip = '0.0.0.0'
bind_port = 10145

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
server.bind((bind_ip,bind_port))
server.listen(5)
print(f"[*] listen {bind_ip}:{bind_port}")

#
def handle_client(client_socket):
    bufsize=1024
    while True:
        request = client_socket.recv(bufsize)
        print(f"[*] recv: {request.decode('utf-8')}")
        client_socket.send('Received Message!\n'.encode('utf-8'))


while True:
    client,addr = server.accept()
    print(f"[*] connected from: {addr[0],addr[1]}")
    client_handler = threading.Thread(target=handle_client,args=(client,)) #スレッドを立てることで複数のクライアントからの接続に対応
    client_handler.start()