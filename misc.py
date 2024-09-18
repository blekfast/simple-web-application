import typing
import socket

def iter_lines(sock: socket.socket, buf_size: int = 16384) -> typing.Generator[bytes, None, bytes]:
    buff = b''
    while True:
        data = sock.recv(buf_size)
        if not data:
            return b''

        buff += data

        while True:
            try:
                i = buff.index(b"\r\n")
                line, buff = buff[:i], buff[i + 2:]

                if not line:
                    return buff

                yield line

            except IndexError:
                break
