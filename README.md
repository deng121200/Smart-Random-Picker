# Smart-Random-Picker (课堂智能随机点名系统)

[![Version](https://img.shields.io/badge/Version-v3.4.0-blue.svg)](https://github.com/deng121200/Smart-Random-Picker/releases/latest)
![Platform](https://img.shields.io/badge/Platform-Windows_7%2B-lightgrey.svg)
[![Python](https://img.shields.io/badge/Python-3.8.10-green.svg)](https://www.python.org/downloads/release/python-3810/)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](https://opensource.org/licenses/MIT)

**SmartPicker** 是一款专为教育教学环境（尤其是老旧多媒体教学白板）量身打造的极简、极速、极安全的课堂随机点名工具。

本项目致力于解决传统点名软件在 Windows 7 系统上的兼容性痛点，通过极致的底层代码重构，实现了**零第三方图像库依赖（秒开）**、**本地离线 TTS 语音播报**、**物理级隐蔽的暗箱管理机制**，以及**工业级的 OTA 自动热更新引擎**。

---

## 🌟 V3.4 核心特性 (Architecture & Security)

### 🔄 自动进化 (OTA Update Engine) [New!]
* **金蝉脱壳热更新**：内置双进程接力替换机制，突破 Windows 文件锁限制，实现一键静默覆盖与自动重启。
* **法医级容灾机制**：包含流式下载进度条防假死、底层状态码拦截、文件防劫持校验及 `.backup` 自动回滚，确保断网、断电等极端环境下的系统绝对安全。

### ⚡ 性能革命 (Performance 2.0)
* **极速检索引擎**：底层名单查重与黑名单过滤全面采用 `O(1)` 时间复杂度的哈希集合（Set）运算，即使名单上千人也能在毫秒内完成验证。
* **零泄漏动画引擎**：摒弃传统的递归动画，采用 Python 迭代器（Generator）驱动界面色彩渐变与脉冲效果，彻底告别 CPU 飙升与内存泄漏。
* **异步延迟 I/O**：配置系统与历史记录全部采用多线程延迟批量写入机制，极大缓解老旧机械硬盘读写压力。

### 🔒 绝对暗箱 (Dark Box 2.0)
* **便携式游击队加密**：黑名单数据彻底告别明文，通过“Base64 编码 + 字节倒置”算法混淆为隐藏的 `system_config.dat`。**完美支持 U 盘跨电脑热插拔漫游**。
* **图形化隐秘后台**：内置触发式 GUI 控制台，主界面零暴露。动画滚动池与黑名单底层物理隔离，视觉上绝对公平。

### 🔊 视听双擎 (Audio & Visual)
* **原生离线 TTS**：底层直连 Windows SAPI 语音接口，无需联网即可播报，采用原生异步线程标志位防崩溃。
* **纯享 Tkinter 动效**：无需安装庞大的 Pillow 库，纯原生代码实现平滑的色彩呼吸与动态轮盘。

---

## 🚀 快速上手 (小白用户指南)

### 1. 下载与准备
本项目为纯净便携版，**无需安装 Python 及任何环境**。
1. 前往 [Releases 页面](https://github.com/deng121200/Smart-Random-Picker/releases/latest) 下载最新的 **`SmartPicker_V3.4.0_Portable.zip`**。
2. 将压缩包解压到你的电脑或 **U 盘**的任意文件夹中。

### 2. 配置名单
打开解压后的文件夹，找到 **`名单.txt`**。
* 用记事本打开，将学生的姓名逐行录入（每行一个名字）。
* 无需担心文件编码问题，系统内置智能双模解码引擎，自动兼容 `UTF-8` 与 `GBK`。

### 3. 开始使用
* 双击运行 `SmartPicker.exe`。
* 拖动滑块选择需要抽取的人数（1~20人）。
* 点击“开始”按钮；点击“停止”揭晓最终结果，并触发语音播报。
* *注：当 [GitHub 主页](https://github.com/deng121200/Smart-Random-Picker) 有新版本发布时，软件会自动弹出升级提示，一键即可无感热更新。*

---

## 🔐 极客进阶：暗箱操作指南

如果你希望某些特定学生“绝对不会被抽中”，请使用内置的暗箱机制：

1. **唤醒暗门**：在软件主界面，使用鼠标左键**双击顶部的大标题文字**（“课堂随机点名”）。
2. **身份验证**：在弹出的输入框中输入管理员指令：`114514`。
3. **管理后台**：点击“管理黑名单”，在弹出的图形化窗口中完成拦截名单的增删。
4. **加密保存**：操作完成后务必点击“💾 保存更改”。系统会将其隐式加密。

> **⚠️ 提示**：整个拦截过程对普通观察者绝对隐蔽，滚动动画中也不会出现被拦截者的名字。

---

## 🛠️ 开发者构建指南

如果你希望基于源码进行二次开发，请严格遵循以下环境约束：

### 环境依赖
为了确保打包出的 `.exe` 完美兼容 Windows 7 白板，请务必使用 **Python 3.8.10 (64位)** 环境。

    pip install pygame==2.5.2 pywin32==306 pyinstaller==5.13.2

### 极速单行编译命令
在 CMD 终端中执行以下命令（注意隐式导入了 `win32com.extracommod` 以防止跨线程 TTS 报错）：

    pyinstaller --noconsole --onefile --clean --name "SmartPicker" --hidden-import=pygame --hidden-import=win32com --hidden-import=win32com.client --hidden-import=win32com.extracommod dianming.py

本项目已配置完备的 GitHub Actions CI/CD 流水线，推送 `v*` 标签即可自动触发云端自动化构建。

---

## 📄 版权与致谢

* **Author**: [@遇屿迟](https://github.com/deng121200)
* **Acknowledgments**: 感谢在架构重构与法医级排错中提供深度推演的多模型 AI 协同开发阵列 (Gemini 3.1 Pro x DeepSeek R1 x GLM 4.7)。
* **License**: 本项目遵循 [MIT 开源协议](https://opensource.org/licenses/MIT)。允许自由使用、修改及分发。
