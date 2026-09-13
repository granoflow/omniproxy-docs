# 12 · CLI 与运行时

CLI 用于明确执行命令和读取结构化结果，桌面版提供另一种操作界面。两种发行配置并非每个入口都可用：先检查当前二进制的帮助和能力说明，再判断命令是否适合这个运行环境。

例如，同名的 `omniproxy` 可能来自独立安装，也可能来自 App 提供的正式终端入口。遇到“不可用”或运行时连接失败，先核对实际二进制和连接对象，不要先删除数据或反复初始化。

## 三种入口

| 入口 | 用途 | 边界 |
|------|------|------|
| CLI | 参数化操作和脚本调用 | 具体命令受发行配置与运行前提限制 |
| HTTP 网关 | 客户端调用模型或独立搜索 | 不是远程管理服务 |
| 本机管理连接 | typed RPC 与持续 adapter 会话 | 需要匹配的运行实例与访问权限 |

当前没有可用的 CLI Web 管理页面，不要把 HTTP 模型端口当成 Web 管理入口。

## 命令总览

| 命令 | 用途 |
|---|---|
| `omniproxy init` | 配置翻译模型、外部来源、网络搜索和下载计划 |
| `omniproxy service start\|stop\|status\|enable\|disable` | 管理当前用户级 CLI 网关服务 |
| `omniproxy status` | 查看运行状态、锁、端口、健康度和活动任务 |
| `omniproxy doctor` | 自检配置、权限、端口、模型、检索和 schema |
| `omniproxy version` / `omniproxy -V` | 查看产品名、版本、构建与协议版本 |
| `omniproxy gateway ...` | 管理端口、代理密钥、监听范围和当前复制地址 |
| `omniproxy models ...` | 浏览、下载、删除、测试和选择本地模型 |
| `omniproxy sources ...` | 管理外部订阅来源 |
| `omniproxy retrieval ...` | 管理和测试检索源 |
| `omniproxy glossary ...` | 管理词表 |
| `omniproxy redaction ...` | 管理并真实测试脱敏 |
| `omniproxy logs ...` | 查询详情、清理日志和查看占用 |
| `omniproxy cache ...` | 查看、配置和清理路由/检索/答案缓存 |
| `omniproxy stats ...` | 查询今日、日、周、月统计 |
| `omniproxy config ...` | 管理非密钥设置 |
| `omniproxy jobs ...` | 查询、观察、取消和重试长任务 |
| `omniproxy <command> --help` / `--help-ai` | 五语静态帮助和可选 AI 增强解释 |

命令存在并不证明当前环境满足其运行条件。按帮助中的发行配置、初始化状态和运行时要求判断。

## 全局参数

| 参数 | 用途 |
|---|---|
| `-h, --help` | 按当前语言显示命令、参数、默认值和示例 |
| `-V, --version` | 显示 `OmniProxy - Personal AI Gateway` 与当前版本；不需要 Runtime |
| `--help-ai [问题]` | 请求命令解释；当前 Runtime 返回静态回退，见下文 |
| `--data-dir <path>` | 高级/测试用途：覆盖本次发行物私有 state home；不改变模型存储根 |
| `--lang <en\|zh-CN\|zh-TW\|de\|ar>` | 仅覆盖本次调用的静态帮助、运行消息和 AI 解释语言；要持久化默认语言，用 `config set runtime.language <code>` |
| `--dry-run` | 对任意命令只验证并显示执行计划，不产生持久化或外部副作用 |
| `--output <human\|json\|jsonl>` | 选择人类文本、JSON 或持续事件输出 |
| `--json` | `--output json` 的便捷写法 |
| `-v, --verbose` | 在支持详细输出的命令中查看诊断信息，具体参数以该命令帮助为准 |
| `--timeout <duration>` | 设置本次操作超时 |
| `--yes` | 对删除、清空、重置等破坏性操作显式确认 |

命令名、参数名、枚举、JSON 字段和错误码保持英文。根命令、每一级子命令、参数说明、默认值、示例、运行状态、提示和错误支持英语、简体中文、繁体中文、德语和阿拉伯语。脚本应读取 JSON 字段和错误码，不应解析翻译后的句子。

版本信息不依赖已初始化的数据目录或正在运行的 Runtime：

```text
$ omniproxy --version
OmniProxy - Personal AI Gateway
Version: 0.1.0
```

其中版本号和构建标识由实际构建产物提供；示例中的 `0.1.0` 不是固定承诺。自动化脚本可使用 `omniproxy version --json` 读取结构化字段。

### 本地推理 helper

Store 与 Homebrew 安装时都携带 `omniproxy-mlx-backend`、`mlx.metallib` 与 `omniproxy-llama-server`。运行时不下载可执行代码。包装缺少 helper 时返回 `runtime_backend_not_installed`，应重装产品，而不是执行已删除的 backend 安装命令。

## 终端快捷方式与路径诊断

首次定位原程序、创建快捷方式、配置 PATH、验证和移除，见 [01 · 安装与引导](01-getting-started.md#在任意目录运行-cli)。产品不自动管理链接或修改 shell 配置。遇到同名程序时，macOS / Linux 使用 `command -v omniproxy`、`type -a omniproxy`，Windows PowerShell 使用 `Get-Command omniproxy -All` 核对实际入口。

`init` / `doctor --json` 另外给出建议字段（不是强制）：`dual_install`、PATH 链的 `link_path` / `target_path` / `distribution` / `resolved_binary` / `path_shadowed`、是否有对方网关（`peer_gateway` + edition/pid）、以及若有冲突时的 `conflict_kind`。人类输出只在发现多个安装、终端路径异常或已有实例占用时给出建议：检测到多个 OmniProxy 时建议只保留一个；如果同时使用 App 和 CLI，两边的设置和数据分开保存。`resident_helper_unreachable` 不复用「对方占用网关」句子。

## 策略快照与模型续传

词表和规则覆盖使用显式导出、导入，不因复制模型目录而自动恢复来源、凭据或允许名单。具体覆盖语义见 [10 · 词表与翻译](10-glossary-translation.md) 与 [11 · 脱敏](11-redaction.md)。

模型下载通过已验证分片与受管 staging 恢复。不要把旧 job ID 当作另一发行物可以直接继续使用的任务，也不要手改租约或校验文件；详见 [05 · 本地模型管理](05-local-models.md)。

## 先用 help 和 dry-run 审核完整 CLI

完整命令树提供英语、简体中文、繁体中文静态 help 和全局 dry-run。可以一次导出全部帮助：

```bash
omniproxy models --help --lang zh-CN
omniproxy models --help --lang zh-TW
omniproxy models --help --lang en
```

也可以逐条预演：

```bash
omniproxy init --dry-run --output json
omniproxy service start --dry-run
omniproxy models pull <catalog-id> --dry-run --output json
omniproxy logs clear --dry-run --output json
```

dry-run 与正式执行共用相同的参数校验和计划器，但具有硬限制：

- 可以读取本地非敏感状态、检查路径和完整验证用户指定的导入文件。
- 不写 SQLite、文件或凭据库，不创建作业或 staging，不下载，不 bind 端口，不进入 watch/serve 循环。
- 不联网、不调用模型、不产生费用，也不读取 `--*-stdin` 中的秘密正文。
- 不要求 `--yes`，但会显示正式执行是否需要确认及何种敏感输入。
- 端口竞态、远端能力、模型结果等无法安全确认的事实进入 `unresolved_checks[]`，不会显示为已通过。

JSON dry-run 结果位于统一 envelope 的 `data`，固定为 `dry_run=true`、`plan_kind="business"`，并包含 `would_read`、`would_write`、`would_contact`、`would_start_jobs`、`required_secret_inputs`、`confirmation_required` 和 `unresolved_checks[]`。尚未接入领域 prepare 的命令显示 `implementation_status="contract_only"` 和 `business_prepare_not_connected` warning，只用于审阅命令及声明的业务边界；接入真实共享 prepare 后才显示 `implementation_status="implemented"`。端口竞态、远端能力、模型输出等必须执行时才能确认的条件仍明确列为未决，不会伪报成功。

## 初始化

交互使用：

```bash
omniproxy init
```

非交互初始化读取 JSON 计划。以下是不预装模型、不添加来源的最小版本 4 计划；它只完成基础设置，不会因此获得模型或搜索能力：

```json
{"version":4,"translation_model_catalog_id":null,"source_ids":[],"retrieval_source_ids":[]}
```

将计划保存为 `onboarding.json`，先验证，再确认执行：

```bash
omniproxy init --validate --non-interactive --input onboarding.json
omniproxy init --non-interactive --input onboarding.json
```

检查验证结果中的 `valid`、`issues` 和所需下载，再决定是否执行。来源 ID 必须引用已配置且满足验证条件的来源。旧的默认模型、来源 URL 和代理密钥初始化参数不能代替当前计划。

代理密钥在初始化后通过专门入口设置，不放进计划文件或命令行参数：

```bash
printf '%s' "$OMNIPROXY_KEY" | omniproxy gateway auth set --key-stdin
```

密钥可能因命令参数进入 shell 历史或进程列表，必须使用所用入口支持的安全输入方式。

## 启动、状态和停止

```bash
omniproxy service start
omniproxy service status
omniproxy status
omniproxy service stop
```

独立 CLI 通过当前用户级服务管理网关；macOS 使用 launchd，Linux 使用 systemd --user。`service enable`／`disable` 改变自动启动策略，`start`／`stop` 改变当前状态。启动请求被接受不等于模型调用已验证，随后检查 `status` 与真实调用。

旧 `omniproxy serve` 与 MCP 入口已经退役。普通 CLI 管理操作直接调用共享能力，不为此开放管理端口；App 的私有管理连接不供独立 CLI 复用。

## 模型和来源

```bash
omniproxy models list
omniproxy models search gemma --tag chat
omniproxy models pull gemma-4-e2b-it-4bit
omniproxy models test <installation-id>
omniproxy models remove <installation-id> --yes
```

`models remove --yes` 只会删除当前 OmniProxy Home `models/` 下、该安装记录明确拥有的受管目录；仍被占用的模型、下载/推理租约以及没有受管目录的旧记录都会被拒绝为 `model_busy`。它不会仅删除数据库记录来遗留未知模型文件。没有全局默认对话模型。

外部来源的密钥从 stdin 输入：

```bash
printf '%s' "$DEEPSEEK_KEY" | \
  omniproxy sources add deepseek \
  --base-url https://api.deepseek.com \
  --api-key-stdin

omniproxy sources test deepseek
omniproxy sources refresh-models deepseek
```

`sources preferred get|set|clear` 已退出公开合同，调用返回 `unknown_operation`。裸名路由：0 候选稳定错误，1 候选可用，多候选歧义错误，不得静默首选。

`sources add`、从停用状态执行 `sources enable`、`sources test` 与 `sources refresh-models` 都只使用配置的凭据读取非空模型目录；首版不探测模型类型，也不发送 `hello`、1-token 请求或任何生成请求。能列出模型即视为来源目录验证通过；失败保留来源配置和凭据但标记为未验证、不可路由。官方 Anthropic、Gemini 和任意主机的 `:11434` Ollama endpoint 自动选择原生出站适配器，其余 endpoint 默认使用 OpenAI-compatible；自定义端口的本机或远程 Ollama 用 `--adapter ollama` 显式声明。OmniProxy 不安装或管理 Ollama 进程。流式响应已经输出事件后不会重放。

`jobs watch <job-id>` 输出 snapshot/changed/terminal JSONL；Ctrl-C 只结束观察，不取消后台作业。字节作业在已有足够进度样本时显示预计剩余秒数。

## 网关和代理密钥

```bash
omniproxy gateway show
omniproxy gateway proxy pause
omniproxy gateway proxy resume
omniproxy gateway port set 56788
omniproxy gateway auth generate
omniproxy gateway auth status
omniproxy gateway auth reveal --yes
omniproxy gateway listen show
omniproxy gateway listen set local
omniproxy gateway listen set all
omniproxy gateway endpoints list
omniproxy gateway endpoints select <endpoint-id>
omniproxy gateway show --copy url
```

切换为 `all` 前必须已经设置代理密钥，否则返回 `proxy_key_required` 且配置不变。`local` 同时监听 IPv4/IPv6 loopback，`all` 同时监听 IPv4/IPv6 wildcard；任一必要 listener 失败都不会留下半生效状态。endpoint 选择只改变 `show`、托盘和 GUI 当前展示/复制的地址，不改变监听范围。`auth generate` 和 `auth reveal --yes` 都只允许交互式 TTY 输出明文；JSON/JSONL、dry-run、非 TTY 和日志只显示密钥状态或掩码。

App 的私有管理连接与 HTTP 代理端口用途不同。独立 CLI 不提供管理监听；设置结果如果返回 `change_effect=next_runtime_start`，表示配置将在下次 Runtime 启动时生效。

## 检索、词表和脱敏

网络搜索的完整例子与当前引擎选择规则见 [09 · 网络搜索](09-search-sources.md)。下面保留按来源操作及词表、脱敏示例；占位符必须替换为真实来源。

```bash

printf '%s' "$SEARCH_KEY" | omniproxy retrieval add tavily \
  --adapter http_json --base-url https://search.example/api --credential-stdin
omniproxy retrieval enable <source-id>
omniproxy retrieval disable <source-id>
omniproxy retrieval verify <source-id> --query "OmniProxy"
omniproxy retrieval query <source-id> "OmniProxy"

# 查看并导出当前生效的基础词表
omniproxy glossary list
omniproxy glossary export omniproxy-base-en-zh-cn --output-file ./base.csv

# 明确导出未经用户覆盖的内置版本
omniproxy glossary export omniproxy-base-en-zh-cn --layer builtin \
  --output-file ./base-builtin.csv

# 编辑后上传；同名即形成用户覆盖，非交互覆盖需 --yes
omniproxy glossary import ./base.csv --yes

# 删除用户覆盖并恢复内置版本
omniproxy glossary reset omniproxy-base-en-zh-cn --yes

omniproxy glossary mode set auto
omniproxy glossary mode set manual --glossary-key omniproxy-base-en-zh-cn
omniproxy glossary mode set off

omniproxy redaction status
omniproxy redaction sources list
omniproxy redaction sources set --kind model_source \
  --source <source-id> --enabled true
omniproxy redaction settings set --review-model 'local/<catalog-id>'
printf '%s' '{"mode":"translation","text":"contact jane@example.com"}' \
  | omniproxy redaction test --source <source-id> --stdin

# 下载只读默认规则，查看或应用用户覆盖文档
omniproxy redaction rules defaults export --output-file ./omniproxy-redaction-defaults.yaml
omniproxy redaction rules overrides show
omniproxy redaction rules plan --stdin < ./my-redaction-overrides.yaml
omniproxy redaction rules apply --stdin --yes < ./my-redaction-overrides.yaml

# 允许名单的值从标准输入进入，不放在命令行参数中
printf '%s' 'Jane Example' | omniproxy redaction allowlist add --value-stdin
omniproxy redaction allowlist list
```

发送前脱敏按外部来源分别设置并默认关闭，没有全局 egress 开关或继承/覆盖模式。勾选来源后，`pii` 标准规则和 OmniProxy 补充规则始终运行；通过 `redaction settings set --review-model <local/ref|none>` 独立选择已就绪的本地对话模型或停用复核；复核不可用、超时或只完成部分分段时，Runtime 使用 Rust 结果继续并返回 `review_incomplete`。首版不提供账本文本脱敏 CLI 或公共合同；调用正文保留与清理由 D40 和日志设置负责，凭据与翻译恢复映射始终不入账。未解析图片、音频、视频和二进制 raw 正文不在文本脱敏范围，Runtime 原样转发并返回 `non_text_unredacted`。默认规则文档只读；用户覆盖只应用已知规则的显式 `enabled: true|false`。没有该字段、删除导出记录或修改只读字段都不会改写 Runtime。`plan` 输出 `applied`、`unchanged`、`warnings` 与 `errors`，应先确认再执行 `apply`。允许名单只接受精确文本值，不接受正则、通配符或 detector 定义。

翻译词表也采用只读内置层和用户覆盖层，但覆盖单位是整份词表：上传同名词表后，用户版本成为当前有效版本，不逐词条与内置版本混合。导入失败不会改变现行版本。`glossary reset` 只删除用户覆盖，随后自动使用当前 OmniProxy 版本提供的内置词表。


## 日志和统计

```bash
omniproxy logs list --status error --since 24h
omniproxy logs show <call-id>
omniproxy logs show <call-id> -v
omniproxy logs show <call-id> --output json
omniproxy logs storage
omniproxy logs clear --yes

omniproxy cache status
omniproxy cache policy get
omniproxy cache policy set --retrieval enabled --answer disabled
omniproxy cache clear --yes

omniproxy stats show --period today
omniproxy stats show --period month --group-by model
```

`logs list` 和 `logs watch` 支持 `--status`、`--source-id`、`--since`、`--until`；时间既可用 Unix epoch 毫秒，也可用 `24h`、`7d` 这类“距现在多久”的写法。`logs list` 还支持 `--page`，每页最多 100 条。

`logs show` 按正文保留策略美化显示实际发给目标 AI 的最终请求 JSON 与实际收到的响应 JSON；加 `-v` 追加已掩码头部和注入上下文。正文到期后仍返回 `body_state=expired` 与安全元数据，不伪造空响应。详细输出以 `logs show --help` 为准。

请求无法无损转译时会返回警告，不应静默当作完整成功。网络搜索使用独立 `/v1/search` 和对应 `search query` / `search probe`，不会因 chat 开关自动执行。`files` 接受有界内联 data URI，不读取调用方指定路径，也不联网抓附件；格式与平台限制见 [14 · 帮助与 API 文档](14-help-api.md)。

每次缓存命中仍生成一条轻量调用记录，并以 `cache_source_call_id` 指向被复用的原始记录，因此调用次数、命中率和节省 token 都可以核对；响应正文不重复保存。检索缓存默认开启，答案缓存默认关闭。显式开启答案缓存后，key 是发行物私有 HMAC，响应用系统凭据库保护的 AES-256-GCM 密钥加密；认证失败即删除并按未命中处理。

清空调用日志同时清除当前发行物的缓存，但不清除长期统计表，行为与 GUI 一致。

GUI 的监控、详情、统计和设置不读取上述终端输出。它们通过本机 gRPC 的调用账本查询和实时事件流读取相同的结构化记录；终端 stdout/stderr 仅服务于人在终端或 systemd / launchd 日志中排障。GUI 内“CLI 命令行”页是唯一展示例外：它可以原样显示用户主动运行命令的 stdout/stderr，但仍不得从这些文本推导产品状态。

## 长任务

模型下载等长任务返回 `job_id`，例如：

```bash
omniproxy models pull mlx-community/example --detach --output json
omniproxy jobs show <job-id>
omniproxy jobs watch <job-id> --output jsonl
omniproxy jobs cancel <job-id>
omniproxy jobs retry <job-id>
```

没有常驻 Runtime 时，长任务默认在当前终端前台完成。`--detach` 需要一个正在运行且能接管任务的 Runtime；如需启动 CLI 网关服务，使用 `omniproxy service start`。

前台作业收到 Ctrl-C 时请求取消；`jobs watch` 收到 Ctrl-C 只停止观察。取消下载保留已校验 partial 供后续 retry；Runtime 崩溃后，可恢复作业重新排队，不可恢复作业以 `runtime_interrupted` 失败。终态作业记录保留30天。

JobService 同时返回两种作用范围：模型资产等 Shared 工作是 `scope=shared`；来源测试、检索验证和账本维护等只属于当前发行物的工作是 `scope=private`。Private 作业属于当前发行物，不因共用模型文件而共享。公开的 list/show/watch 不返回作业输入、结果正文或 checkpoint，因此来源密钥和待处理正文不会借作业接口泄漏。

`jobs watch` 是真实事件流：第一条为 `snapshot`，变化为 `changed`，终态为 `terminal`，随后服务端关闭流。取消 queued 作业可直接进入 `cancelled`；取消 running 作业先进入 `cancelling`，worker 到下一个安全点确认后才成为 `cancelled`。同步网络或文件调用不能在系统调用中间强行中断，最多等待到其返回后的第一个安全点。

`jobs retry` 不复活旧记录，而是创建新的 queued 作业；只有标记为 resumable 且已 `failed`/`cancelled` 的作业可以重试。新作业继承最后一个已验证 checkpoint；模型下载还继承原作业的内部 staging 身份，所以新 job ID 不会让 `.part` 从零开始。该内部身份不通过 CLI/gRPC 暴露，也不能指定任意路径。Runtime 启动时先关闭遗留 attempt：可恢复工作重新排队，不可恢复工作写入 `runtime_interrupted`；损坏的 Private 作业输入只失败该作业，不阻断 UDS/HTTP 就绪。模型下载的分片与恢复规则见[本地模型](05-local-models.md)。

## 两层帮助

第一层是快速、离线、稳定的五语静态帮助；命令和参数保持英文，说明随 `--lang en|zh-CN|zh-TW|de|ar` 切换：

```bash
omniproxy --help --lang zh-CN
omniproxy models pull --help --lang zh-TW
omniproxy models --help --lang zh-CN
```

第二层是可选 AI 增强：

```bash
omniproxy models pull --help-ai "下载中断后如何恢复？" --lang zh-CN
```

当前帮助服务返回 `source: static`、`used_ai: false` 和静态回退提示，不提供已经实现的模型回答或引文保证。独立的 `omniproxy helper` 和通用聊天入口已经废弃。

## 结构化输出和退出码

所有业务 JSON 输出都有稳定的 `schema_version`、`operation`、`ok`、`data`、`warnings` 和 `error`。dry-run 使用业务计划并保留无法无副作用确认的条件；静态 `--help` 保持终端文本格式，不属于业务结果 envelope。持续进度使用 JSON Lines，每行一个完整事件。

| 退出码 | 含义 |
|---:|---|
| `0` | 成功 |
| `1` | 一般执行失败 |
| `2` | 用法或参数错误 |
| `3` | 未初始化或配置不完整 |
| `4` | Runtime、端口或数据锁冲突 |
| `5` | 目标不存在 |
| `6` | 权限不足 |
| `7` | 上游或依赖不可用 |
| `130` | 用户中断 |

## 判断一次操作是否成功

命令存在、dry-run 成功、HTTP 网关可用、typed 管理连接可用和模型真实调用成功是不同层次。分别检查所需结果，不用其中一项代替另一项。

脚本应检查退出码以及 JSON 的 `ok`、`error` 和 `warnings`。后台作业还需要观察终态，不能仅凭拿到 job ID 宣称下载完成。发生错误时保留安全错误信息，按 [13 · 运行时系统状态](13-system-states.md) 排查，不先删除私有状态。

下一章：[13 · 运行时系统状态](13-system-states.md)
