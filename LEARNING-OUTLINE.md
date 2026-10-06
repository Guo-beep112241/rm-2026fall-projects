# 项目学习大纲（引导 Agent 版）

> 用途：这是给「引导 Agent」参考的完整路线图。Agent 照此一步步带我（候选人）做项目，
> **边做边学**，而不是直接代写全部答案。每完成一个小任务，先讲清概念 → 让我动手 → 补测试 →
> 跑检查 → 提交。我是走 **Python 路线先熟悉项目**，之后再学 **Rust** 优化/重实现。

---

## 0. 给引导 Agent 的工作原则（贯穿全程，务必遵守）

1. **先教后做**：每个新概念（HTTP、token、锁、异步等）先用一两句话解释「它解决什么问题、为什么这里需要它」，再让我动手写。
2. **引导思考，不直接给答案**：先让我试、让我查官方文档；我卡住时给提示和排查方向，而不是直接贴完整代码。
3. **小步推进**：一次只做一个接口/一个行为，补上对应测试，跑过检查，再 commit，再进入下一步。
4. **每个小任务都要验证**：能写测试就用测试验证；能交互就用客户端/参考程序验证。不让「看起来能跑」蒙混过关。
5. **查官方文档优先**：遇到不熟的库/命令/报错，带准确的符号名、报错去查官方文档（Python 见 `projects/python/learning.md` 的资料表），结论回到项目验证。
6. **AI 代码要理解再提交**：我给的解释/代码必须自己跑测试、回官方文档求证后，才允许提交。

---

## 项目概览（Agent 先带我用 5 分钟建立心智模型）

- **是什么**：一个 HTTP 文本服务。客户端 + 服务端，HTTP/1.1，默认 `http://127.0.0.1:7878`，请求/响应为 UTF-8 JSON，数据全部存内存、重启即清空。
- **考核重点**：不是业务本身，而是工程能力——Git 工作流、测试、HTTP 协议理解、身份验证、用户数据隔离、共享状态并发保护、异步阻塞、验证方法。
- **权威文档**：
  - `common/protocol.md` —— 9 个接口的唯一验收标准
  - `common/tasks.md` —— 三层任务的推进顺序
  - `common/preface.md` —— 学习心态与取舍
  - `common/self-check.md` —— 自查问题（面试题库示例）

### 9 个接口与现状

| 接口 | 说明 | 起始状态 |
|---|---|---|
| `GET /ping` | 连通检查，返回 `{"data":"pong"}` | ✅ 已实现 |
| `POST /users` | 注册（不自动登录） | ✅ 已实现 |
| `POST /sessions` | 登录，发 token | ⚠️ 部分（缺过期/`expires_in`） |
| `DELETE /sessions/current` | 退出，撤销当前 token | ✅ 已实现 |
| `GET /texts` | 列出当前用户文本名（升序） | ✅ 已实现（列表恒空，待补上传后验证） |
| `POST /echo` | 回显文本 | ❌ 待实现 |
| `PUT /texts/{name}` | 上传/覆盖文本 | ❌ 待实现 |
| `GET /texts/{name}` | 读取文本 | ❌ 待实现 |
| `DELETE /texts/{name}` | 删除文本 | ❌ 待实现 |
| `DELETE /users/me` | 注销账号（连同文本、token） | ❌ 待实现 |

---

## 全程贯穿的工作习惯（每个阶段都执行）

### 检查命令（提交前必须依次通过）

在具体任务目录内：

```bash
uv sync --locked              # 首次/依赖变化时
uv run pytest                 # 测试
uv run ruff check .           # lint
uv run ruff format --check .  # 格式
uv run pyright                # 类型检查
```

### 提交纪律

- 一个提交 = 一个可独立验证的小改动；提交信息说明「改了什么、为什么」。
- 提交前 `git diff` 自查；不提交 `.venv/`、缓存、构建产物、凭证（已由 `.gitignore` 覆盖）。
- `commit`（本地）≠ `push`（远程）；先在个人仓库里留自然、可读的提交历史。

### 学习节奏

- 每完成一个阶段，用 `common/self-check.md` 里对应小节的问题自查（不提交答案）。
- 卡住时：把问题缩小成最小复现 → 查文档/验证假设 → 补回归测试。

---

## 阶段 0 — 环境与 Git/GitHub 准备

**目标**：环境可用；有个人仓库，之后都在个人仓库做。

- [ ] 确认环境：Python ≥3.13、uv、git（`python3 --version`、`uv --version`、`git --version`）。
- [ ] 学习 Git/GitHub：按 `common/git-github.md` 的教程链接。
- [ ] 在 GitHub 把本仓库作为**模板**创建个人私有仓库。
- [ ] 理解 `git status` / `git add` / `git commit` / `git push` / `.gitignore` 各自作用（见 self-check「开发工作流与 Git」）。

**学习点**：工作目录 / 暂存区 / 本地提交 / 远程仓库四者的关系；`commit` 与 `push` 的区别。

---

## 阶段 1 — 跑通起始代码（理解「已实现」长什么样）

**目标**：确认起始代码能跑、测试能过，建立对现状的准确认识。

- [ ] 三个目录各执行 `uv sync --locked`，再 `uv run pytest`（应全绿）。
- [ ] 理解 `pyproject.toml` / `uv.lock` / `.venv` 的关系（见 preface.md 的追问示例）。
- [ ] 手动交互一次：起 `server-async`（终端 1）+ `client-sync`（终端 2），走 `ping → register → login → list → logout → q`。
- [ ] 观察：`echo/put/get/delete/delete-user` 现在提示未实现——记下这就是要补的。
- [ ] 读起始代码 `service.py` / `server.py` / `client.py`，能说清每个文件职责（见 Python README 的代码结构表）。

**学习点**：`uv sync --locked` 的 `--locked` 保护什么；`ruff/pytest/pyright` 各发现哪类问题；为什么业务、HTTP 适配、测试分开放。

---

## 阶段 2 — 同步客户端 `client-sync`（必做）

**目录**：`projects/python/client-sync/`
**权威任务**：`common/tasks.md` §同步客户端；协议依据 `common/protocol.md`
**验证工具**：用**参考服务端** `rm-server-async` 测真实交互。

按 6 个小任务推进，每个都「补测试 + 跑检查 + commit」：

### 任务 2.1 验证已有流程
- [ ] 跑通 `ping / register / login / list / logout`，确认显示状态与结果、登录存 token、退出清 token。
- **学习点**：HTTP 请求/响应各含什么；客户端为何按状态码（而非 `message`）判断结果。

### 任务 2.2 回显与文本输入
- [ ] 实现 `POST /echo`，把输入放进 `text` 字段。
- [ ] 支持 Unicode、空字符串、**终端多行输入**（自己定结束标记，但正文里「与结束标记相同的一行」也要能表达）。
- [ ] 确认响应与输入一致；补输入处理与请求构造的测试。
- **学习点**：请求体如何 JSON 编码；多行输入的边界表达。

### 任务 2.3 上传与读取
- [ ] 实现 `PUT /texts/{name}`、`GET /texts/{name}`，读取名称+文本并带登录 token。
- [ ] 验证：上传后可读回原文；同名再上传读回新内容。

### 任务 2.4 删除并验证列表
- [ ] 实现 `DELETE /texts/{name}`；结合已有 `GET /texts` 看上传/删除后列表变化。
- [ ] 验证：名称按序显示；获取/删除不存在的文本显示 404。

### 任务 2.5 账号注销
- [ ] 实现 `DELETE /users/me`，成功后清除本地 token。
- [ ] 验证：旧 token 无法再访问；同名重注册、登录后列表为空。

### 任务 2.6 失败与退出
- [ ] 401 时提示重新登录并清 token；错误体缺失/非 JSON 时仍显示 HTTP 状态。
- [ ] 用 HTTP 库的有限超时：连接失败/超时后能继续操作或明确退出。
- [ ] `q` 与 Ctrl-C 正常退出；为响应处理补测试。
- **学习点**：令牌保存在哪、401/过期/退出/注销后客户端该如何处理本地状态（见 self-check「协议与行为边界」）。

---

## 阶段 3 — 同步服务端 `server-sync`（可选过渡层）

**目录**：`projects/python/server-sync/`
**说明**：业务要求与异步服务端完全一致，只是不碰 `async/await`，用 `service.py` 的同步 `handle()` 补业务。时间紧可跳过，直接做阶段 4。

按 7 个小任务推进：

### 任务 3.1 验证已有账号流程
- [ ] `ping / users / sessions / sessions/current / texts` 行为正确：重复注册 409、错误凭据 401、再次登录旧 token 失效、退出使当前 token 失效。

### 任务 3.2 回显与输入校验
- [ ] 实现 `POST /echo` 原样返回 `text`；Unicode/换行/空文本可往返。
- [ ] 非法 JSON、缺/多字段、错误类型→400；文本或请求体超限→413。

### 任务 3.3 文本上传与读取
- [ ] 实现 `PUT /texts/{name}`、`GET /texts/{name}`；由 token 确定用户，只访问本人数据。
- [ ] 创建/同名覆盖/读取一致；无效身份 401；不存在文本 404。

### 任务 3.4 删除、列表与隔离
- [ ] 实现 `DELETE /texts/{name}`；验证列表升序、删除移除、空列表、重复删除 404。
- [ ] **两个用户**保存同名文本，读/写/列/删互不影响。

### 任务 3.5 账号注销
- [ ] 实现 `DELETE /users/me`，一起清理用户+全部文本+token。
- [ ] 旧 token 失效；同名重注册无旧数据；注销后旧身份的并发操作不能再写入；旧账号登录尚在处理时，不能作用于重注册的新账号。

### 任务 3.6 令牌过期
- [ ] 实现 `--token-ttl-seconds`（默认 300）；`POST /sessions` 响应补 `expires_in`。
- [ ] 所有受保护接口检查有效期；到期 401、操作不续期、重新登录换 token、退出/注销仍能撤销。
- **学习点**：用「经过时间」的时钟算有效期，不用墙钟（`time.monotonic`/`perf_counter` 之类）。

### 任务 3.7 边界、并发与错误恢复
- [ ] 各接口的 400/401/404/405/409/413；未知路径、不支持方法。
- [ ] 并发一致性：同名注册竞争只能一次成功；文本操作、登录替换、注销竞争不产生中间态。
- [ ] 单请求失败不影响其他请求；连接/Ctrl-C 用框架常规机制退出。
- **学习点**：服务端有哪些共享状态、用什么保护（现有 `threading.Lock`）；为何「同步业务处理 ≠ 请求串行执行」。

---

## 阶段 4 — 异步服务端 `server-async`（必做）

**目录**：`projects/python/server-async/`
**说明**：接口/测试要求 = 阶段 3 全部 7 步，但用异步请求处理；跳过阶段 3 也须在此完成全部任务。

**异步专属难点（Agent 重点带我理解）**：
- 密码计算（`pbkdf2`）等**阻塞工作**须 `asyncio.to_thread` 移出事件循环（起始 `server.py` 已有示范）；不能只把函数改成 `async`。
- 共享状态仍要保护；鉴权与数据操作保持一致；**不在持锁期间等待网络**。
- 并发请求下验证业务结果与错误恢复；网络/超时/退出沿用框架机制。

**学习点**（见 self-check「并发与异步」）：`async/await` 到底改变了什么；阻塞调用为何不能靠加 `async` 解决；持锁等待网络 I/O 会有什么后果、如何调整锁范围。

按阶段 3 的 7 个任务逐个完成，每步补测试（异步测试用 `httpx2` + `anyio`，见起始 `tests/test_http.py`）。

---

## 阶段 5 — 复盘自查与面试准备

- [ ] 用 `common/self-check.md` 全部问题自查：环境/工具链、Git、协议行为、并发异步、测试验证、路线补充（Python）。
- [ ] 能口头解释：HTTP 请求响应、token 生命周期、用户数据隔离、共享状态保护、异步阻塞、测试的目的。
- [ ] 能说清「完成了什么、没完成什么、为什么这样安排」（面试会问学习过程与取舍，不考背诵）。
- [ ] 检查个人仓库提交历史是否自然、可读、无杂物。

---

## 阶段 6 — Rust 路线（Python 之后，第二语言）

**前置**：装稳定版 Rust（rustup）。Python 阶段已把协议、并发、异步、测试这些**通用工程问题**吃透，这里只需学语言本身。

**目录映射**（镜像 Python 三层）：

| Rust | Python | 说明 |
|---|---|---|
| `projects/rust/client-sync/` | client-sync | 用 `reqwest` + `clap` |
| `projects/rust/server-sync/` | server-sync | 用 Rocket（同步适配层 `infrastructure.rs`） |
| `projects/rust/server-async/` | server-async | Rocket + `spawn_blocking` 隔离阻塞 |

**Rust 专属要学**：所有权/借用、`String`/`Vec`/`BTreeMap`/锁、Cargo 与锁文件、crate/module 组织（业务放 `lib.rs` 便于测试）、Rocket 路由与测试、`serde_json`、Clippy/rustfmt。

**检查命令**：

```bash
cargo fmt -- --check
cargo check --locked
cargo clippy --locked --all-targets -- -D warnings
cargo test --locked
cargo build --release --locked
```

**推进顺序**：先跑通 Rust 起始代码 → 按客户端 → 服务端 的顺序，把 Python 阶段做过的每个接口在 Rust 里再实现一遍，边写边对照「为什么 Rust 写法不同」（所有权、错误处理、trait）。

---

## 附：各阶段产出检查清单（Agent 核对用）

每个小任务完成后，引导 Agent 确认：
1. ✅ 功能行为符合 `protocol.md`（状态码 + 响应体 `data` 结构）。
2. ✅ 有对应测试，且 `uv run pytest` 通过。
3. ✅ `ruff check` / `ruff format --check` / `pyright` 通过。
4. ✅ 已 `git commit`（信息说明改动目的）。
5. ✅ 我能用自己的话解释「为什么这样改、可能影响什么、如何验证」。

> 达到这 5 条再进入下一个小任务；不必追求「彻底搞懂每个工具」，分清「需要理解取舍 / 知道即可 / 忘记没关系」三层（见 preface.md「学习的取舍」）。
