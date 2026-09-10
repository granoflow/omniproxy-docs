# 09 · 网络搜索

网络搜索和模型回答是两件事。OmniProxy 可以把问题交给已连接的搜索服务，也可以通过网页读取服务取得指定页面的正文；搜索结果由独立接口返回，是否交给模型由调用方决定。公开 chat 不会自动搜索。

例如，你想查找一篇文章，先用网络搜索取得候选网址；已经知道网址时，使用网页读取来源获取正文。不要把网页读取来源当作搜索引擎，也不要只凭来源地址保存成功就认为它可以工作。

## 选择来源类型

| 类型 | 输入 | 结果 |
|------|------|------|
| 网络搜索 | 一段问题或关键词 | 标题、网址和文字片段 |
| 网页读取 | 一个明确的网址 | 页面标题、最终网址和正文 |

「网络搜索」页按模板添加来源。模板决定类型，只有当前版本具备相应 adapter 的模板才可用；页面不提供任意 API 都能直接接入的空白模板。

知乎、Brave、Tavily、Exa、Jina、Firecrawl 的模板会预填服务地址，也支持对应的完整官方 endpoint；SearXNG 需要填写实例地址。CLI 的 `http_json` 用于符合既有兼容格式的来源，不代表任意第三方返回格式都受支持。

凭据保存在系统凭据库。页面只显示掩码和配置状态，不读回原始密钥。

## 添加并测试

打开「网络搜索」，使用来源列表下方的添加按钮选择模板，填写来源名称、地址及所需凭据，再执行功能测试。

| 动作 | 应看到的结果 | 如果不符合 |
|------|--------------|------------|
| 测试搜索来源 | 短问题返回至少一条非空文字结果 | 检查地址、凭据和返回格式 |
| 测试网页读取来源 | 测试网址返回非空正文 | 检查网址与读取服务 |
| 修改配置后重测 | 当前配置显示验证通过 | 旧配置的成功结果不能沿用 |
| 查看测试详情 | 结果数量、耗时及可查看的请求/响应 | 按认证、限流、超时或格式错误处理 |

HTTP 2xx 本身不表示测试通过。空结果、空正文、缺少必要字段、无效 URL 或无法解析的 JSON 都可能导致功能测试失败。测试弹窗中的请求和响应会脱敏；JSON 格式化显示，非 JSON 保持文本，复制内容不应包含来源密钥。

## 独立搜索接口

先启用并验证一个搜索引擎来源，再使用网关的接口。请求使用网关密钥，不传第三方来源密钥：

```http
POST /v1/search
Authorization: Bearer <gateway-key>
Content-Type: application/json
```

```json
{
  "engine": "brave",
  "query": "OmniProxy",
  "limit": 8,
  "debug": false
}
```

`engine` 支持 `zhihu`、`brave`、`tavily`、`exa`、`searxng`。一次选择一个引擎，不支持 `all`、`custom_http_json` 或网页读取。该引擎必须恰好有一个已启用、且当前配置已验证的来源；接口不接受来源 ID，也不会在多个可用来源之间暗中任选。

成功响应提供规范化的 `title`、`url`、`snippet`，以及结果数和耗时，不公开内部选中的来源 ID。`limit` 默认 8，允许 1–20。

| 返回情况 | 含义与处理 |
|----------|------------|
| HTTP 200，`results: []` | 本次搜索没有命中，不等于来源功能测试通过 |
| `source_not_found` | 没有对应引擎来源，先添加 |
| `source_not_ready` | 来源未启用或当前配置未验证，先处理来源状态 |
| `source_ambiguous` | 多个来源同时满足条件，停用多余来源 |
| `invalid_response` | 上游返回不符合格式要求，检查服务与配置 |

认证、权限、额度、限流、超时和上游不可用也会分别返回可诊断错误。格式正确的零命中与无法解析的响应不是同一种情况。

`debug: true` 为本次响应附加有大小限制、脱敏的上游请求和响应。调试内容不包含网关密钥、来源凭据、Authorization 或 Cookie；仍应在分享之前检查其中的业务文本。

## CLI 入口

独立安装的 OmniProxy CLI 可按引擎搜索。前提是已经配置好唯一可用的对应来源：

```bash
omniproxy search query "OmniProxy" --engine brave --limit 8
```

成功时输出搜索结果；查询词是位置参数，不使用 `--query`。App 随附的 CLI 不提供这个直接查询入口，使用网关 HTTP 或下面的调试入口。

`search probe` 需要已初始化且正在运行、可通过本机管理接口连接的 Runtime。`--body` 接收 JSON 对象字符串，不是文件路径：

```bash
omniproxy search probe --body '{"engine":"brave","query":"OmniProxy","limit":8}'
```

调试结果包含 HTTP 状态、响应正文和耗时。命令本身成功返回不代表上游 HTTP 状态一定成功，还需要检查这些字段。

按来源 ID 操作的兼容命令仍使用 `retrieval`。以下为符合既有 `http_json` 格式的来源配置示例；先将示例地址替换为你的实际地址，并通过安全方式提供 `SEARCH_KEY`：

```bash
printf '%s' "$SEARCH_KEY" | omniproxy retrieval add personal-search \
  --adapter http_json --base-url https://search.example/api --credential-stdin
omniproxy retrieval verify <source-id> --query "明天天气怎么样"
omniproxy retrieval query <source-id> "OmniProxy"
```

将 `<source-id>` 替换为已添加来源的标识。`retrieval query` 按来源调用，不受公开搜索接口的固定引擎集合替代；模板、来源类型和参数以所用 CLI 的帮助为准。

## 外发与隐私

网络搜索会把问题或网址发送给你选择的第三方服务，可能产生服务费用。OmniProxy 不提供共用密钥。发送前脱敏的设置与限制见 [11 · 脱敏](11-redaction.md)；不要把调试输出、搜索结果或复制内容当作不含敏感信息的材料。

普通持久日志只保留运行与统计所需的来源标识、耗时、数量、状态和稳定错误码，不记录查询或完整结果正文。这不改变第三方服务自身对收到的数据如何处理。

下一章：[10 · 词表与翻译](10-glossary-translation.md)
