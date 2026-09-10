# 06 · 连接外部模型

连接外部模型时，先区分服务地址、认证和模型名称。保存连接配置之后还需要验证目录，再检查一次真实调用；能列出模型不等于每种能力都已测试。OmniProxy 提供兼容入口并将请求转交给你配置的来源。Ollama 可以运行在另一台电脑，也可以由用户自行安装在本机；它不是 OmniProxy 的内置依赖。

例如，两份订阅都提供同名模型时，可以用 `deployment/model` 明确指定来源，避免把裸模型名称误当成唯一身份。

## 接入语义

| 类型 | 文案 | 行为 |
|------|------|------|
| 本地模型 | `（本地模型 · OpenAI 协议由 OmniProxy 本地推理引擎应答）` | 本机推理，数据不出机 |
| 透明代理 | `（外部来源 · 透明代理 · 按厂商原生协议调用）` | 字节级原样转发到厂商 |
| 协议转译 | `（外部来源 · OmniProxy 把 OpenAI 协议转译到厂商原生协议）` | 你发 OpenAI 格式，OmniProxy 翻译成厂商格式 |

## 默认识别与显式适配器

- 填「名称 / 网址 / 密钥」后默认自动识别；高级设置也可以显式选择适配器。
- `adapter` 支持 `auto / openai_compatible / anthropic / gemini / ollama`。任意主机使用标准端口 `11434` 时，`auto` 会识别为 Ollama；自定义端口必须显式选 Ollama，CLI 对应 `--adapter ollama`。
- OmniProxy 只调用用户配置的 Ollama HTTP API，不安装、启动、升级或停止 Ollama。OmniProxy 自带本地模型仍由 Runtime 的本地推理引擎加载，两条路径互不依赖。
- 连接时自动探测鉴权：`已自动适配：{scheme}（OpenAI 兼容，概率最高）· 已获取 3 个模型`。
- 未识别源：`未识别源 · 连接时自动探测` 或 `未识别源 · 请填网址`。
- 免密钥源（如 Ollama）可留空：`（Ollama 可留空）/（此源免密钥，可留空）`。

## 五入口 API

API 接入页（`API 接入 api.card_title`）提供五个协议家族。OpenAI 家族同时包含 Chat Completions 与 Responses 两个端点：

| 入口家族 | 本地端点 | 处理方式 |
|---------|----------|----------|
| OpenAI（api.tab_chat / api.tab_responses） | `POST /v1/chat/completions`、`POST /v1/responses` | 归一化后转译 |
| Anthropic Messages | `POST /v1/messages` | 归一化后转译 |
| Gemini | `POST /v1beta/models/{model}:generateContent` 或 `:streamGenerateContent` | 归一化后转译 |
| Ollama Chat | `POST /api/chat` | 归一化后转译 |
| 原生任意透传 | `ANY /v1/raw/{deployment}/{upstream_path}` | 精确选择 deployment 后保真转发 |

- **四个归一化家族**：支持文本、system/developer、工具调用/结果和共同生成参数。不能无损转译的厂商字段不会静默丢失；响应的 `omniproxy.warnings[]` 会给出 `field_not_translated`。需要保留厂商独占字段时改用 raw。
- **来源参数别名**：只挂在该外部来源上，由用户自填「别名 → 参数名」。归一化出站时把 extras 袋里命中的 key 改名为该来源的参数名；`local/` 与 raw 不合并别名。参数别名不会触发 OmniProxy 自动网络搜索。同一请求里别名与参数名都在且值不同会失败，不静默选边。产品不预填厂商参数表。
- **原生任意透传（raw）**：保留方法、上游路径、查询、正文、非 hop-by-hop headers，以及上游响应状态和正文。OmniProxy 仍执行精确 deployment 路由和上游凭据注入，但不探测、不回退到其他来源，也不默认注入搜索或附件内容。
- **流式格式**：OpenAI、Anthropic、Gemini 使用各自 SSE 事件；Ollama 使用 NDJSON。客户端断开后 Runtime 会停止继续读取上游流。
- **上游错误**：鉴权、权限、余额、限流、不可达、无效响应和取消会映射成当前入口协议的错误对象，并附带稳定的 `omniproxy.code`、可获得的上游状态和可排障文本；raw 的上游 `4xx/5xx` 状态和正文保持原样。

- 完整协议细节与示例见 [14 · 帮助与 API 文档](14-help-api.md) 与 [15 · 核心概念](15-concepts.md)。

## 命名空间与路由

- 同一模型多订阅时用 `命名空间（field_namespace）` 区分（如 `openai / deepseek`）。
- qualified 名称 `deployment/model` 永远只发送给指定来源，不探测、不改投。
- 裸模型名只有一个可用候选时直接调用；没有候选时失败，多个候选时返回歧义，不暗中选一个来源。需要明确来源时使用 `deployment/model`。
- 当前不提供首选星标或 `sources preferred` 操作，也不把用户请求广播给多个来源来选择结果。
- 流式请求只在尚未向客户端发出任何事件时自动重试；已经输出部分内容后不会重放，以免产生重复文本。

## 连通验证

- 新增、从停用状态重新启用、显式执行 `sources test` 与 `sources refresh-models` 都使用该来源凭据读取非空模型目录。首版不探测模型类型，也不发送 `hello`、token 请求或任何生成请求；目录读取成功即代表连接、鉴权和目录验证通过。
- 目录读取失败保留来源配置和凭据，但标记为未验证、不可路由；目录读取的真正上游失败可按 adapter 的既有重试规则重试一次。OmniProxy 的联网能力统一来自用户配置的检索来源。
- 认证、权限、余额、限流、不可达和无效响应使用不同稳定错误码；错误、作业输入和诊断输出都不包含密钥或上游响应正文。

```bash
omniproxy sources update <source_id> --parameter-aliases-json \
  '[{"alias":"web_search","parameter":"enable_search"}]'
```

M3 使用本地受控 provider 替身验证目录刷新、错误分类、重试和密钥 canary；真实外部 adapter smoke 留到 M8 发布准备闭环。证据只允许记录来源类型、模型、数量、延迟与结果，不保存凭据、prompt 或响应正文。

下一章：[07 · 模型参数与量化](07-params-quantization.md)
