# 🎲 SmartPicker 课堂智能随机点名系统

![Python](https://img.shields.io/badge/Python-3.8.10-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%207%20SP1+-lightgrey.svg)
![Version](https://img.shields.io/badge/Version-V3.7.0-success.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**SmartPicker** 是一款专为**老旧 Windows 7 多媒体白板**打造的极简、纯净、极客级课堂点名工具。
告别繁杂的环境配置与卡顿的界面，单文件开箱即用，内置工业级热更新与智能防崩底层架构。

## ✨ 核心特性 (V3.7.0)

* **🧠 自适应动态权重算法**：打破绝对随机的概率困境。未抽中者权重累加（+5），中签者权重减半（保底20）。越抽越均匀，兼顾运气与绝对公平。
* **🛡️ 异步安全守护引擎**：手搓级 `safe_after_call` 防崩溃拦截。彻底解决 Tkinter 在多线程网络请求（如后台检查更新）时遭遇强制关闭导致的 Fatal Error 闪退。
* **🚀 工业级 OTA 金蝉脱壳**：内置静默热更新机制，利用原生 CMD 脚本（mbcs 纯净编码）绕过 Windows 文件锁，实现一键无感升级与容灾回滚。
* **🔒 极客暗门与加密沙箱**：
  * **UI 净化**：主界面无任何多余干扰按钮，防学生误触打开浏览器。
  * **暗门唤醒**：双击大标题并输入特定密码（`114514`）即可唤出图形化管理后台。
  * **加密漫游**：彻底抛弃明文，黑名单数据采用 Base64 + 字节反转加密存储，支持 U 盘拔插漫游。
  * **物理护盾**：内置可定制的物理级人物屏蔽机制（有残影参与动画，但绝对不会落锤中签）。
* **兼容极致**：彻底剔除 Pillow 依赖，原生双模编码识别引擎，在 Win7 极其脆弱的图像与文本环境中坚若磐石。

## 📦 快速开始

### 1. 下载便携版 (推荐)
请前往 [Releases 页面](https://github.com/deng121200/Smart-Random-Picker/releases/latest) 下载最新的 `SmartPicker_Vxxx_Portable.zip`。
解压后**无需安装 Python**，双击 `SmartPicker.exe` 即可运行。

### 2. 初始化配置
程序首次运行将自动生成以下文件：
* `名单.txt`：按行存放姓名，支持 `UTF-8` 与 `GBK` 智能识别。
* `weights.json`：自适应权重数据库（自动维护，请勿手动修改）。
* `system_config.dat`：加密存储的黑名单数据。
* `config.ini`：包含动画速度、音效开关等基础设置。

## 🛠️ 本地源码运行

由于本项目高度优化了 Windows 底层调用，如需二次开发，请确保您的环境满足以下要求：

```bash
# 克隆仓库
git clone [https://github.com/deng121200/Smart-Random-Picker.git](https://github.com/deng121200/Smart-Random-Picker.git)

# 安装依赖
pip install pygame==2.5.2 pywin32==306 pyinstaller==5.13.2

# 运行主程序
python dianming.py
```

## 🤖 自动化 CI/CD
本项目已接入 GitHub Actions。开发者只需推送带 `v*` 前缀的 Tag（如 `v3.7.0`），系统将自动剥离版本号、生成带有环境注入的 `config.ini`、打包 `exe` 并发布 Release。

---
*Powered by Python Tkinter & 极客精神 | Inspiration from @遇屿迟*

