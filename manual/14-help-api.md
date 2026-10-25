# 命令帮助与网关 API 参考

日常图形界面操作请直接参阅对应章节。当你需要编写自动化脚本、使用 `curl` 调试网关，或排查第三方客户端的底层协议拼接问题时，可通过本章查阅 CLI 帮助命令与 HTTP 网关接口规范。

## 1. 查阅本地 CLI 帮助

你可以在终端随时通过 `--help` 查看当前安装版本的准确子命令与参数说明：

```sh
omniproxy --help
omniproxy sources add --help
omniproxy gateway capabilities --help
```

- **`--help` 与 `--help-ai` 的区别**：普通 `--help` 直接输出内置静态帮助文档，完全不消耗模型算力；`--help-ai` 则是另一个辅助解释入口，它是否实际调用了模型取决于返回结果中的标识，请勿假定 `--help-ai` 永远在线或必然返回 AI 生成的回答。
- **以实际运行结果为准**：某个子命令出现在帮助文本中，仅代表命令行合同已定义该入口；若当前安装包尚未实现该项底层操作，执行时会返回明确错误码（如 `capability_not_ready`）。

## 2. 常用模型协议端点

OmniProxy 的 HTTP 网关支持多种主流大模型协议以及原生请求透传：

| 协议类型 | HTTP 方法与路径 |
| --- | --- |
| **OpenAI Chat Completions** | `POST /v1/chat/completions` |
| **OpenAI Responses** | `POST /v1/responses` |
| **Anthropic Messages** | `POST /v1/messages` |
| **Google Gemini** | `POST /v1beta/models/{model}:generateContent`（流式：`...:streamGenerateContent`） |
| **Ollama Chat** | `POST /api/chat` |
| **上游原生透传** | `ANY /v1/raw/{deployment}/{upstream_path}` |

### 客户端 Base URL 拼接注意事项
在第三方工具中填写网关服务地址（Base URL）时，请务必查阅该工具的官方文档，确认它会在后台如何追加路径：
- 如果工具会自动追加 `/chat/completions`，你在工具里填写的 Base URL 通常需要保留末尾的 `/v1`（如 `http://127.0.0.1:端口/v1`）。
- 如果工具会自动追加完整的 `/v1/chat/completions`，则 Base URL 末尾**不要**再带 `/v1`，以免重复拼接成 `/v1/v1/...` 导致 404 错误。

### 协议转换与原生透传（`/v1/raw/...`）说明
- **协议转换边界**：网关的跨协议转换仅处理已受支持的标准语义；如果请求中包含某个厂商独有的私有扩展字段且无法转换，网关会在返回中给出警告提示。
- **如何使用原生透传**：当你需要完整保留上游供应商的原生请求语义时，可使用 `ANY /v1/raw/{deployment}/{upstream_path}`：
  - `{deployment}` 是目标来源在当前实例中的**来源标识**（不是模型 ID，也不是你在界面上随便填的中文显示名称）。
  - 在独立 CLI 实例中，可运行 `omniproxy sources list --output json`，先确认 `ok: true`，再从目标来源对象中读取准确的 `deployment` 字段值；`{upstream_path}` 则填写该供应商官方文档要求的实际接口路径（按标准 URL 路径规则编码）。
  - 请求本机网关时，Header 依然携带 OmniProxy 的**代理密钥**，上游供应商的 API Key 仍由网关在后台自动代填。
  - **切勿跨实例混填**：桌面端 App 与独立 CLI 的来源互不共享。如果你不确定桌面端 App 中某个来源的标识，请直接使用 App 内该来源模型的“接口调试”功能查看，不要把独立 CLI 查出的 `deployment` 填给 App，也不要自行盲猜内部 ID。

## 3. 使用 `curl` 发起第一条聊天请求

在运行以下终端命令前，请先在桌面端 App 的**监控台**确认网关处于**运行中**、生成并复制好**代理密钥**，并在[用固定名称映射模型](model-mapping.md)中为 `chat` 用途绑定好一个已验证的对话模型（若绑定的是远程云端模型，执行此命令将真实外发文本并产生上游计费）。

请将下方脚本中的端口与密钥替换为你自己监控台显示的实际值（注意：`OP_ORIGIN` 只保留协议、主机和端口，末尾不带 `/v1`；`56788` 仅为示例端口，请勿直接照抄）：

```sh
OP_ORIGIN='http://127.0.0.1:56788'
OP_KEY='替换为监控台复制的代理密钥'
curl --fail-with-body "$OP_ORIGIN/v1/chat/completions" \
  -H "Authorization: Bearer $OP_KEY" \
  -H 'Content-Type: application/json' \
  --data '{"model":"chat","messages":[{"role":"user","content":"请用一句话解释什么是网关。"}],"stream":false}'
```

- 如果你还没有配置 `chat` 映射，可以把 JSON 中的 `"model":"chat"` 替换为从模型列表复制的、已启用且支持对话的模型名称。
- 这里将 `"stream"` 设为 `false`（关闭流式输出），方便你一次性看清完整的响应 JSON。
- **结果核对**：调用成功时，请检查返回 JSON 中的 `choices[0].message.content` 是否非空且正确回答了问题，随后去**监控台**核对实际执行的来源与模型（注意：HTTP 网关直接返回对应协议的响应体，**没有** CLI 命令那层 `ok` / `data` 外壳，解析时切勿混用）。若返回 `401` 请先检查代理密钥；返回 `404` 请检查 URL 路径拼接；报模型或能力错误请回模型页检查状态。

## 4. 使用 `curl` 调用独立网络搜索接口

HTTP 网关提供独立的关键词搜索端点 `POST /v1/search`。它通过请求体中的 `engine` 字段自动匹配当前唯一可用的对应搜索来源，请求中无需（也不允许）传入内部来源 ID 或上游搜索密钥。

调用前，请先按[配置网络搜索与网页读取](09-search-sources.md)在当前连接的网关实例中启用并验证好 **Brave** 搜索来源，然后沿用上一节的 `OP_ORIGIN` 和 `OP_KEY` 执行：

```sh
curl --fail-with-body "$OP_ORIGIN/v1/search" \
  -H "Authorization: Bearer $OP_KEY" \
  -H 'Content-Type: application/json' \
  --data '{"engine":"brave","query":"开源模型更新","limit":3}'
```

**请求参数与返回解析规范**：
- **`engine`**：必填，可选值为 `zhihu`、`brave`、`tavily`、`exa` 或 `searxng`（注意：网页正文读取服务 Jina Reader / Firecrawl 不使用此接口，详见[配置网络搜索与网页读取](09-search-sources.md)）。
- **`query`**：必填，非空搜索关键词字符串，最大长度为 `4,096` 个 UTF-8 字节。
- **`limit`**：可选，整数范围 `1`–`20`，省略时默认为 `8`。日常调用无需开启 `debug` 字段，以免在日志中额外记录冗余调试体。
- **成功响应**：从返回的 `results` 数组中读取每条结果的 `title`、`snippet` 和 `url`，从 `meta.result_count` 查看实际返回条数（若返回 0 条结果，也请结合状态码综合判断）。
- **错误码排查**：当 HTTP 请求报错时，请读取返回 JSON 中的 `error.code` 与提示：
  - 提示来源不存在或未就绪：先在当前网关实例中添加、启用并重新验证该搜索引擎来源。
  - 返回 `search_source_ambiguous`：同一个 `engine` 下存在多个已启用且已验证的来源，请停用多余的同引擎来源，只保留一个。
  - 认证错误：先区分是本机网关的代理密钥（`OP_KEY`）填错，还是上游搜索服务商的 API Key 失效。

## 5. 排查网关请求的五步检查清单

当任何自定义脚本或工具调用网关出现异常时，请按以下顺序逐一核对：
1. **核对入口三要素**：实际发出的完整 URL 路径、请求的模型名称以及所使用的协议格式是否匹配。
2. **核对双层认证**：请求头是否携带了正确的网关代理密钥；目标上游来源是否已在 OmniProxy 内完成配置并验证通过。
3. **核对状态码与正文**：HTTP 状态码、错误码与返回正文是否一致（即便返回 `HTTP 200`，也要检查正文是否真的包含有效回答而非空内容）。
4. **核对流式完整性**：如果是流式调用（Streaming），确认数据流是否持续输出并正常结束，还是在中途异常截断。
5. **对照监控台记录**：打开[监控台](02-monitor.md)，确认该请求最终路由到的实际来源与模型是否符合你的预期。

> **关于附件与管理通道的安全提醒**：
> - 请勿把本机磁盘文件路径直接当成任意接口的附件上传参数；图片、音频、文件及扩展参数必须严格按照当前协议端点的支持范围传入，且未经解析的二进制媒体流不会自动获得文本脱敏保护。
> - HTTP 网关仅用于提供模型推理、搜索等业务调用能力。OmniProxy 自身的配置管理请使用桌面端 App 界面或[独立 CLI](12-cli-runtime.md)，切勿将内部私有管理通道配置到第三方 AI 工具中。
