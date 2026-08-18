# 🎯 YOLO系列 · 从入门到精通

> 📘 28章 实战体系 · 交互式 HTML 课程

> **English TL;DR:** An all-Chinese 28-chapter course on the **YOLO object-detection family** — from the single-stage philosophy and YOLOv1 (grid cell regression) through YOLOv2/9000 (anchor clustering), v3 (Darknet-53 + FPN), v4 (CSPDarknet + Mosaic + CIoU), and the Ultralytics era: v5 → v8 (anchor-free + C2f + DFL) → v9/v10 (GELAN, NMS-free) → v11/v12 (attention C2PSA). Covers backbone/neck/head design, anchor mechanism, loss evolution (IoU→CIoU→DFL), FPN/PANet, augmentation, NMS/Soft-NMS, lightweighting (pruning/INT8/distillation), small-object detection, deployment (ONNX/TensorRT/OpenVINO/Jetson), YOLO-World multimodal, and real-world capstones (auto/security/industrial).

## 📖 课程简介

本课程围绕 **YOLO 目标检测家族**从第一性原理到最新演进做系统讲解：从检测任务与指标（IoU/mAP/FPS）、单阶段哲学讲起，逐代拆解 YOLOv1→v2/v3→v4→v5→v8→v9/v10→v11/v12 的架构演进，深入骨干/Neck/Head、锚框、损失函数（IoU→CIOU→DFL）、FPN/PANet、NMS 后处理与数据增强，再覆盖模型轻量化、小目标检测、ONNX/TensorRT 部署与边缘平台，最后落到 YOLO-World 多模态与自动驾驶/安防/质检行业实战。

## 🏅 YOLO 十代演进主线

```
v1(网格回归) → v2(锚框) → v3(Darknet+FPN) → v4(集大成) → v5 → v8(anchor-free) → v9/10 → v11/12 → YOLO-World(多模态)
```

## 🚀 快速开始

```bash
open index.html   # macOS，纯静态即开即看
```

## 📂 项目结构

```text
yolo-tutorial/
├── index.html / 01.html ~ 28.html / courses.json / theme.css
```

## 📖 章节分段

| 阶段 | 章节 | 核心 |
|------|------|------|
| **基础与 v1–v4** | 01–09 | 指标、哲学、v1/v2/v3/v4、锚框、损失演进 |
| **组件设计** | 10–14 | FPN/PANet、数据增强、骨干/Neck/Head、NMS |
| **Ultralytics 时代** | 15–18 | v5、v8、v9/v10、v11/v12 |
| **轻量 + 部署** | 19–22 | 剪枝/量化/蒸馏、小目标、ONNX/TensorRT、边缘设备 |
| **实战 + 多模态** | 23–28 | 数据标注、训练流水线、评估调优、YOLO-World、行业案例、综合项目 |

## ✨ 亮点

- 覆盖 YOLO 十代完整演进 + 最新 YOLO-World 多模态
- 从架构到损失/后处理，从训练到 TensorRT/边缘部署
- 含行业实战（自动/安防/质检）与综合实训项目

## 🎯 前置知识

- 适合：CV 学习者 / 检测工程师
- 建议具备：Python + PyTorch + 基础 CNN 概念

## ✨ 特色

- 「十代演进 + 工程部署 + 多模态前沿」一条线
- 即开即用纯静态 HTML

---
*本课程由 `yolo-tutorial/` 项目维护。*