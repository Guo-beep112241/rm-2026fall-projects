#启动入口
import argparse

import uvicorn
from fastapi import FastAPI

from . import _http
from .service import Service

#用来组装app的函数
def create_app(service: Service | None = None) -> FastAPI:
    # Pass a configured Service here when adding business settings such as token TTL.
    return _http.create_app(Service() if service is None else service)


def main() -> None:
    parser = argparse.ArgumentParser()
    #解析命令行参数（--host、--port）
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7878)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be 1..65535")
    #启动服务器
    uvicorn.run(create_app(), host=args.host, port=args.port, workers=1, access_log=False)
