# Smart-Random-Picker (课堂智能随机点名系统)

![Version](https://img.shields.io/badge/Version-v3.3.0-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows_7%2B-lightgrey.svg)
![Python](https://img.shields.io/badge/Python-3.8.10-green.svg)
![License](https://img.shields.io/badge/License-MIT-orange.svg)

**SmartPicker** 是一款专为教育教学环境（尤其是老旧多媒体教学白板）量身打造的极简、极速、极安全的课堂随机点名工具。

本项目致力于解决传统点名软件在 Windows 7 系统上的兼容性痛点，通过极致的底层代码重构，实现了**零第三方图像库依赖（秒开）**、**本地离线 TTS 语音播报**以及**物理级隐蔽的暗箱管理机制**。

---

## 🌟 V3.3 终极版核心特性 (Performance & Security)

### ⚡ 性能革命 (Performance 2.0)
* **极速检索引擎**：底层名单查重与黑名单过滤全面采用 `O(1)` 时间复杂度的哈希集合（Set）运算，即使名单上千人也能在毫秒内完成验证。
* **零泄漏动画引擎**：摒弃传统的递归动画，采用 Python 迭代器（Generator）驱动界面色彩渐变与脉冲效果，彻底告别 CPU 飙升与内存泄漏。
* **异步延迟 I/O**：配置系统（`config.ini`）与历史记录（`history.json`）全部采用多线程延迟批量写入机制，极大缓解老旧教学白板的机械硬盘读写压力。

### 🔒 绝对暗箱 (Dark Box 2.0)
* **无痕操作界面**：主界面及状态栏绝对不暴露任何关于“拦截人数”或“黑名单”的敏感信息，视觉滚动池与底层黑名单物理隔离，保证绝对的公平假象。
* **便携式游击队加密**：黑名单数据不再以明文 TXT 存储，而是通过“Base64 编码 + 字节倒置”的混淆算法被安全加密为 `system_config.dat`。**完美支持 U 盘跨电脑热插拔漫游**，无视 Windows 系统账户凭证限制。
* **图形化管理后台**：内置隐藏的 GUI 控制台，通过特定“暗门”触发，无需手动修改任何文件即可完成名单的增删查改。

### 🔊 视听双擎 (Audio & Visual)
* **原生离线 TTS**：底层直连 Windows SAPI 语音接口，无需联网即可用标准的中文（如 Microsoft Lili/HuiHui）念出中签者姓名，采用原生异步线程，杜绝界面卡死。
* **纯享 Tkinter 动效**：无需安装庞大的 Pillow 库，纯原生代码实现平滑的色彩呼吸、动态轮盘滚动及高亮结果展示。

---

## 🚀 快速上手 (小白用户指南)

### 1. 下载与准备
本项目为纯净便携版，**无需安装 Python 及任何环境**。
1. 前往 Releases 页面下载最新的 **`SmartPicker_V3.3.0_Portable.zip`**。
2. 将压缩包解压到你的电脑或 **U 盘**的任意文件夹中。

### 2. 配置名单
打开解压后的文件夹，找到 **`名单.txt`**。
* 用记事本打开，将学生的姓名逐行录入（每行一个名字）。
* 无需担心文件编码问题，系统内置智能双模解码引擎，自动兼容 `UTF-8` 与 `GBK`。

### 3. 开始使用
* 双击运行 `SmartPicker.exe`。
* 拖动滑块选择需要抽取的人数（1~20人）。
* 点击“开始”按钮，屏幕将飞速滚动姓名；点击“停止”揭晓最终结果，并自动触发语音播报。
* 点击主界面的 🔊/🔇 按钮可随时切换静音状态。

---

## 🔐 极客进阶：暗箱操作指南

如果你希望某些特定学生“绝对不会被抽中”，请使用内置的暗箱机制：

1. **唤醒暗门**：在软件主界面，使用鼠标左键**双击顶部的大标题文字**（“课堂随机点名”）。
2. **身份验证**：在弹出的输入框中输入管理员指令：`114514`。
3. **管理后台**：点击“管理黑名单”，在弹出的图形化窗口中，你可以将特定学生移入或移出黑名单。
4. **加密保存**：操作完成后务必点击“💾 保存更改”。系统会将其加密为 `system_config.dat`。

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

本项目已配置完备的 GitHub Actions CI/CD 流水线，推送 `v*` 标签即可自动触发云端构建。

---

## 📄 版权与致谢

* **Author**: @遇屿迟
* **Acknowledgments**: 感谢在架构重构与法医级排错中提供深度推演的 AI 协同开发阵列。
* **License**: 本项目遵循 MIT 开源协议。允许自由使用、修改及分发。
