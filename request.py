import typing
import socket

from misc import iter_lines


class Request(typing.NamedTuple):
    method: str
    path: str
    headers: typing.Mapping[str, str]

    @classmethod
    def from_socket(cls, sock: socket.socket) -> "Request":

       lines = iter_lines(sock=sock)

       try:
           request_line = next(lines).decode("ascii")
       except StopIteration:
           raise ValueError("Request line is missing")

       try:
           method, patch, _ = request_line.split(' ')
       except ValueError:
           raise ValueError(f'Malformed request line {request_line!r}')

       headers = {}
       for line in lines:
            try:
                name, _, value = line.decode('ascii').partition(":")
                headers[name.lower()] = value.lstrip()
            except ValueError:
                raise ValueError(f'Malformed header line {request_line!r}')

       return cls(method.upper(), path=patch, headers=headers)