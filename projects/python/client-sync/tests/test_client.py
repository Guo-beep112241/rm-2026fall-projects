import json

import httpx

from text_service.client import build_text, exchange


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
