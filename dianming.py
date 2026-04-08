import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import os
import sys
import time
import pygame
import threading
import webbrowser
import ctypes
import urllib.request

# 尝试导入图像处理库 Pillow (用于支持自定义背景图)
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ==========================================
# 【核心修复 1】绝对路径定位 GPS
# ==========================================
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()

# ==========================================
# 注入底层身份 ID，确保任务栏图标正常
# ==========================================
my_app_id = 'yuyuchi.smartpicker.main.2.7' 
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
except Exception:
    pass

class RandomPickerApp:
    def __init__(self, root):
        self.root = root
        
        # 版本号正式升级为 2.7
        self.current_version = "2.7"
        self.root.title(f"SmartPicker v{self.current_version} (视觉自适应版)")
        
        width, height = 800, 600
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # 默认背景色
        self.root.configure(bg="#f0f4f8")

        # ==========================================
        # 【功能】：加载自定义背景图片
        # ==========================================
        bg_path = None
        for ext in ['png', 'jpg', 'jpeg', 'PNG', 'JPG']:
            p = os.path.join(BASE_DIR, f"bg.{ext}")
            if os.path.exists(p):
                bg_path = p
                break
                
        if bg_path:
            if HAS_PIL:
                try:
                    bg_image = Image.open(bg_path)
                    bg_image = bg_image.resize((width, height), Image.Resampling.LANCZOS)
                    self.bg_photo = ImageTk.PhotoImage(bg_image)
                    self.bg_label = tk.Label(root, image=self.bg_photo)
                    self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                    self.bg_label.lower()
                except Exception as e:
                    print(f"背景图片加载失败: {e}")
            else:
                self.root.after(500, lambda: messagebox.showwarning(
                    "缺少图像处理组件", 
                    "检测到您放置了背景图片 (bg)！\n\n为了显示它，请在命令提示符中运行：\npip install pillow\n\n(打包后的EXE无需此操作)", 
                    parent=self.root))

        # 在线更新与反馈配置
        self.github_user = "deng121200" 
        self.github_repo = "Smart-Random-Picker"
        self.update_url = f"https://raw.githubusercontent.com/{self.github_user}/{self.github_repo}/main/version.txt"
        self.release_url = f"https://github.com/{self.github_user}/{self.github_repo}/releases"

        self.audio_enabled = False
        try:
            pygame.mixer.init()
            self.audio_enabled = True
        except:
            pass 
        
        self.names = []
        self.skip_names = []
        self.is_rolling = False
        
        self.rolling_sounds = [os.path.join(BASE_DIR, f) for f in os.listdir(BASE_DIR) if f.startswith('rolling') and f.endswith('.mp3')]

        # --- UI 布局 ---
        self.title_label = tk.Label(root, text="课堂随机点名", font=("Microsoft YaHei", 28, "bold"), bg="#f0f4f8", fg="#333")
        self.title_label.pack(pady=20)
        self.title_label.bind("<Double-Button-1>", self.open_secret_menu) 

        self.name_display = tk.Label(root, text="准备就绪", font=("Microsoft YaHei", 55, "bold"), 
                                     bg="#f0f4f8", fg="#0056b3", wraplength=750)
        self.name_display.pack(pady=20, expand=True)

        self.control_frame = tk.Frame(root, bg="#f0f4f8")
        self.control_frame.pack(pady=10)

        self.btn = tk.Button(self.control_frame, text="开 始", font=("Microsoft YaHei", 20, "bold"), bg="#4caf50", fg="white", 
                             command=self.toggle_roll, width=12, relief="flat", cursor="hand2")
        self.btn.grid(row=0, column=0, padx=20)

        self.slider_frame = tk.Frame(self.control_frame, bg="#f0f4f8")
        self.slider_frame.grid(row=0, column=1, padx=10)
        tk.Label(self.slider_frame, text="抽取人数:", font=("Microsoft YaHei", 12), bg="#f0f4f8").pack(side=tk.LEFT)
        self.draw_count_slider = tk.Scale(self.slider_frame, from_=1, to=20, orient=tk.HORIZONTAL, 
                                          bg="#f0f4f8", length=120, font=("Microsoft YaHei", 10))
        self.draw_count_slider.pack(side=tk.LEFT)

        # ==========================================
        # 【新增功能】：V2.7 专属反馈按钮 (方案 B)
        # ==========================================
        self.feedback_btn = tk.Button(self.control_frame, text="🐛 反馈建议", font=("Microsoft YaHei", 12, "bold"), 
                                      bg="#ff9800", fg="white", command=self.open_feedback_page, 
                                      width=10, relief="flat", cursor="hand2")
        self.feedback_btn.grid(row=0, column=2, padx=10)

        self.bottom_frame = tk.Frame(root, bg="#f0f4f8")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)

        self.history_frame = tk.Frame(self.bottom_frame, bg="#f0f4f8")
        self.history_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(self.history_frame, text="📜 抽取历史:", font=("Microsoft YaHei", 10, "bold"), bg="#f0f4f8", fg="#666").pack(anchor="w")
        
        self.hist_scroll = tk.Scrollbar(self.history_frame)
        self.hist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text = tk.Text(self.history_frame, height=5, width=40, font=("Microsoft YaHei", 10), 
                                    yscrollcommand=self.hist_scroll.set, state=tk.DISABLED, bg="#ffffff")
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.hist_scroll.config(command=self.history_text.yview)

        self.signature_label = tk.Label(self.bottom_frame, text=f"v{self.current_version} | 灵感来源于我\nInspiration from @遇屿迟", 
                                        font=("Microsoft YaHei", 10), bg="#f0f4f8", fg="#999999", justify=tk.RIGHT)
        self.signature_label.pack(side=tk.RIGHT, anchor="s", padx=10)

        self.load_data()
        threading.Thread(target=self.check_for_updates, daemon=True).start()

    # ==========================================
    # 【新增逻辑】：触发浏览器打开 GitHub Issues
    # ==========================================
    def open_feedback_page(self):
        feedback_url = f"https://github.com/{self.github_user}/{self.github_repo}/issues"
        try:
            # 尝试调用系统默认浏览器打开网页
            webbrowser.open(feedback_url)
        except Exception as e:
            # 如果极端情况下（比如多媒体电脑没装任何浏览器），弹出手动复制提示
            messagebox.showerror("连接失败", f"无法自动打开浏览器，请手动复制网址访问：\n\n{feedback_url}", parent=self.root)

    def check_for_updates(self):
        try:
            req = urllib.request.Request(self.update_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read().decode('utf-8').strip()
                remote_version = content.split('\n')[-1].strip()
                if remote_version != self.current_version:
                    if messagebox.askyesno("更新提示", f"发现新版本 v{remote_version}！\n是否前往下载？", parent=self.root):
                        webbrowser.open(self.release_url)
        except:
            pass

    def load_data(self):
        mingdan_path = os.path.join(BASE_DIR, "名单.txt")
        try:
            with open(mingdan_path, "r", encoding="utf-8-sig") as f:
                self.names = [line.strip() for line in f if line.strip()]
            if not self.names:
                self.name_display.config(text="名单为空")
        except FileNotFoundError:
            self.name_display.config(text="未找到名单.txt", fg="red")

        heimingdan_path = os.path.join(BASE_DIR, "黑名单.txt")
        self.skip_names = []
        try:
            with open(heimingdan_path, "r", encoding="utf-8-sig") as f:
                self.skip_names = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            pass

    def open_secret_menu(self, event):
        pwd = simpledialog.askstring("管理员验证", "请输入密码:", show='*', parent=self.root)
        if pwd == "114514":
            self.load_data()
            messagebox.showinfo("成功", f"暗箱操作已就绪！\n已从本地读取 {len(self.skip_names)} 名跳过人员。", parent=self.root)
        elif pwd is not None:
            messagebox.showerror("错误", "密码错误！", parent=self.root)

    def update_names_display(self, names_list):
        text = "、".join(names_list)
        count = len(names_list)
        
        if count <= 2:
            font_size = 55
        elif count <= 5:
            font_size = 45
        elif count <= 10:
            font_size = 35
        elif count <= 15:
            font_size = 28
        else:
            font_size = 22
            
        self.name_display.config(text=text, font=("Microsoft YaHei", font_size, "bold"))

    def toggle_roll(self):
        if not self.names:
            messagebox.showwarning("警告", "请确保程序同目录下有 名单.txt 文件")
            return
        
        if not self.is_rolling:
            self.is_rolling = True
            self.btn.config(text="停 止", bg="#f44336")
            if self.audio_enabled and self.rolling_sounds:
                try:
                    pygame.mixer.music.load(random.choice(self.rolling_sounds))
                    pygame.mixer.music.play(-1)
                except:
                    pass
            self.update_rolling()
        else:
            self.is_rolling = False
            self.btn.config(text="开 始", bg="#4caf50")
            if self.audio_enabled:
                pygame.mixer.music.stop()
            self.finish_roll()

    def update_rolling(self):
        if self.is_rolling:
            count = self.draw_count_slider.get()
            pool = self.names
            if pool:
                fake_winners = random.sample(pool, min(count, len(pool)))
                self.update_names_display(fake_winners)
            self.root.after(50, self.update_rolling)

    def finish_roll(self):
        count = self.draw_count_slider.get()
        pool = [n for n in self.names if n not in self.skip_names]
        if not pool:
            pool = self.names
            
        winners = random.sample(pool, min(count, len(pool)))
        self.update_names_display(winners)
        self.add_to_history(winners)

    def add_to_history(self, winners):
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {'、'.join(winners)}\n")
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = RandomPickerApp(root)
    root.mainloop()
