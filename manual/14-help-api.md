# 命令帮助与 API 参考

普通操作从对应手册章节开始。需要写脚本或接入其他工具时，再用当前 CLI 帮助和协议接口核对精确字段。

## 本地帮助

```sh
omniproxy --help
omniproxy sources add --help
omniproxy gateway capabilities --help
```

`--help` 不需要模型回答。`--help-ai` 是另一个解释入口，是否使用了模型应以返回结果为准，不能假定始终在线或始终提供 AI 回答。某个命令存在也不证明该发行物已经实现全部操作。

## 常用模型接口

| 协议 | 入口示例 |
| --- | --- |
| OpenAI Chat Completions | `POST /v1/chat/completions` |
| OpenAI Responses | `POST /v1/responses` |
| Anthropic Messages | `POST /v1/messages` |
| Gemini | `POST /v1beta/models/{model}:generateContent`，流式使用 `:streamGenerateContent` |
| Ollama Chat | `POST /api/chat` |
| 原生透传 | `ANY /v1/raw/{deployment}/{upstream_path}` |

工具配置 Base URL 时要检查它如何追加路径。例如工具自行追加 `/chat/completions` 时，服务地址通常需要包含 `/v1`；若工具自行追加完整 `/v1/...`，不能再拼两次。精确做法按工具官方说明，不仅凭字段名猜。

协议转换只能处理已支持的语义；厂商独有字段可能不能转换，检查返回警告。原生透传用于保留供应商原生请求语义，它仍需明确目标和认证，不代表任意来源可以相互替代。

原生透传路径中的 `{deployment}` 是来源标识，不是模型 ID 或随意写的显示名称。独立 CLI 实例可用 `omniproxy sources list --output json`，先确认 `ok`，再读取目标来源的 `deployment` 字段；路径中的 `{upstream_path}` 使用该供应商实际接口路径，按 URL 路径要求编码。连接网关仍带代理密钥，供应商凭据由来源配置承担。App 来源与独立 CLI 不共享；不确定 App 来源标识时，使用该来源模型的接口调试入口，不把另一 CLI 实例的 `deployment` 填给 App，也不猜内部 ID。该高级透传入口未包含在本次八项核心成功实测中。

## 发出第一条聊天请求

先在 App 监控台生成或复制代理密钥，启用已经测试的 `chat` 用途映射，确认网关运行。以下使用终端自带的 `curl`；会向 `chat` 的实际目标发送文本，外部模型可能计费。将示例地址替换成监控台实际地址：`OP_ORIGIN` 只保留协议、主机和端口，不带末尾 `/v1`；示例端口不是固定承诺。

```sh
OP_ORIGIN='http://127.0.0.1:56788'
OP_KEY='替换为监控台复制的代理密钥'
curl --fail-with-body "$OP_ORIGIN/v1/chat/completions" \
  -H "Authorization: Bearer $OP_KEY" \
  -H 'Content-Type: application/json' \
  --data '{"model":"chat","messages":[{"role":"user","content":"请用一句话解释什么是网关。"}],"stream":false}'
```

没有配置 `chat` 时，把 JSON 的 `model` 改为模型列表复制的、已启用且支持聊天的完整 ID。`messages` 是消息数组，`role` 为消息角色，`content` 为文本；这里关闭流式，便于先检查完整结果。

成功时检查 `choices[0].message.content` 是否非空并回应问题，再去监控台确认实际来源和模型。401 先查代理密钥；404 先核对完整 URL；模型或能力错误回模型页检查 ID 与支持范围。这里的 HTTP 正文不是 CLI 的 `ok/data` 外层，不能混用解析。

## 独立搜索

`POST /v1/search` 按 `engine` 选择唯一可用搜索来源。`engine` 使用当前支持的知乎、Brave、Tavily、Exa、SearXNG 标识；请求不携带内部来源 ID 或来源密钥。

先按[搜索指南](09-search-sources.md)在所调用网关实例中启用并验证 Brave，沿用上一节实际 `OP_ORIGIN` 和 `OP_KEY`，执行：

```sh
curl --fail-with-body "$OP_ORIGIN/v1/search" \
  -H "Authorization: Bearer $OP_KEY" \
  -H 'Content-Type: application/json' \
  --data '{"engine":"brave","query":"开源模型更新","limit":3}'
```

`engine` 的标识为 `zhihu`、`brave`、`tavily`、`exa` 或 `searxng`；`query` 为非空查询文本，最长 4,096 个 UTF-8 字节；`limit` 为 1—20，省略时为 8。普通调用不必开启 `debug`，避免额外记录请求与响应。成功检查 `results` 中的 `title`、`snippet`、`url` 与 `meta.result_count`；零结果也要结合状态判断。HTTP 错误读取 `error.code` 和提示：来源不存在先添加，来源未就绪先启用并重新验证，`search_source_ambiguous` 则停用同引擎多余可用来源。认证先检查代理密钥，上游认证再检查搜索供应商凭据。

搜索不会自动把结果塞进聊天请求，也不等于网页读取。把结果交给 AI 工具还需要工具明确支持这条能力，或由你提供检索结果。

## 一条请求应检查什么

1. 实际请求的 URL、模型和协议是否正确。
2. 网关代理认证是否正确，来源是否已经配置并验证。
3. HTTP 状态、返回正文和错误码是否一致；成功状态仍要检查结果内容。
4. 流式调用是否持续返回并正常结束，是否只收到一半。
5. 调用记录里的实际来源和模型是否符合预期。

不要把本机文件路径当作任意附件上传接口。媒体、文件及扩展参数须按当前入口支持范围提供；未经解析的二进制也不能当作已脱敏文本。

## 公共调用与管理

HTTP 网关供工具调用模型、搜索等能力。管理操作使用 CLI；App 使用自己的本机连接。接入远程 MCP 工具与使用 MCP 管理 OmniProxy 是两回事，详见[MCP 服务](mcp-services.md)。不要将私有管理通道配置到第三方工具里。
