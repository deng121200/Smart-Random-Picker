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

# ==========================================
# 【核心定位】绝对路径 GPS
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
my_app_id = 'yuyuchi.smartpicker.main.2.8.2' 
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
except Exception:
    pass

class RandomPickerApp:
    def __init__(self, root):
        self.root = root
        
        # 版本号升级为 2.8.2 (修复黑名单暴露Bug，提升隐蔽性)
        self.current_version = "2.8.2"
        self.root.title(f"SmartPicker v{self.current_version} (Win7 纯净防漏版)")
        
        width, height = 800, 600
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # 默认背景色 (清爽蓝灰)
        self.root.configure(bg="#f0f4f8")

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

        # 手动刷新名单按钮
        self.refresh_btn = tk.Button(self.control_frame, text="🔄 刷新", font=("Microsoft YaHei", 12, "bold"), 
                                     bg="#00bcd4", fg="white", command=self.manual_refresh, 
                                     width=8, relief="flat", cursor="hand2")
        self.refresh_btn.grid(row=0, column=2, padx=10)

        # 反馈按钮
        self.feedback_btn = tk.Button(self.control_frame, text="🐛 反馈建议", font=("Microsoft YaHei", 12, "bold"), 
                                      bg="#ff9800", fg="white", command=self.open_feedback_page, 
                                      width=10, relief="flat", cursor="hand2")
        self.feedback_btn.grid(row=0, column=3, padx=10)

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
    # 【引擎】：智能双模文本解码器
    # ==========================================
    def safe_read_file(self, file_path):
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                return [line.strip() for line in f if line.strip()]
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="gbk") as f:
                    return [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"读取文件发生未知错误: {e}")
                return []

    def load_data(self):
        mingdan_path = os.path.join(BASE_DIR, "名单.txt")
        names_data = self.safe_read_file(mingdan_path)
        
        if names_data is None:
            self.name_display.config(text="未找到名单.txt", fg="red")
            self.names = []
        else:
            self.names = names_data
            if not self.names:
                self.name_display.config(text="名单为空")
            else:
                self.name_display.config(fg="#0056b3")

        heimingdan_path = os.path.join(BASE_DIR, "黑名单.txt")
        skip_data = self.safe_read_file(heimingdan_path)
        self.skip_names = skip_data if skip_data is not None else []

    # ==========================================
    # 【漏洞修复】：移除刷新按钮的防漏信息
    # ==========================================
    def manual_refresh(self):
        self.load_data()
        count = len(self.names)
        # 只显示总名单人数，绝口不提跳过人员，确保暗箱完全隐蔽
        messagebox.showinfo("刷新成功", f"名单已更新！\n当前读取到 {count} 名学生。", parent=self.root)

    def open_feedback_page(self):
        feedback_url = f"https://github.com/{self.github_user}/{self.github_repo}/issues"
        try:
            webbrowser.open(feedback_url)
        except Exception as e:
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

    def open_secret_menu(self, event):
        pwd = simpledialog.askstring("管理员验证", "请输入密码:", show='*', parent=self.root)
        if pwd == "114514":
            self.load_data()
            # 只有这里才会显示拦截数量，尽在管理员掌握
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
        if not self.is_rolling:
            self.load_data()
            
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

if __name__ == "__main__":
    root = tk.Tk()
    app = RandomPickerApp(root)
    root.mainloop()
