import mimetypes
import os
import socket
from http.client import responses
from operator import index
from os.path import abspath

from request import Request
from constants import RESPONSE, NOT_FOUND_RESPONSE, BAD_REQUEST_RESPONSE, FILE_RESPONSE_TEMPLATE, \
    METHOD_NOT_ALLOWED_RESPONSE

HOST = "127.0.0.1"
PORT = 9000

SERVER_ROOT = os.path.abspath("www")


def serve_file(sock: socket.socket, path: str) -> None:
    print(f'Serve File')
    if path == '/':
        path = '/index.html'

    abspath = os.path.normpath(os.path.join(SERVER_ROOT, path.lstrip("/")))
    if not abspath:
        sock.sendall(NOT_FOUND_RESPONSE)
        return

    print(abspath)

    try:
        with open(abspath, "rb") as f:
            stat = os.fstat(f.fileno())
            content_type, encoding = mimetypes.guess_type(abspath)

            if content_type is None:
                content_type = 'application/octet-stream'

            if encoding is not None:
                content_type += f"; charset={encoding}"

            response_headers = FILE_RESPONSE_TEMPLATE.format(content_type=content_type, content_length=stat.st_size).encode('ascii')

            sock.sendall(response_headers)
            sock.sendfile(f)

    except FileNotFoundError:
        sock.sendall(NOT_FOUND_RESPONSE)
        return

with socket.socket() as server_sock:

    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(0)

    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_sock, client_addr = server_sock.accept()
        print(f"New connection from client: {client_addr}")

        with client_sock:
            try:
                request = Request.from_socket(client_sock)
                if request.method != 'GET':
                    client_sock.sendall(METHOD_NOT_ALLOWED_RESPONSE)
                    continue
                print(f'Request Path {request.path}')
                serve_file(client_sock, request.path)

            except Exception as e:
                print(f'Failed to parse request: {e}')
                client_sock.sendall(BAD_REQUEST_RESPONSE)
