# v3.0 发布验收报告 · 2026-10-12

## 已执行且通过的检查

- **静态完整性：** `python3 scripts/check_content.py`；检查本地链接、HTML、SVG、封面尺寸、12 个主体 Prompt、15 个模板、23 章完整教程与 24 条练习数据。
- **训练评分单元测试：** `python3 -m unittest discover -s tests -v`，共 4 项通过（示例 4 处错误、非法分类标签、重复 ID、漏 ID 与多 ID）。
- **评分演示：** `python3 scripts/grade_feedback.py labs/sample-predictions-not-a-model-result.csv`，返回 20/24 和 4 处预期错误；此数据为**人为编造的教学输出，不是 AI 真实成绩**。
- **浏览器交互：** Chromium 390px 手机宽度下，7 天打卡勾选与清空、24 条评分与清空按钮通过测试，无脚本报错。
- **浏览器排版：** 首页、23 章文章、评分页、零基础入口、失业现金流、来源和审稿报告的 390px 全页宽度检测均无整体溢出；大表格改为内部可横向滑动。
- **桌面排版：** 1350px 首页无横向溢出。
- **图片：** 首页封面与正文 8 张 SVG 已内嵌于可独立打开的 HTML，素材文件仍在 `assets/` 可编辑。

## 尚未声称通过的部分

- 由于测试环境禁止访问自建测试站点地址，**无法在正常站点源上完成刷新/跨会话的 LocalStorage 持久化测试**；已验证同页打卡更新与清空。上线 GitHub Pages 后须继续验证。
- 还未实际创建或更新 GitHub 线上仓库，无法声称 GitHub Actions 已在线成功执行。
- 还未获得真实职场用户、企业安全负责人或外部同行的独立审阅。对抗式审核是项目内部自查。
- 原有七类职业示范和 24 条评分数据均为教学虚构素材。v3 新增的六个企业与研究案例来自可核查公开出处，但不等于本项目或读者自身的工作业绩，也不代表任何岗位的普遍效果。

## 复核命令

```bash
python3 scripts/check_content.py
python3 -m unittest discover -s tests -v
python3 scripts/grade_feedback.py labs/sample-predictions-not-a-model-result.csv
```

本报告与 [对抗式审核](docs/ADVERSARIAL_AUDIT.md) 一起公开，发现问题欢迎提供可复现步骤。

## v3.0 政策、真实案例与证据复核

- 三份新附录与 HTML 同步：`docs/19-policy-and-opportunities`、`20-real-world-cases`、`21-why-change`。
- 主文第一章已直接加入政策和实验研究；失业与质量评估章节加入可执行规则。
- 政策与案例的原文链接附在正文、附录和 SOURCES；不能把政策目标、公司自述、研究测量混成同一类证据。
- 额外三份模板：政策资格、案例反向核查、招聘 JD 证据表。
- 需要继续人工检查：官方网址的后续迁移、各地政策名额和读者个人适用性；本地工具无法作出个人审批结论。

- **v3 手机兼容性复核：** 首页、完整图文、政策、六个企业案例、原因分析、政策模板和评分实验页，390px 宽度均无整页横向溢出。新增长表格已修改为容器内水平滚动；页面内 JS 无报错。
- **v3 自动化检查：** 原有 4 个单元测试及本地路径/图片校验通过；首页与实验评分器 JavaScript 通过 Node 语法解析。
- **仍待线上验证：** GitHub Pages 原站的跨刷新 LocalStorage、外部官方网站未来有效性、具体地区实时补贴与个人申领结果。
