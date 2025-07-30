import socket
import json
import time
from typing import Any

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 60080
DELIMITER = '\f'


def create_message(data: dict) -> str:
    return json.dumps({"type": "message", "data": data}) + DELIMITER


def parse_message(message: str) -> dict | None:
    try:
        return json.loads(message.strip()).get("data")
    except json.JSONDecodeError:
        return None


def call(name: str, args: list[str] = [], host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: float = 20.0) -> Any:
    """
    调用远程服务方法并返回结果。

    :param name: 方法名
    :param args: 参数列表
    :param host: 服务器地址，默认 127.0.0.1
    :param port: 端口号，默认 60080
    :param timeout: 超时时间（秒）
    :return: 返回的数据或 None
    """
    call_id = f"{int(time.time() * 1000)}_{name}"
    payload = {
        "type": "call",
        "id": call_id,
        "data": {
            "type": "serviceMethod",
            "name": name,
            "args": args
        }
    }

    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.sendall(create_message(payload).encode('utf-8'))

            buffer = ""
            while True:
                chunk = sock.recv(4096).decode('utf-8')
                if not chunk:
                    break
                buffer += chunk

                while DELIMITER in buffer:
                    part, buffer = buffer.split(DELIMITER, 1)
                    msg = parse_message(part)
                    if msg and msg.get("id") == call_id:
                        return msg.get("data")

        return None
    except (socket.timeout, socket.error, json.JSONDecodeError) as e:
        raise RuntimeError(f"Failed to call remote method '{name}': {e}")
