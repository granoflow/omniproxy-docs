# OmniProxy 产品手册

在线阅读：https://granoflow.github.io/omniproxy-docs/

隐私政策：[OmniProxy Privacy Policy（English）](docs/omniproxy-privacy-policy.md)。该政策是独立法律文档，不随手册章节翻译。

`manual/` 是用户手册唯一编辑源。修改 Markdown 和图片，提交到 main 后由 GitHub Actions 构建、检查并发布到 GitHub Pages；HTML 是生成物，不手工编辑或提交。

## 本地预览

维护者需要 Python 3（仅开发工具；产品用户无需安装）。

```sh
python3 tools/build_site.py build _site
python3 tools/check_site.py _site
python3 -m http.server 8000 --directory _site
```

访问 http://localhost:8000/ 。链接保持相对路径，章节改名须修复引用及已发布地址。README 和工具不会进入站点。

## 首次启用发布

在仓库 Settings → Pages 选择 GitHub Actions。部署工作流仅 main 可发布，拉取请求只构建检查。Actions 产物包含本次提交标识，可用于定位文档版本；故障时回退 main 中的文档修改并重新运行部署。

## 内容维护

首页记录适用软件版本。命令以实际发行物 `--help` 为准，未实现能力要明确标注；不发布凭据、个人路径、未脱敏截图或主仓库内部设计资料。源码变更影响用户行为时同步更新本仓库。

本仓库保存用户文档，软件合同和研发设计仍由产品源码仓库维护。
