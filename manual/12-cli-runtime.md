# CLI 与运行实例

CLI 是在终端运行的 `omniproxy` 命令。它可以用于查询、脚本和 AI 自动操作；不要求你通过另一个管理 HTTP 服务配置产品。

## 先确认用的是哪一份程序

```sh
command -v omniproxy
omniproxy --version
omniproxy --help
```

检查输出路径与安装版本。桌面 App 内的 Helper 用于 App 自己启动 Runtime，不能直接复制或链接出来当作独立 CLI。独立 CLI 与 App 有各自的数据边界，不能因为在同一台 Mac 就认为两者配置、来源和记录相同。本章的命令操作独立 CLI，不提供把 `--data-dir` 指向 App 私有资料库、借此管理 App 的做法。需要调整当前 App 时，使用 App 自己的对应页面。

## 找不到命令时

先用独立 CLI 安装目录中的完整程序路径运行 `--version`，路径有空格要加引号。需要从任意目录使用时，把你自己的安装目录加入用户 PATH，或使用自己可核对的符号链接；不要覆盖不认识的同名命令。桌面 Agent 未必读取终端的 shell 配置，可以明确设置独立 CLI 的绝对路径。

移动原程序后检查快捷方式是否失效。不要根据旧教程猜 `path install` 等命令，以当前 `--help` 为准。

## 查找命令与结果

```sh
omniproxy sources --help
omniproxy models --help
omniproxy config --help
omniproxy gateway --help
```

| 命令组 | 常见用途 |
| --- | --- |
| `models`、`sources` | 本地模型与外部来源 |
| `mappings`、`auto` | 模型映射与自动匹配 |
| `gateway`、`service`、`doctor` | 网关、服务与诊断 |
| `config` | 查询和保存配置 |
| `retrieval`、`search` | 来源管理与搜索 |
| `glossary`、`translate`、`redaction` | 词表、翻译和脱敏 |
| `logs`、`stats`、`jobs` | 调用、用量和任务 |

某命令在帮助中出现，不代表这个安装包的所有操作都已可用。返回 `capability_not_ready` 时，应按当前发行物限制处理，不把它当成成功。

## 可复制的设置示例

先查询原值，再修改，再读回：

```sh
omniproxy config get ui.appearance --output json
omniproxy config set ui.appearance dark --output json
omniproxy config get ui.appearance --output json
```

JSON 先检查 `ok`，再读取 `data`；失败看 `error`。`--output jsonl` 适合支持该格式的逐行输出。`--dry-run` 是预演，不会证明操作已经真正发生。`--yes` 是确认有副作用的操作，不能作为排错时随手加上的通用参数。

需要选择独立 CLI 数据目录时，先记录所用程序的完整路径与目录；每一条命令都使用同一程序和相同的 `--data-dir` 参数。没有指定时使用该发行物默认目录；不要一条指定、一条省略，再拿两个结果比较。例如对你已准备的 CLI 专用目录执行 `omniproxy --data-dir "/你自己的CLI数据目录" config get ui.appearance --output json`，把示例目录替换成实际路径。不要指向 App 私有资料库或拿工作数据试验删除。

`service` 命令管理设备上的默认独立 CLI 服务，不接受 `--data-dir`。需要检查默认服务时使用 `omniproxy service status --output json`，不能加一个自定义目录就以为查看的是那个目录的服务。`--lang` 控制帮助和人类可读输出，不改变结构化字段名。

## 终端交互管理台

提供 TUI 的独立 CLI 版本可在交互式终端运行 `omniproxy tui`；先以 `omniproxy tui --help` 核对是否包含。它用于监控、模型、来源、映射、隐私工具和设置；不支持 TUI 的安装包应使用普通命令或桌面版。

| 按键 | 用途 |
| --- | --- |
| `1`–`6` | 切换区域 |
| `Tab` / `Shift-Tab` | 移动页面或表单焦点 |
| `↑` / `↓`、`Enter` | 选择并打开对象 |
| `e` / `a` | 当前页面支持时编辑 / 添加 |
| `/`、`r` | 筛选、刷新 |
| `Ctrl-S` | 保存表单 |
| `Esc` | 返回或取消；未保存内容先确认是否放弃 |
| `?`、`q` | 帮助、退出界面 |

关闭 TUI 不会自动停止服务；取消凭据编辑保留原值，只有明确清除动作才删除凭据。TUI 需要可交互终端，不能与 JSON/JSONL 或 `--dry-run` 混用。设置区的 `s`、`x`、`t`、`e` 分别用于启动、停止、自启动切换和设置编辑，以当前页面提示为准。

TUI 保存后可退出界面，用同一独立 CLI 和相同数据目录执行 `omniproxy config get ui.appearance --output json` 读回外观；其他设置换成实际修改的键。检查默认服务启停，用 `omniproxy service status --output json`，读取返回的实际状态和错误，不能只因按过 `s` 或 `x` 就认定成功。该服务查询不接受 `--data-dir`，不要拿它判断一个自定义目录的实例，更不能据此判断桌面 App 已停止。

## 启动与停止

先查看 `omniproxy service --help` 和 `omniproxy doctor --help`，再按当前安装包提供的入口操作。确认目标实例及监听端口，不因为一个端口返回正常就认定它属于当前 CLI。

需要 AI 自动执行时，使用[先查询、限定修改、读回验证](18-agent-capability-discovery.md)的流程。不要把 CLI 帮助、预演或静态能力快照当成真实模型调用成功。
