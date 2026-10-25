# 让 AI 工具帮你操作 OmniProxy

具备命令执行能力的 AI 工具可以运行 OmniProxy CLI，替你查询状态或执行明确的设置。普通聊天窗口只有给出建议的能力时，不能因此操作你的电脑。

先使用[独立 CLI](12-cli-runtime.md)，核对 `command -v omniproxy` 和 `omniproxy --version`。不要把 App 内部 Helper 复制出来当独立 CLI；两种发行物也不一定使用同一份设置和记录。

## 先让它查询，不要一开始就改配置

可以把下面这段话交给你的 AI 工具：

> 请先确认 OmniProxy CLI 的路径、版本和目标数据实例。阅读 `omniproxy --help` 和相关子命令帮助，然后查询网关能力与当前外观设置。只查询，不安装模型、不外发内容、不改配置；把查到的结果和不可用项告诉我。

对应的查询命令：

```sh
omniproxy --version
omniproxy gateway capabilities --output json
omniproxy config get ui.appearance --output json
```

能力快照帮助 AI 读到模型、协议和当前可用状态，不会替它完成一次真实模型测试。模型只有目录信息、未加入代理或状态过期时，AI 不应直接宣布可用。

![独立 CLI 实际返回的设置查询与修改结果](images/zh-CN/automation-cli.png)

图中是隔离实例真实返回的阅读视图，展示设置相关字段，不是终端应用截图。命令返回的 `ok` 和 `data.value` 用于判断结果，不能只看 AI 说“已完成”。

## 执行一个可以撤销的小设置

先记下当前 `ui.appearance` 值。可以向 AI 发出更具体的任务：

> 将刚才确认的 OmniProxy 实例外观改为深色。先核对 `config set` 的帮助，执行后重新读取设置。不要操作另一份 App 数据，不修改模型来源或凭据；告诉我恢复原值的命令。

实际命令为：

```sh
omniproxy config set ui.appearance dark --output json
omniproxy config get ui.appearance --output json
```

第一次返回保存结果，第二次应读到 `data.value` 为 `dark`。如果原值是 `system`，用下面命令恢复：

```sh
omniproxy config set ui.appearance system --output json
```

这是独立 CLI 实例的设置示例，不用于改变当前 App。要求 AI 在报告中写明程序完整路径、版本、是否使用 `--data-dir` 及其值；读、写、恢复始终使用同一组参数。当前 App 的设置到 App 内操作，不把 App 私有资料库填进独立 CLI。恢复值应使用你第一次读到的值；只有原值确实为 `system` 时，才照抄上面的恢复命令。

## 让任务边界足够清楚

“帮我优化一下”没有说明能改什么。改成具体对象和结果，例如：“列出当前来源，找出哪个没有验证，先向我报告，不替换密钥、不发送测试生成请求。”

下载、模型调用、搜索、删除和凭据修改可能有磁盘、费用、外发或数据后果。把允许执行的动作说清楚，要求 AI 操作前读取当前状态，操作后核对结果，并在失败时停止依赖步骤。

## 检查结果和错误

结构化输出先读 `ok`；成功再读取 `data`，失败读取 `error.code` 和提示。`--dry-run` 只是预览可能动作，不代表已执行或已连接服务。

若返回 `capability_not_ready`、命令不存在或当前发行物不支持，先核对版本与帮助，不让 AI 编造替代命令。已经成功的查询也不能证明其他子命令都可用。可复制的 CLI 参考见[命令行](12-cli-runtime.md)，网关模型入口见[用途映射](model-mapping.md)。
