# 17 · 工具

「工具」页列出一组可以接到 OmniProxy 网关的第三方 AI 软件。OmniProxy **不安装、不卸载、不启动、不修改、不托管、不分发**它们，只提供固定推荐、只读检测、官方官网入口和手工配置说明。

页面名称是 **工具（Tools）**。它不是 Marketplace、插件商店或软件仓库。

## 分组

### 创作与对话

- **Open WebUI**：通用 AI Chat Web UI，可连接本地模型和 OpenAI-compatible API。
- **ComfyUI**：节点式生成式 AI 工作流，主要用于图像和视频。

### 智能体

- **Hermes**：功能完整的通用 AI Agent Runtime。
- **goose**：通用 AI Agent，可做开发、研究和自动化。
- **OpenClaw**：个人 AI 助手和 Agent Runtime。

### 开发者

- **Pi**：轻量 Agent Harness，适合自己搭 Agent。
- **Aider**：终端里的 AI 编程 Agent。

首版只包含以上 7 个。不会继续做成 AI 软件目录。

## 卡片上能做什么

每张卡片显示名称、一句话说明和状态：

| 状态 | 含义 | 动作 |
|------|------|------|
| 已安装 | 受支持的探测找到高置信安装证据 | 显示“已安装”；打开官网；查看配置说明 |
| 运行中 | 固定 loopback 服务或官方状态证据可用 | 显示“运行中”；打开官网；查看配置说明 |
| 无安装证据 | 本轮受支持的探测没有找到证据 | 不显示状态文案；仍可打开官网或查看配置说明 |
| 检测受限 | 权限或运行环境阻止了至少一项探测 | 不显示状态文案；仍可打开官网或查看配置说明 |

官网入口始终显示。检测失败不会隐藏固定目录；没有安装证据或检测受限时，卡片保持无状态文案。OmniProxy 不扫描任意目录，不调用包管理器、第三方命令或 Terminal。

## 配置说明

点击卡片上的“配置说明”会打开只读说明，按工具展示：

- 当前 OmniProxy Base URL：`http://127.0.0.1:<端口>/v1`；
- 模型列表地址：`http://127.0.0.1:<端口>/v1/models`；
- API Key 应从「设置 › 网关」查看或复制；
- 工具官方支持的配置入口和模型 ID 填写方式。

Base URL 与模型列表地址可以复制。说明页不会显示真实 API Key，也不会修改第三方配置、环境变量、Keychain 或数据库。

Open WebUI、Hermes、goose、OpenClaw、Pi 和 Aider 分别按其官方 OpenAI-compatible 配置方式说明。Aider 使用的 Python/venv 属于 Aider 自身环境，需由用户在 OmniProxy 外安装。ComfyUI 当前没有通用 OpenAI-compatible 接入方式，因此只显示现状说明和官网，不生成虚假配置步骤。

## CLI

图形界面与命令行共用同一套规则：

```bash
omniproxy tools list
omniproxy tools status aider
omniproxy tools open aider
omniproxy tools guide aider
```

## 这页不负责什么

- 不安装、卸载、启动、升级、清缓存或替第三方删依赖。
- 不自动写入第三方设置或保存第三方凭据。
- 不管理 ComfyUI 工作流或 Agent 会话。
- 不把这些工具的功能搬进 OmniProxy。

下一章：[18 · Agent 能力发现](18-agent-capability-discovery.md)
