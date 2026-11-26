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

首页提供章节搜索与阶段筛选。01–28 章均已按独立文章标准重写，每章包含背景、符号约定、原理图解、可运行的教学脚本、适用边界与原始参考文献，并配有逐篇证据台账。

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
│   ├── 01.html ... 20.html    # 基础、组件、现代架构与轻量化篇（01–20）
│   └── 21.html ... 28.html    # 部署、数据、评估与实战篇（21–28）
├── assets/
│   ├── theme.css              # 首页与章节共用设计系统
│   ├── site.js                # 首页搜索与阶段筛选增强
│   ├── lab-*.js / *-demo.js   # 章节内离线交互实验
│   └── figures/               # 35 张独立可用的 SVG 机制图导出
├── labs/                      # 数据增强、骨干、Neck、NMS、量化等确定性教学工具
├── pdfs/                      # 已收录论文资料
├── docs/
│   ├── architecture.md        # 页面、导航和发布结构说明
│   ├── improvements.md        # 追加式工程改进记录
│   └── evidence/              # 01.json ... 28.json：逐篇证据台账
├── tests/
│   ├── test_site.py                     # 静态结构、链接、公式和 SVG 检查
│   ├── test_labs.py                     # 06–10 章计算工具数值验证
│   ├── test_labs_11_15.py               # 11–15 章数值、标签与协议检查
│   ├── test_modern_yolo_contract.py     # 16–20 章契约与几何数值检查
│   └── browser_check.py                 # Playwright 桌面/移动端浏览器验收
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
- **图示有语义：** SVG 必须有标题和描述，箭头、分支、特征尺度与文字说明一致。06–15 章的 16 张示意图既内联于文章，也导出为 `assets/figures/` 下的独立 SVG，支持离线复用和 XML 比对。
- **离线优先：** 页面不依赖外部字体、CDN、遥测或运行时网络请求；关键数学表达使用浏览器原生 MathML。
- **如实呈现实验：** 教学示例不是论文复现；未执行的浏览器测试不能标为通过。

01–05 章依据 YOLOv1、YOLO9000/YOLOv2、YOLOv3 原始论文和 COCO 官方协议重写；06–10 章依据 YOLOv4、FPN/PANet/BiFPN、GIoU/DIoU/CIoU 与 Darknet/OpenCV 实现进行交叉验证。每篇文章的证据台账存放在 `docs/evidence/01.json` 至 `28.json`，区分已核对的论文主张、推导数字和教学示例。11–15 章核对 Mosaic/CutMix 几何、SPPF 池化等价、NMS 语义与 YOLOv5 v7.0 标签解码；16–28 章核对 YOLOv8/9/10/11/12 架构、量化口径、COCO AP_s 面积定义与 SAHI 全局坐标。

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

浏览器检查覆盖首页搜索、28 章入口、01–28 章的桌面与移动端布局、SVG/MathML、横向溢出、打印模式、锚框交互以及 NMS 阈值/算法交互实验。GitHub Actions 会在 Pull Request 和主分支更新时运行相同的检查。

## GitHub Pages

首页位于仓库根目录，所有资源使用相对路径，可作为 GitHub Pages 的静态站点源。是否已启用 Pages、发布分支/目录以及部署是否成功，应以仓库 Settings → Pages 和 Actions 中的实际状态为准；本仓库文件本身不代表 Pages 已自动启用。

## 许可与第三方资料

仓库未提供经核验的统一开源许可证，因此不要据此推断第三方论文、PDF、模型权重或其他素材可被重新分发。文章中的图示与解释应独立编写；引用原始论文时保留来源链接，并遵守对应资源的许可条件。

## 可运行的工程实验

无需第三方依赖的几何、形状与配置检查：

```bash
python -m labs.anchor_clusters labs/sample-boxes.csv --k 3 --seed 42
python -m labs.box_geometry
python -m labs.fpn_shapes --size 416
python -m labs.darknet_cfg_audit path/to/yolov3-custom.cfg --classes 2
```

完整 YOLOv3 CPU 推理示例需要外部的原始 Darknet cfg/weights、类别名文件、输入图片和 OpenCV：

```bash
python -m pip install -r labs/requirements-inference.txt
python -m labs.yolov3_opencv --help
```

这些实验是配置或算法契约的教学验证，不是论文原始 AP 的重新复现；真正训练与推理时，请固定对应 Darknet/OpenCV 版本及数据来源。

## 第三批深入实验（11–15）

数据增强的几何约定、卷积计算量、池化等价、NMS 算法与 YOLOv5 v7.0 标签/解码均可用 Python 标准库验证：

```bash
python -m labs.augmentation_geometry
python -m labs.backbone_cost
python -m labs.neck_head_contract
python -m labs.nms_reference
python -m labs.yolov5_contract --labels labs/sample-yolov5-labels --classes 2
python -m unittest discover -s tests -v
```

这些实验均是<strong>教学用确定性测试</strong>，不加载第三方权重、不训练网络，也不复现论文 benchmark。YOLOv5 的训练/导出命令固定到上游 `ultralytics/yolov5` **v7.0**；请注意其许可与当前 Ultralytics Python 包的模型 API 不完全相同。

已发布站点：[GitHub Pages](https://1998x-stack.github.io/yolo-tutorial/)。发布与质量验证记录在 [Actions](https://github.com/1998x-stack/yolo-tutorial/actions)。

## 第四批：第 16–20 章深度重构（2026-11-22）

- **16 YOLOv8：** Anchor-Free 格点契约、C2f、解耦 Head、DFL 插值与训练分配。
- **17 YOLOv9/v10：** PGI/GELAN 与一致性双重分配；区分训练辅助机制、one-to-one 推理及真实 NMS-Free 约束。
- **18 YOLO11/v12：** 区分不同发布主体、C3k2/C2PSA 与注意力架构；交互展示关系矩阵复杂度的边界。
- **19 轻量化：** 结构化剪枝、PTQ/QAT、蒸馏、重参数化与全链路验收；不把权重体积当作推理延迟。
- **20 小目标：** COCO AP_s 的面积口径、stride、SAHI 切片、坐标还原与防数据泄漏。

五篇均以独立 HTML 编排，提供一手来源、原创建模 SVG（同步导出 `assets/figures/chapter-16-01.svg` 至 `20-01.svg`）、离线交互与 `docs/evidence/16.json`–`20.json`。计算实验为标准库玩具契约，不代表训练、论文 AP 或 GPU 加速复现。

```bash
python -m labs.modern_yolo_contract
python -m unittest discover -s tests -v
python tests/browser_check.py  # 需要 Playwright + Chromium，覆盖 01–28 章
```

文章源代码、演示与证据在 Pages 部署成功后可通过 `/chapters/16.html` 至 `/chapters/20.html` 访问；仅存在文件或 workflow 不等于浏览器验收通过。

## 第五批：第 21–28 章深度重构（2026-11-22）

- **21 部署与推理加速：** 导出（ONNX/opset）、图优化、FP16/INT8 精度校准与可复现的延迟/吞吐基准口径。
- **22 边缘设备部署：** 功耗、带宽与内存约束下的运行时选择；区分峰值算力与可持续吞吐。
- **23 数据标注与格式：** COCO/YOLO/VOC 坐标约定与转换幂等性、标注质量与泄漏排查。
- **24 训练流水线：** 数据划分、超参与可复现性约束；把训练配置与结果绑定到具体版本。
- **25 模型评估与调优：** PR/混淆矩阵、mAP 协议与误差分析；区分指标下降与分布漂移。
- **26 YOLO+多模态：** 开放词汇、CLIP/SAM/跟踪的组合拆解；区分检测器与下游组件职责。
- **27 行业实战案例：** 以任务契约组织案例，不编造缺出处的业务指标。
- **28 综合实训项目：** 以验收门槛串起数据、训练、评估与部署流程。

八篇均以独立 HTML 编排，提供一手来源、原创建模 SVG（同步导出 `assets/figures/chapter-21-01.svg` 至 `28-01.svg`）、离线交互与 `docs/evidence/21.json`–`28.json`（每篇 8 条证据）。页面内固定开销、吞吐等数字均标注为教学示意值，不代表任何硬件实测。
