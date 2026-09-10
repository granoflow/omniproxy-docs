# 05 · 本地模型管理

「本地模型」页按 catalog 槽位管理本机模型：浏览验签目录、下载、健康测试、删除。翻译、脱敏复核等功能分别选择自己的模型。获取中的下载出现在同一列表，没有独立作业页。Desktop 和 standalone CLI 调用同一 application 规则；standalone 不提供公开管理 API，管理命令直接调用共享能力。

例如，你下载一个准备对话的模型，先确认文件身份与下载结果，再执行对话测试。列表中有文件、被标为可用能力和一次真实调用成功，是三个不同的判断。

## 验签模型目录

Runtime 只接受随发行物提供并通过 Ed25519 验证的目录。每个条目固定仓库、40 位不可变 revision、许可文本、文件路径、字节数与 SHA-256。签名错误、未知字段、不安全路径、重复路径或不完整元数据会拒绝整个目录，不能降级成未验证下载。

当前签名目录里的对话基座是 Instruct，不是 pretrained。发行物 `assets/model-catalog/manifest.json` 的生产条目以 `gemma-4-e2b-it-4bit`（`mlx-community/gemma-4-e2b-it-4bit`）等 IT / QAT IT 为准；它们带 `chat`，用户可选安装，不是安装、脱敏或发布前验收的必需项。固定 revision、许可、文件路径、字节数与 SHA-256 以该 manifest 为准，构建时必须重新核对。

`gemma-4-e2b-mxfp4`（`mlx-community/gemma-4-e2b-mxfp4`）是 Gemma 4 E2B 的 pretrained / base。Hub 常见 `any-to-any`、没有 `conversational`，因此不会自动获得聊天能力、标准对话调试器或默认模型资格。它初始位于「仅下载」，但可以用通用 JSON 接口调试器人工尝试；即使用户随后准入代理，也不会因此变成已确认聊天模型。不要把它和 4-bit / QAT Instruct 混成「同一个可测基座」。

这些是目录元数据事实；M3/M8 的自动化门禁使用小型已签名 fixture 验证下载、失败、恢复和校验流程，不把 fixture 冒充真实模型 smoke。已有真实模型资产只复用并校验，不因测试删除或重新下载。设备没有本地模型时，OmniProxy 仍可使用远程或用户自管来源；脱敏继续使用确定性 PII，Gemma 复核显示不可用并降级。真实 MLX 生成仅在用户已经安装**可服务对话**模型时作为可选证据。

验签事实在下载确认框里核对。`models.search` 检索 Hugging Face 上声明 `library=mlx` 的仓库；与发行物验签目录同一仓库时，界面与下载仍使用目录里固定的 revision 与 SHA-256。Hub 独有条目在下载时按 Hub 文件清单解析，有 LFS SHA-256 的按哈希校验。M5 的自有网络搜索增强与 M7 的 AI 帮助不得覆盖这些身份事实。

## 槽位、下载、恢复与删除

每个签名 catalog 条目在本机是一个槽位。`models list` 按 `catalog_id` 列出就绪与未就绪行；同一 catalog 不会出现两条下载。每个槽位都有「打开介绍」图标，用系统浏览器打开该仓库的 Hugging Face 模型页。

`models pull <catalog-id>` 先创建 resumable Shared 作业，在 `models/.staging/<owner>` 下载，并写带 SHA-256 的 `progress.json` 与夹内租约。每个文件完成后保存已验证字节。全部文件通过大小和 SHA-256 后，才写入该目录的 `omniproxy-model.json`、原子移动到最终位置，并将槽位标为 `ready`。下载进度和失败状态不写入这份 JSON，也不写入 `models/omniproxy-models.json`。换机或清空 Internal State 后，对同一夹再次 `pull` 会按 sidecar 与分片续传，不复活另一发行物的 `job_id`。半写 manifest、越界符号链接、外部删除、替换或移动会在使用前 reconcile，不能把 Private SQLite 的旧记录当作公共文件事实。

关闭页面不会取消下载。暂停只停止传输并保留分片。删除未完成的槽位必须显式确认：运行中先进入 `cancelling`，再到安全点清除 staging 与可见作业；再次 `pull` 从零开始。`jobs retry` 从原 checkpoint 继续，并新建 attempt；旧记录不再出现在默认列表。Runtime 重启会把可恢复 attempt 重新排队。

删除就绪模型必须显式确认；仍被占用、存在推理租约或不属于受管根目录的资产会被拒绝。清理过期作业档案不会删除 ready 模型。

## 健康测试与调用测试

每个就绪行都有一个调试入口。已确认能力使用专属界面：对话默认显示对话结果并在流式时逐步追加；向量显示数值并可比较相似度；ASR/OCR 显示文字或 Markdown；TTS 显示播放器；生图显示图片。所有界面都可切换到同一次调用的 JSON。对话界面还可选择文字、图片、音频和视频输入；不支持或尚未确认的选项默认禁用，悬停可看原因，也可以直接启用后真实尝试。

「仅下载」不是永久放弃代理，而是当前安装还没有获得用户准入。它使用通用 JSON 接口调试器，可选择已登记入口和结果类型，错误或服务端忽略字段都照实显示。HTTP 2xx 也会提醒你检查内容；没有网关响应会显示风险提示，但你仍可坚持加入代理。加入后原因与用途标签保留，今后仍打开通用调试器。关闭代理只停用路由，不移动模型，也不会回到仅下载；只有删除并重新下载才重新开始准入。

“保存调试 JSON”只为下次调试保留最后一份请求，不会改变代理参数或模型能力。代理始终按 OmniProxy 的固定透传合同工作；本地 Authorization/API key 由 Runtime 读取，无需写进 JSON。对话模型的演示 JSON 带 `max_tokens: 32`；网络搜索使用独立入口，不通过对话开关触发。安装目录 UUID 只作内部句柄和兼容别名；用户可见模型名使用 `local/<catalog_slug>`。

向量模型打开向量测试：预填文本、可选第二段（默认关）和可编辑 OpenAI embeddings JSON，默认 768 维。运行后请求进入当前网关 `POST /v1/embeddings`，默认显示向量值与总维度；开启对比时显示余弦相似度，也可切换到完整 JSON。打开弹窗不会自动发送。

翻译模型的播放走与工作台相同的 `omniproxy translate run`：短句 + 当前翻译配置的语言/引擎，不走 `models test`，也不用对话 generate 冒充翻译。不安装或调用 Ollama；没有本地模型不影响远程来源。

各功能使用自己的模型选择，不存在统一替所有任务决定来源的默认对话模型。检查对应功能的选择与实际执行结果；不要假定一个模型不可用时一定会自动换成另一个。

| 状态 | 需要确认什么 |
|------|--------------|
| 下载完成 | 文件是否完整并通过校验 |
| 能力已识别 | 是否支持你要使用的入口或输入类型 |
| 调用测试成功 | 本次实际内容和结果是否符合预期 |
| 模型被占用 | 先处理引用或正在运行的任务，不手工删除受管目录 |

## CLI

```bash
omniproxy models list
omniproxy models search gemma --tag chat
omniproxy models pull gemma-4-e2b-it-4bit
omniproxy models remove gemma-4-e2b-it-4bit --yes
omniproxy jobs watch <job-id>
omniproxy jobs retry <job-id>
omniproxy models test <installation-id>
omniproxy models probe-chat --body '{"model":"local/<catalog-id>","messages":[{"role":"user","content":"hi"}]}'
omniproxy models probe-embedding --body '{"model":"local/<catalog-id>","input":"hello"}'
omniproxy translate run --input OK
```

`models remove` 接受 catalog 槽位；若 `installation_id` 仍能唯一对应就绪槽位，也可使用。`jobs watch` 先输出 snapshot，变化时输出 changed，终态输出 terminal；按 Ctrl-C 只停止观察，不取消也不删除。默认 `jobs list` 对同一 catalog 的模型下载只显示当前可见 attempt。`models default get/set` 已退出公开合同，调用返回 `unknown_operation`。每个功能保留自己的模型选择。

下一章：[06 · 连接外部模型](06-external-models.md)
