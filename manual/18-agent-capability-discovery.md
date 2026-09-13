# 18 · Agent 能力发现

Agent 不必靠模型名称猜 OmniProxy 能做什么。它需要能执行 OmniProxy CLI 的命令行工具；负责发起模型请求的客户端还须已经配置好网关 endpoint 与认证。确认 CLI 指向目标发行物后，Agent 可以查询该实例的模型能力快照，再按用户任务和授权选择模型。快照像一张随时更新的菜单：它能说明记录了哪些菜和规则，但不保证厨房此刻可用，更不会替用户下单。命令定位与发行物差异见 [12 · CLI 与运行时](12-cli-runtime.md)。

## 查询当前实例

```bash
omniproxy gateway capabilities --output json
```

这是只读查询，不会联网探测 Provider、调用模型、启用模型、修改配置或创建调用记录。请使用正常命令，不要加 `--dry-run`；dry-run 只审阅命令计划，不返回能力快照。

输出使用 OmniProxy CLI 的标准 JSON envelope。能力结果在 `data` 中，包含独立的 `schema_version`、`instance_scope`、`snapshot_at_epoch_ms` 和 `models[]`。`schema_version` 当前为 `1`；遇到不认识的版本时，Agent 应停止自动选择，不要猜字段含义。

`instance_scope` 表示 `standalone_cli` 或 `desktop_app`。两者状态彼此隔离；Agent 应查询它实际连接的那一份，不要把一份实例的结果拿去调用另一份。

独立 CLI 只读取已初始化的本地状态；若尚未初始化，返回 `not_initialized`，不会替用户引导初始化或创建状态。App CLI 通过本机私有管理连接读取对应 App Runtime，Runtime 不可用时命令会失败。此命令不负责启动 App、Runtime 或公共 HTTP 网关。

## 如何读一条模型记录

模型引用使用网关接受的稳定名称：本地模型形如 `local/<catalog-slug>`，外部模型形如 `<deployment>/<model-id>`。不要改成仓库地址或来源内部 ID。

| 字段 | 含义 |
|---|---|
| `purposes` | 本地安装 Runtime 元数据中已记录的用途标签；远端无明确用途证据时为空。标签保留安装记录原值，不保证等同于浏览目录 schema-v5 的规范名。 |
| `purpose_evidence` | 本地为 `installation_metadata`；远端缺少用途证据时为 `unknown`。这不是调用成功证明。 |
| `availability` | `configured` 表示记录的配置/准入条件齐备，不保证文件、后端、监听端口或远端服务此刻正常；`unavailable` 表示已知配置门未通过；`ambiguous` 表示公开引用重复，不能选择。 |
| `availability_reason` | 稳定原因码，例如 `proxy_disabled`、`protocol_target_missing` 或 `model_reference_ambiguous`。 |
| `protocols` | 当前记录的协议入口与操作。仍须同时满足模型级 `availability`，并按 `operation` 和正式 API 合同构造请求。 |
| `protocols[].availability` | `registered` 表示本地网关操作已登记，`configured` 表示远端目标已登记，`unavailable` 表示目标已 retired；均不表示真实调用成功。 |
| `streaming_support` / `tools_support` | 当前未明确记录时为 `unknown`。未知不等于支持；不能从同一模型的另一个协议推导。 |
| `readiness_state` | 本地准入记录或远端未探测等状态，不代替正式 Runtime 请求时的再次检查。 |
| `proxy_admitted` / `proxy_enabled` | 仅对本地模型有意义，表示网关准入和开关；远端记录中的 `false` 不应解释成远端已禁用。 |

协议里的 `capability_status` 也要按原值理解。比如本地目录推导出的能力可能是 `catalog_only`，表示目录分类而非真实调用验证。查询刻意不返回远端私有来源/目标 ID、Provider URL、自定义上游路径、凭据或证据正文。

浏览目录的用途 taxonomy 与已安装 Runtime 能力是不同证据面。本快照不会把旧安装标签悄悄改名，也不会因为目录新增分类就自动开放新调用操作；已明确同义的标签仅用于匹配当前已有路由。特别是 `multimodal` 不单独证明支持图像输入，只有明确的 `vision` 标签才会声明 `image/*` 输入。

当前远端协议记录不包含用途声明，所以远端条目的 `purposes` 为空、`purpose_evidence` 为 `unknown`；不能根据 `openai_chat`、Provider 模型名或模型 ID 猜它适合什么任务。

`input_media_types` 和 `output_media_types` 描述模型内容类型，不是 HTTP `Content-Type`。请求 JSON 结构、必填字段和协议转换细节以 [14 · 帮助与 API 文档](14-help-api.md) 中对应 API 合同为准。

下面只展示 `data` 的结构示意，不是某台机器的实测结果：

```json
{
  "schema_version": 1,
  "instance_scope": "standalone_cli",
  "snapshot_at_epoch_ms": 0,
  "models": [
    {
      "model_id": "local/<catalog-slug>",
      "source_kind": "local",
      "purposes": ["chat"],
      "purpose_evidence": "installation_metadata",
      "availability": "configured",
      "availability_reason": "proxy_enabled",
      "protocols": [
        {
          "surface": "openai_chat",
          "capability_status": "catalog_only",
          "passthrough_status": "not_applicable",
          "lifecycle": "not_applicable",
          "transport_kind": "http_unary",
          "operation": "POST /v1/chat/completions",
          "input_media_types": ["text/plain"],
          "output_media_types": ["text/plain"],
          "streaming_support": "unknown",
          "tools_support": "unknown",
          "availability": "registered"
        }
      ],
      "readiness_state": "admission_recorded",
      "readiness_reason_code": "proxy_admission_recorded",
      "proxy_admitted": true,
      "proxy_enabled": true
    }
  ]
}
```

若 `models` 为空，表示这份实例当前没有可列出的模型记录。不要自动下载、安装、启用模型或转向云端；告诉用户当前没有符合条件的候选，并等待下一步授权。

## Agent 的使用顺序

1. 确认用户要求的用途、数据边界和云端/费用授权。
2. 查询当前实例，并验证 `data.schema_version` 与 `instance_scope`。
3. 排除 `ambiguous` 和模型级 `unavailable`；再确认模型用途、协议 surface、operation 及协议级状态都与任务相符。`catalog_only` 只证明目录分类，不能声称该模型此前运行成功。
4. 使用用户已经配置好的网关 endpoint 与凭据，经正式协议和请求合同发起调用。只有用户请求及授权覆盖该操作时才执行；能力查询不会提供或创建认证凭据，也不会自动改第三方客户端配置。
5. 检查实际响应和错误。显式的模型不存在/禁用等失败可刷新一次快照；若超时或连接断开使请求是否执行未知，不要自动重放可能计费的调用。请求字段与协议差异见 [14 · 帮助与 API 文档](14-help-api.md)。

运行时会在正式请求时重新验证准入。快照可能在查询与调用之间过期，所以 `configured` 不是成功承诺。静态命令帮助可通过 `omniproxy gateway capabilities --help` 查看；不要用 `init --capabilities` 替代，它只用于首次设置时建议翻译模型。
