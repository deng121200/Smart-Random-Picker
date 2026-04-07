import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import os
import time
import pygame
import threading
import webbrowser
import ctypes
import urllib.request

# ==========================================
# 【新增】：注入底层身份 ID，确保任务栏图标正常
# ==========================================
my_app_id = 'yuyuchi.smartpicker.main.2.0' 
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
except Exception:
    pass

class RandomPickerApp:
    def __init__(self, root):
        self.root = root
        
        # 定义当前版本号
        self.current_version = "2.0"
        self.root.title(f"SmartPicker v{self.current_version} (在线更新版)")
        
        width, height = 800, 600
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.configure(bg="#f0f4f8")

        # 在线更新配置
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
        self.rolling_sounds = [f for f in os.listdir('.') if f.startswith('rolling') and f.endswith('.mp3')]

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
        self.slider_frame.grid(row=0, column=1, padx=20)
        tk.Label(self.slider_frame, text="抽取人数:", font=("Microsoft YaHei", 12), bg="#f0f4f8").pack(side=tk.LEFT)
        self.draw_count_slider = tk.Scale(self.slider_frame, from_=1, to=20, orient=tk.HORIZONTAL, 
                                          bg="#f0f4f8", length=150, font=("Microsoft YaHei", 10))
        self.draw_count_slider.pack(side=tk.LEFT)

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
        try:
            with open("名单.txt", "r", encoding="utf-8") as f:
                self.names = [line.strip() for line in f if line.strip()]
            if not self.names:
                self.name_display.config(text="名单为空")
        except FileNotFoundError:
            self.name_display.config(text="未找到名单.txt", fg="red")

    def open_secret_menu(self, event):
        pwd = simpledialog.askstring("管理员验证", "请输入密码:", show='*', parent=self.root)
        if pwd == "114514":
            self.show_editor()
        elif pwd is not None:
            messagebox.showerror("错误", "密码错误！", parent=self.root)

    def show_editor(self):
        # 统一使用 self.root，彻底解决 AttributeError 报错
        editor = tk.Toplevel(self.root)
        editor.title("高级配置 (机密)")
        editor.geometry("300x450")
        editor.eval(f'tk::PlaceWindow {editor} center')
        
        # Win7 焦点锁定修复
        editor.transient(self.root)
        editor.grab_set()

        tk.Label(editor, text="请输入要暗中跳过的人名\n(每行一个)：", font=("Microsoft YaHei", 10)).pack(pady=10)
        text_area = tk.Text(editor, font=("Microsoft YaHei", 12))
        text_area.pack(expand=True, fill='both', padx=10, pady=5)
        text_area.insert('1.0', '\n'.join(self.skip_names))
        
        # 自动获取光标焦点，直接打字
        text_area.focus_set()

        def save_and_close():
            self.skip_names = [n.strip() for n in text_area.get('1.0', 'end').split('\n') if n.strip()]
            editor.destroy()
            messagebox.showinfo("成功", "跳过名单已更新！", parent=self.root)

        tk.Button(editor, text="保存并退出", font=("Microsoft YaHei", 10, "bold"), bg="#2196f3", fg="white", 
                  command=save_and_close, pady=5).pack(pady=10)

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
            self.name_display.config(text=random.choice(self.names))
            self.root.after(50, self.update_rolling)

    def finish_roll(self):
        count = self.draw_count_slider.get()
        # 过滤掉需要跳过的人
        pool = [n for n in self.names if n not in self.skip_names]
        if not pool:
            pool = self.names # 如果全都被跳过了，就回退到全员名单
        
        winners = random.sample(pool, min(count, len(pool)))
        self.name_display.config(text="、".join(winners))
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
