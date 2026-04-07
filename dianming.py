import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import os
import time
import pygame
import base64
import urllib.request
import threading
import webbrowser
import ctypes  # 【新增】：导入系统底层接口模块

# ==========================================
# 【新增】：注入底层身份 ID
# 这行代码能确保 Windows 任务栏正确显示你的程序独立图标和名字，而不是显示默认的 Python 图标
# ==========================================
my_app_id = 'yuyuchi.smartpicker.main.1.4' 
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
except Exception:
    pass

class RandomPickerApp:
    def __init__(self, root):
        self.root = root
        
        # 定义当前版本号
        self.current_version = "1.4"
        
        # 【修改】：把窗口标题改成了你的专属名字
        self.root.title(f"遇屿迟点名器 v{self.current_version} (在线更新版)")
        
        width, height = 800, 600
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.configure(bg="#f0f4f8")

        # ==========================================
        # 【在线更新配置区】
        # ==========================================
        self.github_user = "deng121200" 
        self.github_repo = "Smart-Random-Picker"
        
        # 抓取版本号的原始链接
        self.update_url = f"https://raw.githubusercontent.com/{self.github_user}/{self.github_repo}/main/version.txt"
        # 用户点击下载时跳转的链接
        self.release_url = f"https://github.com/{self.github_user}/{self.github_repo}/releases"
        # ==========================================

        self.audio_enabled = False
        try:
            pygame.mixer.init()
            self.audio_enabled = True
        except:
            pass 
        
        self.names = []
        self.skip_names = []
        self.is_rolling = False
        self.rolling_sound = None
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

        # 底部增加了版本号显示
        self.signature_label = tk.Label(self.bottom_frame, text=f"v{self.current_version} | 灵感来源于我\nInspiration from @遇屿迟", 
                                        font=("Microsoft YaHei", 10), bg="#f0f4f8", fg="#999999", justify=tk.RIGHT)
        self.signature_label.pack(side=tk.RIGHT, anchor="s", padx=10)

        self.load_data()
        
        # 软件启动时，在后台线程悄悄检查更新，防止卡死界面
        threading.Thread(target=self.check_for_updates, daemon=True).start()

    def check_for_updates(self):
        try:
            # 伪装成浏览器去访问 GitHub，防止被拦截
            req = urllib.request.Request(self.update_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                latest_version = response.read().decode('utf-8').strip()
            
            # 如果网上的版本号大于当前版本号，触发升级弹窗
            if latest_version > self.current_version:
                # 必须在主线程弹出窗口
                self.root.after(0, self.prompt_update, latest_version)
        except Exception as e:
            # 没网或者报错就当无事发生，绝不打扰用户
            pass

    def prompt_update(self, latest_version):
        ans = messagebox.askyesno("发现新版本！", f"当前版本: v{self.current_version}\n最新版本: v{latest_version}\n\n点名器有新功能啦！是否前往下载更新？")
        if ans:
            webbrowser.open(self.release_url)

    # ... [下方的 load_data, open_secret_menu, show_editor, play_sound, toggle_roll, update_display, add_history, roll_names 函数保持不变] ...
    # 为了排版简洁，这部分逻辑代码和 V1.2 完全一样，直接无缝衔接即可。
    
    def load_data(self):
        if os.path.exists("名单.txt"):
            with open("名单.txt", "r", encoding="utf-8") as f:
                self.names = [line.strip() for line in f if line.strip()]
        
        self.skip_names = []
        if os.path.exists("sys_cache.dat"):
            try:
                with open("sys_cache.dat", "r", encoding="utf-8") as f:
                    encoded_data = f.read().strip()
                    if encoded_data:
                        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
                        self.skip_names = [line.strip() for line in decoded_data.split('\n') if line.strip()]
            except:
                pass

    pwd = simpledialog.askstring("管理员验证", "请输入密码:", show='*', parent=self.root)

        if pwd == "114514":
            self.show_editor()
        elif pwd is not None:
            messagebox.showerror("错误", "密码不正确，访问被拒绝！")

        def show_editor(self):
        # 【修复 1】：把 self.root 改成 self.window，解决报错
        editor = tk.Toplevel(self.window) 
        editor.title("高级配置 (机密)")
        editor.geometry("300x400")
        editor.eval(f'tk::PlaceWindow {editor} center')

        # 【修复 2】：锁定焦点！这是解决 Win7 无法输入的“神药”
        editor.transient(self.window) # 让它始终浮在主程序上面
        editor.grab_set()             # 强制抓取键盘，不输入完不准点别处

        tk.Label(editor, text="请输入要暗中跳过的人名\n(每行一个)：").pack(pady=10)
        
        # 创建文本框
        text_area = tk.Text(editor, font=("Microsoft YaHei", 12))
        text_area.pack(expand=True, fill='both', padx=10, pady=5)
        text_area.insert('1.0', '\n'.join(self.skip_names))
        
        # 【修复 3】：光标自动闪烁，让你一打开就能打字
        text_area.focus_set()

        # 这里下面应该还有你原本的“保存”按钮代码，请记得接在后面

        tk.Label(editor, text="请输入要暗中跳过的人名\n(每行一个)：").pack(pady=10)
        text_area = tk.Text(editor, font=("Microsoft YaHei", 12))
        text_area.pack(expand=True, fill='both', padx=10, pady=5)
        text_area.insert('1.0', '\n'.join(self.skip_names))

        def save_secret():
            new_data = text_area.get('1.0', 'end').strip()
            self.skip_names = [n.strip() for n in new_data.split('\n') if n.strip()]
            encoded = base64.b64encode(new_data.encode('utf-8')).decode('utf-8')
            with open("sys_cache.dat", "w", encoding="utf-8") as f:
                f.write(encoded)
            messagebox.showinfo("成功", "数据已加密保存！")
            editor.destroy()

        tk.Button(editor, text="加密并保存", bg="#f0ad4e", fg="white", font=("Microsoft YaHei", 12), command=save_secret).pack(pady=10)

    def play_sound(self, file, loop=0):
        if self.audio_enabled and os.path.exists(file):
            try:
                sound = pygame.mixer.Sound(file)
                sound.play(loops=loop)
                return sound
            except:
                pass
        return None

    def toggle_roll(self):
        if not self.names:
            self.name_display.config(text="请检查名单", fg="red")
            return

        if not self.is_rolling:
            self.is_rolling = True
            self.btn.config(text="停 止", bg="#f44336")
            
            if self.rolling_sounds:
                chosen_bgm = random.choice(self.rolling_sounds)
                self.rolling_sound = self.play_sound(chosen_bgm, loop=-1)
            else:
                self.rolling_sound = self.play_sound("rolling.mp3", loop=-1)
            
            self.roll_names()
        else:
            self.is_rolling = False
            self.btn.config(text="开 始", bg="#4caf50")
            if self.rolling_sound:
                self.rolling_sound.stop()
            self.play_sound("win.mp3", loop=0)

    def update_display(self, choices, color):
        length = len(choices)
        if length <= 1: font_size = 55
        elif length <= 5: font_size = 40
        elif length <= 10: font_size = 30
        else: font_size = 22
        
        text = "   ".join(choices)
        self.name_display.config(text=text, fg=color, font=("Microsoft YaHei", font_size, "bold"))

    def add_history(self, choices):
        current_time = time.strftime('%H:%M:%S')
        history_str = f"[{current_time}] 抽取了: " + "、".join(choices) + "\n"
        
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert('1.0', history_str)
        self.history_text.config(state=tk.DISABLED)

    def roll_names(self):
        target_count = self.draw_count_slider.get()

        if self.is_rolling:
            fake_count = min(target_count, len(self.names))
            fake_choices = random.sample(self.names, fake_count) if fake_count > 0 else []
            self.update_display(fake_choices, "#555")
            self.root.after(60, self.roll_names)
        else:
            valid_pool = [n for n in self.names if n not in self.skip_names]
            if not valid_pool: valid_pool = self.names 
            real_count = min(target_count, len(valid_pool))
            final_choices = random.sample(valid_pool, real_count) if real_count > 0 else ["无数据"]
            self.update_display(final_choices, "#d9534f")
            if final_choices != ["无数据"]:
                self.add_history(final_choices)

if __name__ == "__main__":
    root = tk.Tk()
    app = RandomPickerApp(root)
    root.mainloop()
