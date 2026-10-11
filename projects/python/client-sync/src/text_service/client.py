import argparse
import getpass
from typing import Any

import httpx


def exchange(
    client: httpx.Client, method: str, path: str, token: str = "", body: object = None
) -> tuple[int, Any]:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = client.request(method, path, json=body, headers=headers)
    try:
        result = response.json()
    except ValueError:
        result = {"message": response.text}
    return response.status_code, result


# 多行输入的结束标记：用户单独输入一行「.」表示输入结束。
# 正文里想表达一行「.」时，输入「..」（连续两个标记）来转义。
END_MARKER = "."


def build_text(lines: list[str]) -> str:
    """把按行读入的原始内容拼成最终文本。
    - 单独一行「.」是结束标记，它本身不进入正文（遇到就停止）；
    - 单独一行「..」表示正文里真的想要一行「.」（转义）；
    - 其余行原样保留，最后用换行符连接。
    这样空行、空文本、末尾换行、Unicode，以及「等于结束标记的那一行」都能表达。
    """
    result: list[str] = []
    for line in lines:
        if line == END_MARKER:
            break  # 结束
        if line == END_MARKER * 2:
            result.append(END_MARKER)  # 两个标记 = 正文里的一行「.」
        else:
            result.append(line)
    return "\n".join(result)  # 把拼接好的所有内容作为返回值返回


def read_multiline(prompt: str = "> ") -> str:
    """从终端循环读取多行，直到遇到单独一行的结束标记，再交给 build_text 解释。"""
    lines: list[str] = []
    while True:
        line = input(prompt)
        if line == END_MARKER:
            break  # 负责判断转义的结束，具体的转义解释交给 build_text
        lines.append(line)
    return build_text(lines)


def handle_token(command: str, status: int, result: Any, token: str) -> str:
    """根据「命令 + 响应状态」决定本地 token 该怎么更新，返回新的 token。

    - login 成功（200）：把响应里的新 token 存下来；
    - logout / delete-user 成功（200），或任何 401：清空本地 token；
    - 其他情况：token 保持不变。
    把这段逻辑抽成纯函数，是为了方便单测（见 tests 里的 handle_token 系列测试）。
    """
    if command == "login" and status == 200:
        return result["data"]["token"]
    if status == 401 or (command in ("logout", "delete-user") and status == 200):
        return ""
    return token


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:7878")
    args = parser.parse_args()
    token = ""
    with httpx.Client(
        base_url=args.url, timeout=12, follow_redirects=False, trust_env=False
    ) as client:
        try:
            while True:
                command = input(
                    "ping / register / login / logout / list / echo / "
                    "delete-user / put / get / delete / q > "
                ).strip()
                body = None
                if command == "q":
                    break
                if command in ("register", "login"):
                    body = {
                        "username": input("username: "),
                        "password": getpass.getpass("password: "),
                    }
                    method, path = "POST", "/users" if command == "register" else "/sessions"
                elif command in ("ping", "logout", "list"):
                    method, path = {
                        "ping": ("GET", "/ping"),
                        "logout": ("DELETE", "/sessions/current"),
                        "list": ("GET", "/texts"),
                    }[command]
                elif command == "echo":
                    # POST /echo：把输入放进 text 字段，服务端原样返回，无需登录。
                    method, path = "POST", "/echo"
                    print("逐行输入文本；单独一行「.」结束，单独一行「..」表示正文里的一个「.」。")
                    body = {"text": read_multiline()}
                elif command == "put":
                    # PUT /texts/{name}：上传或覆盖一篇文本，需要登录。
                    name = input("name: ")
                    print("逐行输入文本；单独一行「.」结束，单独一行「..」表示正文里的一个「.」。")
                    method, path = (
                        "PUT",
                        f"/texts/{name}",
                    )  # f"/texts/{name}" 里的 {name} 会被 Python 替换成 name 变量的值。
                    body = {"text": read_multiline()}
                elif command == "get":
                    # GET /texts/{name}：读取一篇文本，需要登录，无请求体。
                    name = input("name: ")
                    method, path = "GET", f"/texts/{name}"
                elif command == "delete":
                    # DELETE /texts/{name}：删除一篇文本，需要登录，无请求体。
                    name = input("name: ")
                    method, path = "DELETE", f"/texts/{name}"
                elif command == "delete-user":
                    # DELETE /users/me：注销当前账号，服务端会连同文本和令牌一起删除。
                    # 路径固定是 /users/me：删的是「谁」由令牌决定，不在路径里写名字。
                    method, path = "DELETE", "/users/me"
                else:
                    print("Unknown command.")
                    continue
                try:
                    # 只要你在 login 成功后，token 变量里有值，之后所有的 put/get 就会自动带上 Authorization: Bearer <token> 头。没登录就调用，token 是空字符串，不带认证头，服务端返回 401。
                    status, result = exchange(client, method, path, token, body)
                    print(status, result)
                    if status == 401:
                        print("Please log in again.")
                    token = handle_token(command, status, result, token)
                except (httpx.HTTPError, ValueError, KeyError) as exc:
                    print(f"Request failed: {exc}")
        except (EOFError, KeyboardInterrupt):
            print()
