# YOLO 目标检测教程

**从检测任务与评估协议，到 YOLO 架构演进、训练策略、推理部署与行业实践的 28 章中文教程。**

本仓库面向希望理解目标检测原理并能独立完成模型选型、训练、评估和部署的读者。课程不仅介绍模型结构，也解释每项设计解决了什么问题、引入了哪些约束，以及论文指标应该怎样正确比较。

## 快速开始

课程是静态 HTML，无需安装前端框架、构建工具或在线 CDN。可以直接打开首页：

```bash
open index.html
```

也可以启动本地 HTTP 服务：

```bash
python -m http.server 8000
# 浏览器访问 http://localhost:8000
```

首页提供章节搜索与阶段筛选。每篇文章都是独立页面，包含必要的背景、概念定义、结构解释、公式或代码、适用边界与参考来源。无需先读完前文才能理解当前页面。

## 课程路线

| 阶段 | 章节 | 学习主题 |
|---|---:|---|
| 01 · 基础与 YOLOv1–v3 | 01–05 | 目标检测任务、IoU/mAP、单阶段思想、YOLOv1、YOLOv2/9000、YOLOv3 |
| 02 · 检测组件与训练 | 06–14 | YOLOv3 实战、YOLOv4、锚框、损失函数、FPN、数据增强、骨干/Neck/Head、NMS |
| 03 · 现代 YOLO 架构 | 15–18 | YOLOv5、YOLOv8、YOLOv9/v10、YOLO11/v12 |
| 04 · 轻量化与部署 | 19–22 | 剪枝、量化、蒸馏、小目标、ONNX/TensorRT、边缘设备 |
| 05 · 数据、评估与实战 | 23–28 | 标注格式、训练流水线、模型评估、多模态、行业案例、综合项目 |

## 仓库结构

```text
yolo-tutorial/
├── index.html                 # 静态课程首页：搜索、阶段筛选、学习路线
├── courses.json               # 28 章结构化元数据（首页的机器可读目录）
├── chapters/
│   ├── 01.html ... 05.html    # 第一批重构后的独立技术文章
│   └── 06.html ... 28.html    # 其余课程页面
├── assets/
│   ├── theme.css              # 首页与章节共用设计系统
│   └── site.js                # 首页搜索与阶段筛选增强
├── pdfs/                      # 论文原始 PDF 资料
├── docs/
│   ├── architecture.md        # 页面、导航和发布结构说明
│   ├── improvements.md        # 追加式工程改进记录
│   └── evidence/
│       └── chapters-01-05.json # 第一批章节的主张—来源映射
├── tests/
│   ├── test_site.py           # 静态结构、链接、公式和 SVG 检查
│   └── browser_check.py       # Playwright 桌面/移动端浏览器验收
├── .github/workflows/
│   └── quality.yml            # 静态测试与 Chromium 浏览器检查
├── AGENTS.md                  # 内容编辑与工程协作规范
└── 01.html ... 28.html        # 旧链接兼容跳转页
```

根目录的 `01.html`–`28.html` 是兼容入口，会跳转到 `chapters/` 中的正式页面。新内容应写入 `chapters/`，并同步维护 `courses.json`。

## 内容与证据标准

- **独立完整：** 每篇文章都重新定义本页需要的术语与上下文，不以“上一章已经讲过”代替解释。
- **先问题、后机制：** 从具体技术难点开始，依次解释结构、数据流、数学表达、代码和结果。
- **区分事实类型：** 论文原始主张、教学简化、代码实现和后续变体分别标注，不把后来的实现倒灌进早期论文。
- **指标可追溯：** 记录数据集版本、split、IoU 协议、输入分辨率、硬件和计时口径；AP@0.5 不与 COCO AP 混为一谈。
- **图示有语义：** SVG 必须有标题和描述，箭头、分支、特征尺度与文字说明一致。
- **离线优先：** 页面不依赖外部字体、CDN、遥测或运行时网络请求；关键数学表达使用浏览器原生 MathML。
- **如实呈现实验：** 教学示例不是论文复现；未执行的浏览器测试不能标为通过。

第一批 01–05 章依据 YOLOv1、YOLO9000/YOLOv2、YOLOv3 原始论文和 COCO 官方评估协议重写。来源映射见 每篇文章对应的证据台账位于 `docs/evidence/01.json` 至 `05.json`。。

## 本地质量检查

静态检查仅依赖 Python 标准库：

```bash
python -m unittest discover -s tests -v
```

浏览器验收需要安装 Playwright：

```bash
python -m pip install playwright
python -m playwright install chromium
python tests/browser_check.py
```

浏览器检查覆盖首页搜索、28 章入口、01–05 章桌面与移动端布局、横向溢出、页面异常以及核心 SVG 渲染。GitHub Actions 会在 Pull Request 和主分支更新时运行相同的检查。

## GitHub Pages

首页位于仓库根目录，所有资源使用相对路径，可作为 GitHub Pages 的静态站点源。是否已启用 Pages、发布分支/目录以及部署是否成功，应以仓库 Settings → Pages 和 Actions 中的实际状态为准；本仓库文件本身不代表 Pages 已自动启用。

## 许可与第三方资料

仓库未提供经核验的统一开源许可证，因此不要据此推断第三方论文、PDF、模型权重或其他素材可被重新分发。文章中的图示与解释应独立编写；引用原始论文时保留来源链接，并遵守对应资源的许可条件。
