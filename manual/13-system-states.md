# 13 · 运行时系统状态

服务可达、模型可用和一次调用成功是不同状态。先确认当前运行实例和连接，再查看具体错误；不要因为看到旧诊断文件就认定服务仍在运行。

例如，HTTP 网关可以访问但某条管理命令失败时，应检查该命令要求的本机管理连接，而不是直接删除数据目录。

## 诊断维度

| 维度 | 状态 | 含义 |
|------|------|------|
| 托盘（tray） | `wf.state.tray` | 菜单栏图标是否在线 |
| 活动请求 | `wf.state.active-request` | 当前是否有在途请求 |
| 锁 · 使用中 | `wf.state.live-lock` | 正在被某进程持有的锁 |
| 诊断 · 陈旧 | `wf.state.stale-diagnostic` | 旧进程留下的诊断记录；不代表仍被占用，也不需要手工删除 |
| 端口冲突 | `wf.state.port-conflict` | 端口被占用，需换端口（引导里 1024–65535） |
| 双栈切换失败 | `port_conflict` / `listener_unavailable` | 新 IPv4/IPv6 候选未完整建立；旧监听器和旧配置继续有效 |
| 地址已回退 | `endpoint_fallback` | 上次选择的网卡或地址已消失，地址栏就地改为当前推荐 endpoint；不常驻提示条，辅助技术播报一次 |
| 数据版本较新 | `wf.state.schema-newer` | 数据格式比当前程序新，可能需升级/迁移 |
| 来源目录验证失败 | `source_directory_failed:<code>` | 认证后的模型目录为空或读取失败；来源配置保留，按认证、权限、额度、限流、网络或响应格式检查 |
| 外部检索响应无效 | `invalid_response` | 字段缺失、URL 非 HTTP(S) 或 JSON 不符合合同；公开搜索零命中不等于格式无效 |
| 账本正文已过期 | `body_state=expired` | 请求/响应正文已按 TTL 清空；安全元数据墓碑仍可用于排障和统计核对 |
| 日志容量报警 | `warning_active=true` | 当日新增账本正文达到配置阈值；可清理日志或调整保留策略 |
| 答案缓存失效 | cache miss | 密文篡改、密钥不可用、解密失败或 TTL 到期；Runtime 安全删除并重新请求，不返回损坏内容 |
| 发行物冲突 | `runtime_conflict` + `conflict_kind=gateway_held_by_other` | 另一发行物已在监听网关；当前入口不得再常驻，也不连接或接管对方。只读 / one-shot 不因此失败 |
| 本侧常驻不可达 | `runtime_conflict` + `conflict_kind=resident_helper_unreachable` | 同 bundle PATH 客户端连不上已在听的 helper；禁止降级 one-shot |
| 公共资产写入冲突 | `asset_write_busy` | 模型目录内活租约（下载等写入）；立刻失败，不排队 |
| 能力不可用 | `capability_unavailable` | 当前封装不提供该操作；例如 App 随附 CLI 不提供 standalone 的 service 生命周期 |

## 作业状态与重启恢复

macOS 菜单栏图标使用系统原生菜单。菜单顶层显示网关状态、打开、复制 API 地址、最近调用和退出；最近调用子菜单最多显示五条调用方、结果与相对时间，详细模型、token、错误和正文仍只在主界面查看。菜单在每次展开时刷新，新调用不要求在已经展开的菜单中实时跳动。图标在 AppKit 中处于可见状态但屏幕上找不到时，先检查菜单栏空间、刘海和第三方菜单栏管理工具；不要反复重启或删除用户设置。

系统状态页可以从 JobService 汇总当前 Runtime 可见的 Shared/Private 作业，但不读取 CLI stdout。`queued` 表示等待 worker claim，`running` 表示已有 attempt，`cancelling` 表示已收到取消请求、正在等待安全点，终态为 `succeeded`、`failed` 或 `cancelled`。如果界面仍显示 `cancelling`，先等待当前网络或文件系统调用返回，不要删除锁或 staging 文件。

模型恢复时会检查当前存储位置和文件完整性：模型在完整 manifest 与 hash 校验前显示 `verifying`，不能路由；验证完成后才成为 `ready`。这不会绕过校验，也不会把目录存在误当成可用模型。随后处理上次中断的 attempt：resumable 作业保留 checkpoint 并回到 `queued`；不可恢复作业写入 `runtime_interrupted`；无效的 Private 作业输入写入 `invalid_job_input`，但不会阻止其他功能启动。终态记录保留 30 天后安全清理，Asset Catalog State 和当前发行物 Private 数据分别清理，不跨发行物读取或删除。

同一启动恢复阶段还会清理过期缓存、把到期账本正文转为墓碑、删除到期墓碑，并执行容量上限。任何清理都只作用于当前发行物 Private State，不清除独立日统计。

## 排查顺序建议

1. **托盘或 CLI 服务 是否已在听端口？** 桌面未开时，免费 CLI 命令仍可单独执行；要当网关再 `omniproxy service start`（见 [12 · CLI 与运行时](12-cli-runtime.md)）。另一发行物已在听则先退出对方。
2. **端口冲突？** App helper 会保留旧端口；换一个 1024–65535 的端口重试。standalone 一次性设置显示 `next_runtime_start` 时，下次启动 `serve` 生效。
3. **陈旧诊断？** 直接重试。OmniProxy 在取得内核锁后会自动重写诊断记录，不要手工删除模型或应用状态文件。
4. **数据版本较新？** 说明数据由更高版本写入，按提示升级或处理迁移。
5. **作业停在 cancelling？** 等待当前调用到达安全点；若 Runtime 已退出，重启后由恢复流程决定重新排队或标记 `runtime_interrupted`。
6. 仍不通：看 [14 · 帮助与 API 文档](14-help-api.md) 的健康检查与故障排查，或查看当前页面的「?」说明。


来源探测摘要只保存在当前发行物 Private State，不进入用户调用账本或用量统计。它包含来源、模型、结果、错误分类和延迟，不包含 API key、用户正文或上游正文。

`status`/`doctor` 应同时核对 Home ID、schema、活动 Runtime 的发行物和 PID。macOS/Linux 两种发行物的 socket 名不同，深路径使用短哈希名；Windows 管道名则带稳定 Home ID 和 `cli`/`desktop` 后缀。不要因为发现另一发行物的端点就手工改名或连接它，正确处理是退出对方 Runtime 后再启动当前发行物。

平台回归把三种证据分开：macOS 和 Linux 运行完整 workspace；Windows 在原生 runner 编译生产库/二进制，并启动真实 Runtime 验证 typed 状态调用和已实际应用的当前用户 SID ACL。macOS 上的 Windows 交叉编译不具备 MSVC 系统头文件，因此不能替代 Windows 真机证据。

下一章：[14 · 帮助与 API 文档](14-help-api.md)
