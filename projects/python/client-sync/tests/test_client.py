import json

import httpx

from text_service.client import build_text, exchange, handle_token


def test_request() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/texts"
        assert request.headers["Authorization"] == "Bearer example"
        return httpx.Response(200, json={"data": []})

    with httpx.Client(
        base_url="http://localhost", transport=httpx.MockTransport(respond)
    ) as client:
        assert exchange(client, "GET", "/texts", "example") == (200, {"data": []})


def test_build_text_basic() -> None:
    assert build_text(["hello", "world"]) == "hello\nworld"


def test_build_text_unicode_and_blank_lines() -> None:
    # Unicode、中间空行、末尾换行都要能原样表达
    assert build_text(["你好", "", "RM", ""]) == "你好\n\nRM\n"


def test_build_text_empty() -> None:
    # 没有输入任何行 => 空文本
    assert build_text([]) == ""


def test_build_text_literal_marker() -> None:
    # 连续两个结束标记「..」表示正文里的一行「.」
    assert build_text([".."]) == "."
    # 正文中「等于结束标记的那一行」也能表达
    assert build_text(["abc", "..", "def"]) == "abc\n.\ndef"


def test_build_text_stops_at_marker() -> None:
    # 遇到单独一行的结束标记就停止，其后内容忽略
    assert build_text(["a", ".", "b"]) == "a"


def test_exchange_put_with_token_and_body() -> None:
    # PUT 请求要带对：方法、路径、鉴权头，以及正确的 JSON 请求体
    def respond(request: httpx.Request) -> httpx.Response:
        assert request.method == "PUT"
        assert request.url.path == "/texts/note"
        assert request.headers["Authorization"] == "Bearer example"
        assert json.loads(request.content) == {"text": "你好\nRM"}
        return httpx.Response(200, json={"data": None})

    with httpx.Client(
        base_url="http://localhost", transport=httpx.MockTransport(respond)
    ) as client:
        status, result = exchange(client, "PUT", "/texts/note", "example", {"text": "你好\nRM"})
        assert status == 200
        assert result == {"data": None}


def test_exchange_delete_with_token() -> None:
    # DELETE 请求：方法、路径、鉴权头正确，且不带请求体
    def respond(request: httpx.Request) -> httpx.Response:
        assert request.method == "DELETE"
        assert request.url.path == "/texts/note"
        assert request.headers["Authorization"] == "Bearer example"
        assert request.content == b""
        return httpx.Response(200, json={"data": None})

    with httpx.Client(
        base_url="http://localhost", transport=httpx.MockTransport(respond)
    ) as client:
        status, result = exchange(client, "DELETE", "/texts/note", "example")
        assert status == 200
        assert result == {"data": None}


def test_exchange_non_json_body() -> None:
    # 响应体不是合法 JSON 时：仍返回状态码，并把原始文本塞进 message
    def respond(request: httpx.Request) -> httpx.Response:
        return httpx.Response(502, text="Bad Gateway")

    with httpx.Client(
        base_url="http://localhost", transport=httpx.MockTransport(respond)
    ) as client:
        status, result = exchange(client, "GET", "/ping")
        assert status == 502
        assert result == {"message": "Bad Gateway"}


def test_exchange_empty_body() -> None:
    # 响应体为空（缺失）时：仍返回状态码，message 为空字符串
    def respond(request: httpx.Request) -> httpx.Response:
        return httpx.Response(204)

    with httpx.Client(
        base_url="http://localhost", transport=httpx.MockTransport(respond)
    ) as client:
        status, result = exchange(client, "GET", "/ping")
        assert status == 204
        assert result == {"message": ""}


def test_handle_token_login_success() -> None:
    # 登录成功：把新 token 存下来
    assert handle_token("login", 200, {"data": {"token": "abc"}}, "") == "abc"


def test_handle_token_login_401_clears() -> None:
    # 登录失败（401）也会清空本地 token
    assert handle_token("login", 401, {"message": "密码错误"}, "old") == ""


def test_handle_token_logout_clears() -> None:
    assert handle_token("logout", 200, {"data": None}, "old") == ""


def test_handle_token_delete_user_clears() -> None:
    # 注销账号成功：清空本地 token（2.5 的核心行为）
    assert handle_token("delete-user", 200, {"data": None}, "old") == ""


def test_handle_token_401_clears() -> None:
    # 任意受保护接口返回 401 都清 token
    assert handle_token("list", 401, {"message": "请先登录"}, "old") == ""


def test_handle_token_other_keeps() -> None:
    # 其他成功操作（如 put 200）不动 token
    assert handle_token("put", 200, {"data": None}, "old") == "old"
