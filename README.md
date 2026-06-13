# 🎓 SmartPicker Pro 全能智慧课堂管理系统

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20macOS%20|%20Linux-lightgrey.svg)
![Version](https://img.shields.io/badge/Version-V5.0.0%20Pro-success.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![i18n](https://img.shields.io/badge/i18n-ZH%20|%20EN%20|%20JA%20|%20KO-orange.svg)

**SmartPicker Pro** 是一款开源、跨平台、全能型的智慧课堂数字化管理中枢。
项目由最初的“课堂随机点名器”进化而来，现已集成**多模式点名、智能考勤、作业成绩管理、数据可视化报表生成**等核心教务功能。

## ✨ 核心特性

* **🎯 10维抽取引擎**：普通/加权/分组/轮盘/淘汰/竞赛等 10 种点名模式，满足任何课堂互动场景。
* **🌍 全球化跨平台**：完美运行于 Windows、macOS 和 Linux。内置中文、英文、日文、韩文四国语言无缝切换。
* **🏫 全生命周期管理**：
  * **考勤审批**：迟到、早退、请假全流程记录。
  * **考务与作业**：作业分发批改、考场自动排座、成绩雷达图分析。
  * **游戏化互动**：支持积分排行、星星奖励与隐藏徽章（成就系统）解锁。
* **📊 深度数据驱动**：底层基于 SQLite 关系型数据库。支持利用 `matplotlib` 动态生成数据报表，并通过 `fpdf` / `openpyxl` 引擎一键导出 PDF 综合报告与 Excel 电子表格。
* **🎨 现代化界面**：8套预设 UI 主题（暗夜模式、浪漫粉、科技蓝等），支持丰富的 GUI 呼吸/渐变动画引擎。

## 📥 快速下载 (开箱即用)

我们通过 GitHub Actions 矩阵构建了全平台的免安装可执行文件：
👉 [点击前往 Releases 下载最新版本](https://github.com/deng121200/Smart-Random-Picker/releases/latest)

* **Windows 用户**：直接下载并运行 `SmartPicker-Pro.exe`
* **macOS / Linux 用户**：下载对应平台的打包程序即可运行

## 🛠️ 本地开发与源码运行

如果你想参与二次开发或构建自己的插件，请按以下步骤配置环境：

### 1. 克隆代码
git clone https://github.com/deng121200/Smart-Random-Picker.git
cd Smart-Random-Picker

### 2. 安装核心生态依赖
本项目采用了优雅降级设计，缺少某些库只影响特定功能，不会导致崩溃。但为了获得完整体验（如图表、PDF导出、语音），建议安装全量依赖：

# 基础运行库与图表/办公导出生态
pip install pygame pyinstaller openpyxl fpdf python-docx matplotlib Pillow psutil

# Windows 专属依赖（用于 TTS 语音播报，Mac/Linux 用户无需安装）
pip install pywin32

### 3. 启动项目
python dianming.py

## 🧩 插件系统 (Plugin Architecture)
V5.0 引入了高度可扩展的插件沙箱机制。开发者只需在 `plugins` 目录下创建 Python 脚本并实现 `Plugin` 基类，即可无缝向主程序注入新菜单、新功能与监听底层生命周期事件。详情请见 `plugins/example_plugin.py` 示例。

## 🤝 贡献与反馈
欢迎提交 Pull Requests 或发布 Issues。让我们一起让教育技术变得更酷！

---
*Architected and crafted with ❤️ by [@遇屿迟]*
