# GitHub 发布与维护

目标仓库：[AIPMAndy/ai-era-survival-guide](https://github.com/AIPMAndy/ai-era-survival-guide)；在线入口：[https://aipmandy.github.io/ai-era-survival-guide/](https://aipmandy.github.io/ai-era-survival-guide/)。是否已部署以 Actions 与正式网址验收为准。

## 1. 新建仓库

建议名称 `ai-era-survival-guide`，Public，默认分支 `main`。**ZIP 生成不等于仓库已经创建**。不要上传任何真实简历、客户信息、秘钥或敏感工作文件。

## 2. 上传文件

在 GitHub 新建仓库后，将解压目录 `ai-era-survival-guide` 中的**全部内容**放在仓库根目录（包括隐藏的 `.github`），而不是再嵌套一层目录。建议一次性提交并填写具体变更说明。

## 3. 部署 GitHub Pages

仓库 `Settings → Pages → Build and deployment → Deploy from a branch → main → /(root) → Save`。等待部署完成，访问系统给出的 URL。首次启用可能需要等待；以 GitHub UI 实际状态为准。

## 4. 发布验收

- `index.html` 首页及按身份选择功能。
- `article.html` 23 章正文与 8 张 SVG。
- `lab.html` 载入错误演示 → 得到 `20/24`，清空按钮有用。
- 手机 390px 宽度无明显横向溢出。
- 七天打卡的保存、刷新、清空，在**同一站点浏览器**内能工作。
- `docs/START-HERE.html` 和 `docs/ADVERSARIAL_AUDIT.html` 可在网页阅读。
- 对外发布时需要另查当前平台的 AI 内容标识与版权规则。

本地检查：

```bash
python3 scripts/check_content.py
python3 -m unittest discover -s tests -v
python3 scripts/grade_feedback.py labs/sample-predictions-not-a-model-result.csv
```

若静态页可以打开但浏览器未保存打卡，检查是否处于隐私模式、是否禁止浏览器本地存储。数据只保存本机，不跨设备同步。
