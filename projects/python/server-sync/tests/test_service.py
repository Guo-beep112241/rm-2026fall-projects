from text_service.service import TEXT_MAX_BYTES, Service


def test_account_lifecycle() -> None:
    service = Service()
    account = {"username": "alice", "password": "password1"}
    assert service.handle("GET", "/ping", None, "") == (200, {"data": "pong"})
    assert service.handle("POST", "/users", account, "")[0] == 201
    assert service.handle("POST", "/users", account, "")[0] == 409
    assert service.handle("POST", "/sessions", {**account, "password": "incorrect"}, "")[0] == 401
    token = service.handle("POST", "/sessions", account, "")[1]["data"]["token"]
    next_token = service.handle("POST", "/sessions", account, "")[1]["data"]["token"]
    assert token != next_token
    assert service.handle("GET", "/texts", None, f"Bearer {token}")[0] == 401
    assert service.handle("GET", "/texts", None, f"Bearer {next_token}") == (200, {"data": []})
    assert service.handle("DELETE", "/sessions/current", None, f"Bearer {next_token}")[0] == 200
    assert service.handle("GET", "/texts", None, f"Bearer {next_token}")[0] == 401


def test_validation() -> None:
    service = Service()
    for body in (
        None,
        [],
        {},
        {"username": True, "password": "password1"},
        {"username": "a/b", "password": "password1"},
    ):
        assert service.handle("POST", "/users", body, "")[0] == 400


def test_echo() -> None:
    service = Service()
    # 回显原样往返：Unicode、换行、空字符串
    assert service.handle("POST", "/echo", {"text": "你好\nRM"}, "") == (200, {"data": "你好\nRM"})
    assert service.handle("POST", "/echo", {"text": ""}, "") == (200, {"data": ""})
    # 字段不合法 → 400
    for body in (None, [], {}, {"text": 42}, {"text": "a", "extra": 1}):
        assert service.handle("POST", "/echo", body, "")[0] == 400
    # 文本超限 → 413（一个「汉」占 3 字节，取超过上限的最少数量）
    assert service.handle("POST", "/echo", {"text": "汉" * (TEXT_MAX_BYTES // 3 + 1)}, "")[0] == 413


def test_concurrent_registration() -> None:
    from concurrent.futures import ThreadPoolExecutor

    service = Service()
    body = {"username": "alice", "password": "password1"}
    with ThreadPoolExecutor(max_workers=4) as pool:
        statuses = list(pool.map(lambda _: service.handle("POST", "/users", body, "")[0], range(4)))
    assert sorted(statuses) == [201, 409, 409, 409]
