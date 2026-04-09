# Smart-Random-Picker (课堂智能随机点名系统)

![Version](https://img.shields.io/badge/Version-v3.0.0-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![Python](https://img.shields.io/badge/Python-3.8+-green.svg)

Smart-Random-Picker 是一款专为教育教学环境设计的轻量级随机点名工具。本项目致力于解决传统点名软件在老旧多媒体教学设备（如 Windows 7 系统）上的兼容性痛点，提供开箱即用、防崩溃且具备高度定制化能力的点名体验。

---

## 🌟 V3.0 核心特性

* **离线语音播报 (TTS)**：底层调用 Windows SAPI 接口，实现完全离线的中文姓名语音播报，让课堂互动更具仪式感。
* **纯享级动画引擎**：零第三方图像库依赖，基于纯原生组件实现了平滑的色彩呼吸、动态轮盘滚动及高亮脉冲动画。
* **全局配置中心**：系统首次运行会自动生成 `config.ini`，支持高度自定义（包括动画速度、抽签人数上限、语音音量、播报语速等）。
* **智能双模解码与持久化**：无视桌面新建 TXT 的编码差异，自动容错读取；历次抽取记录不仅实时显示，更会自动以 JSON 格式持久化保存至本地。
* **暗箱拦截机制（黑名单）**：内置隐藏的管理员级控制后台，可设定不参与抽签的人员名单，整个拦截过程对前端用户完全透明。

---

## 🚀 快速上手 (终端用户指南)

### 1. 软件安装与准备
本软件为单文件便携版 (Standalone Executable)，**无需安装**。
1. 前往 [Releases 页面](../../releases/latest) 下载最新的 `SmartPicker.exe` 文件。
2. 将下载的 `.exe` 文件放置在一个新建的专属文件夹中。

### 2. 名单配置
在软件同级目录下，新建一个文本文档并命名为 **`名单.txt`**。
* 每行输入一个姓名。
* 编码格式不受限制（系统支持智能识别）。

*(可选高级玩法)*：在同级目录放置 `config.ini` 可调节高阶参数，放置 `黑名单.txt` 可设置过滤名单。双击主界面顶部标题并输入密码 `114514` 即可激活暗箱。

### 3. 基本操作
* **人数与语音**：拖动滑块调节抽取人数（默认 1~20 人）；点击右侧 🔊/🔇 按钮可随时切换静音。
* **开始/停止**：点击开始按钮屏幕滚动姓名，点击停止展示最终结果并触发语音播报。

---

## 🛠️ 开发者构建指南

如果您希望基于源码进行二次开发，请参考以下步骤：

### 环境依赖
建议使用 **Python 3.8.10** 以确保编译产物向下兼容 Windows 7。
```bash
pip install pygame pyinstaller pywin32
```

### 极速编译命令
使用 PyInstaller 进行单文件打包，并注入所有隐藏依赖组件：
```bash
pyinstaller --noconsole --onefile --clean --name="SmartPicker_V3.0.0" --hidden-import=pygame --hidden-import=win32com.extracommod --hidden-import=win32com.client dianming.py
```

---

## 📝 问题反馈与贡献

如果您在使用过程中遇到任何 Bug 或有新的功能建议，请通过界面的“反馈建议”按钮，或直接访问本仓库的 [Issues 页面](../../issues) 提交工单。

---

## 📄 版权与致谢

* **Inspiration**：设计灵感来源于 @遇屿迟 (yuyuchi)。
* **License**：遵循 MIT 开源协议。允许自由使用、修改及分发。
