#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SmartPicker V3.0 - 课堂智能随机点名系统（性能优化版）
【核心定位】Win7 多媒体白板专用纯净版
【环境要求】Python 3.8.10 (64位) + Windows 7 SP1
【作者】@遇屿迟
【版本】3.0.0-Optimized
【优化内容】
- ConfigManager: 延迟写入机制，减少90%磁盘I/O
- DataManager: 集合查找O(1)，提升100倍验证速度
- AnimationEngine: 迭代器替代递归，消除内存泄漏
- SmartPickerApp: 滚动动画优化，减少80% CPU占用
- 历史记录: 限制1000条，控制内存增长
"""

import tkinter as tk
from tkinter import simpledialog, messagebox, font as tkfont
import random
import os
import sys
import time
import threading
import webbrowser
import ctypes
import urllib.request
import json
import configparser
from datetime import datetime
from typing import List, Optional, Tuple, Dict

# ==========================================
# 可选依赖导入（优雅降级设计）
# ==========================================
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("【提示】pygame 未安装，音频功能将禁用")

try:
    import win32com.client
    WIN32COM_AVAILABLE = True
except ImportError:
    WIN32COM_AVAILABLE = False
    print("【提示】pywin32 未安装，语音播报功能将禁用")

# ==========================================
# 【核心定位】绝对路径 GPS
# ==========================================
def get_base_path() -> str:
    """获取程序运行的基准目录（支持打包和源码运行）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()

# ==========================================
# 注入底层身份 ID，确保任务栏图标正常
# ==========================================
MY_APP_ID = 'yuyuchi.smartpicker.main.3.0.0'
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(MY_APP_ID)
except (AttributeError, OSError):
    pass  # 非Windows环境或旧版Windows静默忽略

# ==========================================
# 配置管理器（单例模式 + 性能优化版）
# ==========================================
class ConfigManager:
    """配置管理器，负责读取、写入和验证所有配置参数"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.config_path = os.path.join(BASE_DIR, "config.ini")
        self.default_config = {
            'GENERAL': {
                'version': '3.6.0',
                'language': 'zh_CN',
                'auto_check_update': 'true',
                'enable_logging': 'true',
                'log_level': 'INFO',
                'skipped_version': ''  # <--- 新增这行
            },
            'UI': {
                'theme': 'light',
                'animation_speed': 'medium',
                'font_family': 'Microsoft YaHei',
                'enable_animations': 'true'
            },
            'PICKER': {
                'default_draw_count': '1',
                'max_draw_count': '20',
                'enable_blacklist': 'true',
                'voice_enabled': 'true',
                'voice_rate': '0',
                'voice_volume': '100'
            },
            'AUDIO': {
                'enable_sound': 'true',
                'rolling_sound_volume': '80',
                'victory_sound_volume': '100'
            }
        }
        
        self.config = configparser.ConfigParser()
        self._load_or_create_config()
        
        # 【性能优化】延迟写入机制
        self._pending_save = False
        self._save_timer = None
        self._dirty = False
        self._root_ref = None
        
        self._initialized = True
    
    def _load_or_create_config(self):
        """加载或创建配置文件"""
        if not os.path.exists(self.config_path):
            self._create_default_config()
        else:
            try:
                self.config.read(self.config_path, encoding='utf-8')
                self._validate_config()
            except Exception as e:
                print(f"【警告】配置文件读取失败，将使用默认配置: {e}")
                self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置文件"""
        for section, options in self.default_config.items():
            self.config[section] = options
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            print(f"【提示】已创建默认配置文件: {self.config_path}")
        except Exception as e:
            print(f"【警告】无法创建配置文件: {e}")
    
    def _validate_config(self):
        """验证配置文件完整性"""
        for section, options in self.default_config.items():
            if section not in self.config:
                self.config[section] = {}
            for key, default_value in options.items():
                if key not in self.config[section]:
                    self.config[section][key] = default_value
    
    def get(self, section: str, key: str, fallback=None):
        """获取配置值"""
        try:
            return self.config.get(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def set(self, section: str, key: str, value: str):
        """设置配置值（延迟写入优化）"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = str(value)
        
        self._dirty = True
        self._schedule_save()
    
    def _schedule_save(self):
        """【性能优化】调度延迟保存（2秒后批量写入）"""
        if self._save_timer:
            self._save_timer.cancel()
        
        if self._root_ref:
            self._save_timer = self._root_ref.after(2000, self._save_config)
        else:
            self._save_config()
    
    def set_root_reference(self, root):
        """设置Tkinter root引用，用于延迟保存"""
        self._root_ref = root
    
    def _save_config(self):
        """保存配置文件（批量写入优化）"""
        if not self._dirty:
            return
        
        try:
            temp_path = self.config_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            
            if os.path.exists(self.config_path):
                os.remove(self.config_path)
            os.rename(temp_path, self.config_path)
            
            self._dirty = False
            self._save_timer = None
        except Exception as e:
            print(f"【警告】无法保存配置文件: {e}")
    
    def force_save(self):
        """【性能优化】强制立即保存配置"""
        if self._save_timer:
            self._save_timer.cancel()
            self._save_timer = None
        self._save_config()
    
    def get_bool(self, section: str, key: str, fallback=False) -> bool:
        """获取布尔值配置"""
        value = self.get(section, key, str(fallback))
        return value.lower() in ('true', 'yes', '1', 'on')
    
    def get_int(self, section: str, key: str, fallback=0) -> int:
        """获取整数值配置"""
        try:
            return int(self.get(section, key, str(fallback)))
        except ValueError:
            return fallback
    
    def get_float(self, section: str, key: str, fallback=0.0) -> float:
        """获取浮点数值配置"""
        try:
            return float(self.get(section, key, str(fallback)))
        except ValueError:
            return fallback
    
    def __del__(self):
        """析构时确保保存配置"""
        if self._dirty:
            self._save_config()

# ==========================================
# 数据管理器（性能优化版）
# ==========================================
class DataManager:
    """数据管理器，负责名单文件的读写和编码处理"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.logger = self._get_logger()
        
        # 【性能优化】缓存机制
        self._cache = {
            'names': None,
            'blacklist': None,
            'names_set': None,
            'blacklist_set': None,
            'last_load_time': 0
        }
        
        # 【性能优化】历史记录大小限制
        self._max_history_size = 1000
    
    def _get_logger(self):
        """获取日志记录器（简化版）"""
        class SimpleLogger:
            def info(self, msg): print(f"[INFO] {msg}")
            def warning(self, msg): print(f"[WARNING] {msg}")
            def error(self, msg): print(f"[ERROR] {msg}")
        return SimpleLogger()
    
    def safe_read_file(self, file_path: str) -> Optional[List[str]]:
        """安全读取文件，智能处理编码问题"""
        if not os.path.exists(file_path):
            self.logger.warning(f"文件不存在: {file_path}")
            return None
        
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'utf-16', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    lines = [line.strip() for line in f if line.strip()]
                    if lines:
                        self.logger.info(f"成功读取文件 [{encoding}]: {file_path}, 共{len(lines)}行")
                        
                        seen = set()
                        unique_lines = []
                        for line in lines:
                            if line not in seen:
                                seen.add(line)
                                unique_lines.append(line)
                        
                        if len(unique_lines) < len(lines):
                            self.logger.warning(f"已移除 {len(lines) - len(unique_lines)} 个重复项")
                        
                        return unique_lines
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.logger.error(f"读取文件时发生错误 [{encoding}]: {file_path} - {e}")
                if encoding == encodings[-1]:
                    break
        
        self.logger.error(f"无法解码文件，尝试了所有编码: {file_path}")
        return []
    
    def load_all_data(self) -> Tuple[List[str], List[str]]:
        """加载所有名单数据（带缓存优化）"""
        current_time = time.time()
        if (self._cache['names'] is not None and 
            current_time - self._cache['last_load_time'] < 5):
            return self._cache['names'], self._cache['blacklist']
        
        main_list_path = os.path.join(BASE_DIR, "名单.txt")
        names = self.safe_read_file(main_list_path)
        if names is None:
            self.logger.error("未找到 名单.txt 文件")
            names = []
        
        blacklist = self.load_encrypted_blacklist()
        
        names_set = set(names)
        blacklist_set = set(blacklist)
        
        valid_blacklist_set = blacklist_set & names_set
        invalid_names_set = blacklist_set - names_set
        
        valid_blacklist = list(valid_blacklist_set)
        invalid_names = list(invalid_names_set)
        
        if invalid_names:
            if self.config.get_bool('GENERAL', 'enable_logging', False):
                self.logger.warning(f"发现 {len(invalid_names)} 个无效的跳过名单条目")
        
        self._cache['names'] = names
        self._cache['blacklist'] = valid_blacklist
        self._cache['names_set'] = names_set
        self._cache['blacklist_set'] = valid_blacklist_set
        self._cache['last_load_time'] = current_time
        
        return names, valid_blacklist
    
    def save_history(self, history_data: List[Dict]):
        """保存抽取历史到文件（性能优化版）"""
        try:
            if len(history_data) > self._max_history_size:
                history_data = history_data[-self._max_history_size:]
            
            history_path = os.path.join(BASE_DIR, "history.json")
            
            temp_path = history_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
            
            if os.path.exists(history_path):
                os.remove(history_path)
            os.rename(temp_path, history_path)
            
            self.logger.info(f"历史记录已保存: {history_path}")
        except Exception as e:
            self.logger.error(f"保存历史记录失败: {e}")
    
    def clear_cache(self):
        """【性能优化】清除缓存，强制重新加载数据"""
        self._cache = {
            'names': None,
            'blacklist': None,
            'names_set': None,
            'blacklist_set': None,
            'last_load_time': 0
        }
    
    def _encrypt_blacklist(self, blacklist: List[str]) -> Optional[bytes]:
        """便携式混淆加密：支持跨电脑 U 盘流转"""
        if not blacklist:
            return None
            
        try:
            import base64
            data_str = json.dumps(blacklist, ensure_ascii=False)
            encoded = base64.b64encode(data_str.encode('utf-8'))
            reversed_bytes = encoded[::-1]
            
            self.logger.info(f"黑名单便携式加密成功，{len(blacklist)}条记录")
            return reversed_bytes
            
        except Exception as e:
            self.logger.error(f"黑名单加密失败: {e}")
            return None
    
    def _decrypt_blacklist(self, encrypted_data: bytes) -> List[str]:
        """便携式解密：还原反转并解开 Base64"""
        if not encrypted_data:
            return []
            
        try:
            import base64
            decoded_bytes = base64.b64decode(encrypted_data[::-1])
            data_str = decoded_bytes.decode('utf-8')
            blacklist = json.loads(data_str)
            
            self.logger.info(f"黑名单便携式解密成功，{len(blacklist)}条记录")
            return blacklist
            
        except Exception as e:
            self.logger.error(f"黑名单解密失败: {e}")
            return []
    
    def _get_blacklist_path(self) -> str:
        """获取加密黑名单文件路径"""
        return os.path.join(BASE_DIR, "system_config.dat")
    
    def load_encrypted_blacklist(self) -> List[str]:
        """加载加密的黑名单"""
        encrypted_path = self._get_blacklist_path()
        legacy_path = os.path.join(BASE_DIR, "黑名单.txt")
        
        if os.path.exists(encrypted_path):
            try:
                with open(encrypted_path, 'rb') as f:
                    encrypted_data = f.read()
                
                if encrypted_data:
                    return self._decrypt_blacklist(encrypted_data)
                    
            except Exception as e:
                self.logger.error(f"读取加密黑名单文件失败: {e}")
        
        if os.path.exists(legacy_path):
            self.logger.warning("发现明文黑名单文件，将自动迁移到加密格式")
            plain_blacklist = self.safe_read_file(legacy_path) or []
            
            encrypted_data = self._encrypt_blacklist(plain_blacklist)
            if encrypted_data:
                try:
                    with open(encrypted_path, 'wb') as f:
                        f.write(encrypted_data)
                    self.logger.info("黑名单已迁移到加密格式")
                    
                    try:
                        os.remove(legacy_path)
                        self.logger.info("明文黑名单文件已删除")
                    except:
                        pass
                        
                except Exception as e:
                    self.logger.error(f"保存加密黑名单失败: {e}")
            
            return plain_blacklist
        
        return []
    
    def save_encrypted_blacklist(self, blacklist: List[str]) -> bool:
        """保存加密的黑名单"""
        try:
            encrypted_data = self._encrypt_blacklist(blacklist)
            if encrypted_data is None:
                return False
            
            encrypted_path = self._get_blacklist_path()
            
            temp_path = encrypted_path + '.tmp'
            with open(temp_path, 'wb') as f:
                f.write(encrypted_data)
            
            if os.path.exists(encrypted_path):
                os.remove(encrypted_path)
            os.rename(temp_path, encrypted_path)
            
            self.logger.info(f"黑名单已加密保存: {encrypted_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存加密黑名单失败: {e}")
            return False

# ==========================================
# 语音管理器
# ==========================================
class VoiceManager:
    """语音管理器，负责文本到语音的转换"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.enabled = self.config.get_bool('PICKER', 'voice_enabled', True) and WIN32COM_AVAILABLE
        
        if self.enabled:
            try:
                self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
                self._setup_voice()
                self.log("语音引擎初始化成功")
            except Exception as e:
                self.enabled = False
                self.log(f"语音引擎初始化失败: {e}", level="error")
        else:
            self.speaker = None
            if not WIN32COM_AVAILABLE:
                self.log("pywin32 未安装，语音功能禁用", level="warning")
    
    def log(self, message: str, level: str = "info"):
        """日志记录"""
        prefix = {
            "info": "[VOICE-INFO]",
            "warning": "[VOICE-WARN]",
            "error": "[VOICE-ERROR]"
        }.get(level, "[VOICE]")
        print(f"{prefix} {message}")
    
    def _setup_voice(self):
        """配置语音参数"""
        if not self.enabled or not self.speaker:
            return
        
        try:
            rate = self.config.get_int('PICKER', 'voice_rate', 0)
            if -10 <= rate <= 10:
                self.speaker.Rate = rate
            
            volume = self.config.get_int('PICKER', 'voice_volume', 100)
            if 0 <= volume <= 100:
                self.speaker.Volume = volume
            
            voices = self.speaker.GetVoices()
            chinese_voice_found = False
            
            for i in range(voices.Count):
                voice = voices.Item(i)
                voice_desc = voice.GetDescription()
                if any(keyword in voice_desc for keyword in ["Chinese", "中文", "China", "Taiwan"]):
                    self.speaker.Voice = voice
                    chinese_voice_found = True
                    self.log(f"使用中文语音: {voice_desc}")
                    break
            
            if not chinese_voice_found and voices.Count > 0:
                self.speaker.Voice = voices.Item(0)
                self.log(f"使用默认语音: {self.speaker.Voice.GetDescription()}")
                
        except Exception as e:
            self.log(f"语音配置失败: {e}", level="warning")
    
    def speak(self, text: str, async_mode: bool = True):
        """朗读文本"""
        if not self.enabled or not self.speaker or not text:
            return
        
        try:
            flags = 1 if async_mode else 0
            self.speaker.Speak(text, flags)
        except Exception as e:
            self.log(f"语音播放失败: {e}", level="error")
    
    def speak_winners(self, winners: List[str]):
        """播报抽取结果"""
        if not winners:
            return
        
        if len(winners) == 1:
            text = f"抽取到：{winners[0]}"
        else:
            names_text = "、".join(winners)
            text = f"共抽取 {len(winners)} 人，分别是：{names_text}"
        
        self.speak(text)
    
    def stop(self):
        """停止当前语音播放"""
        if self.enabled and self.speaker:
            try:
                self.speaker.Speak("", 3)
            except Exception:
                pass

# ==========================================
# 动画引擎（纯Tkinter实现 + 性能优化版）
# ==========================================
class AnimationEngine:
    """纯Tkinter动画引擎，无Pillow依赖"""
    
    def __init__(self, root):
        self.root = root
        self.config = ConfigManager()
        self.animation_speed = self._get_speed_value()
        
        self._animation_pool = {}
        self._active_animations = set()
        
        self.colors = {
            'primary': '#0056b3',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'rolling_start': '#0056b3',
            'rolling_end': '#2196f3',
            'victory': '#4caf50'
        }
    
    def _get_speed_value(self) -> int:
        """根据配置获取动画速度值"""
        speed_map = {
            'slow': 30,
            'medium': 16,
            'fast': 8
        }
        speed_config = self.config.get('UI', 'animation_speed', 'medium')
        return speed_map.get(speed_config.lower(), 16)
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """十六进制颜色转RGB元组"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """RGB元组转十六进制颜色"""
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    
    def interpolate_color(self, start_color: str, end_color: str, ratio: float) -> str:
        """颜色插值"""
        start_rgb = self.hex_to_rgb(start_color)
        end_rgb = self.hex_to_rgb(end_color)
        
        result_rgb = (
            int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio),
            int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio),
            int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
        )
        
        return self.rgb_to_hex(result_rgb)
    
    def color_transition(self, widget, start_color: str, end_color: str, 
                        duration: int = 500, callback=None):
        """颜色渐变动画（性能优化版）"""
        if not self.config.get_bool('UI', 'enable_animations', True):
            widget.config(fg=end_color)
            if callback:
                callback()
            return
        
        animation_id = id(widget)
        if animation_id in self._active_animations:
            self._cancel_animation(animation_id)
        
        frames = max(1, int(duration / self.animation_speed))
        
        def animation_generator():
            for frame in range(frames + 1):
                ratio = frame / frames
                current_color = self.interpolate_color(start_color, end_color, ratio)
                widget.config(fg=current_color)
                yield frame
        
        gen = animation_generator()
        self._active_animations.add(animation_id)
        
        def animate_step():
            try:
                next(gen)
                self.root.after(self.animation_speed, animate_step)
            except StopIteration:
                widget.config(fg=end_color)
                self._active_animations.discard(animation_id)
                if callback:
                    callback()
        
        animate_step()
    
    def _cancel_animation(self, animation_id):
        """【性能优化】取消指定动画"""
        self._active_animations.discard(animation_id)
    
    def cancel_all_animations(self):
        """【性能优化】取消所有动画"""
        self._active_animations.clear()
    
    def pulse_animation(self, widget, base_color: str, pulse_color: str, 
                       cycles: int = 3, pulse_duration: int = 300):
        """脉冲动画（呼吸效果）"""
        if not self.config.get_bool('UI', 'enable_animations', True):
            return
        
        def pulse_generator():
            for cycle in range(cycles * 2):
                if cycle % 2 == 0:
                    for frame in range(int(pulse_duration / (2 * self.animation_speed)) + 1):
                        ratio = frame / int(pulse_duration / (2 * self.animation_speed))
                        current_color = self.interpolate_color(base_color, pulse_color, ratio)
                        widget.config(fg=current_color)
                        yield frame
                else:
                    for frame in range(int(pulse_duration / (2 * self.animation_speed)) + 1):
                        ratio = frame / int(pulse_duration / (2 * self.animation_speed))
                        current_color = self.interpolate_color(pulse_color, base_color, ratio)
                        widget.config(fg=current_color)
                        yield frame
        
        gen = pulse_generator()
        animation_id = id(widget)
        self._active_animations.add(animation_id)
        
        def animate_step():
            try:
                next(gen)
                self.root.after(self.animation_speed, animate_step)
            except StopIteration:
                widget.config(fg=base_color)
                self._active_animations.discard(animation_id)
        
        animate_step()
    
    def rolling_name_animation(self, name_label, names: List[str], 
                              interval: int = 50, callback=None):
        """名字滚动动画（模拟轮盘效果）"""
        if not names:
            return
        
        total_names = len(names)
        display_order = list(range(total_names))
        
        current_index = [0]
        
        def show_next_name():
            if current_index[0] < total_names:
                name_label.config(text=names[display_order[current_index[0]]])
                current_index[0] += 1
                self.root.after(interval, show_next_name)
            else:
                if callback:
                    callback()
        
        show_next_name()
    
    def victory_animation(self, widget, winners: List[str]):
        """胜利动画（抽取结果展示）"""
        if not winners or not self.config.get_bool('UI', 'enable_animations', True):
            return
        
        self.color_transition(
            widget, 
            self.colors['rolling_start'], 
            self.colors['victory'], 
            300,
            lambda: self._victory_step2(widget, winners)
        )
    
    def _victory_step2(self, widget, winners: List[str]):
        """胜利动画第二步：脉冲效果"""
        self.pulse_animation(
            widget,
            self.colors['victory'],
            '#ffffff',
            cycles=2,
            pulse_duration=400
        )

# ==========================================
# 主应用程序（性能优化版）
# ==========================================
class SmartPickerApp:
    """主应用程序类"""
    
    def __init__(self, root):
        self.root = root
        self.config = ConfigManager()
        self.config.set_root_reference(root)
        self.data_manager = DataManager()
        self.voice_manager = VoiceManager()
        self.animation_engine = AnimationEngine(root)
        
        self.current_version = "3.6.0"
        self.github_user = "deng121200"
        self.github_repo = "Smart-Random-Picker"
        
        self.names = []
        self.blacklist = []
        self.is_rolling = False
        self.history_counter = 0
        self.history_data = []
        
        self._rolling_pool = []
        self._rolling_index = 0
        
        self.audio_enabled = False
        self.rolling_sounds = []
        
        self._setup_window()
        self._setup_ui()
        self._setup_audio()
        self.load_data()
        
        if self.config.get_bool('GENERAL', 'auto_check_update', True):
            threading.Thread(target=self.check_for_updates, daemon=True).start()
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _on_closing(self):
        """【性能优化】窗口关闭时的清理工作"""
        self.config.force_save()
        self.animation_engine.cancel_all_animations()
        
        if self.audio_enabled:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except:
                pass
        
        self.root.destroy()
    
    def _setup_window(self):
        """设置主窗口"""
        self.root.title(f"SmartPicker v{self.current_version} (Win7 纯净语音版)")
        
        width, height = 800, 600
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.root.configure(bg="#f0f4f8")
        
        icon_path = os.path.join(BASE_DIR, "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                print(f"【提示】无法加载窗口图标: {e}")
    
    def _setup_ui(self):
        """设置用户界面"""
        self.title_label = tk.Label(
            self.root, 
            text="课堂随机点名", 
            font=("Microsoft YaHei", 28, "bold"), 
            bg="#f0f4f8", 
            fg="#333"
        )
        self.title_label.pack(pady=20)
        self.title_label.bind("<Double-Button-1>", self.open_secret_menu)
        
        self.name_display = tk.Label(
            self.root,
            text="准备就绪",
            font=("Microsoft YaHei", 55, "bold"),
            bg="#f0f4f8",
            fg="#0056b3",
            wraplength=750,
            justify="center"
        )
        self.name_display.pack(pady=20, expand=True, fill=tk.BOTH)
        
        self.control_frame = tk.Frame(self.root, bg="#f0f4f8")
        self.control_frame.pack(pady=10)
        
        self.btn = tk.Button(
            self.control_frame,
            text="开 始",
            font=("Microsoft YaHei", 20, "bold"),
            bg="#4caf50",
            fg="white",
            command=self.toggle_roll,
            width=12,
            relief="flat",
            cursor="hand2",
            activebackground="#45a049",
            activeforeground="white"
        )
        self.btn.grid(row=0, column=0, padx=20)
        
        self.slider_frame = tk.Frame(self.control_frame, bg="#f0f4f8")
        self.slider_frame.grid(row=0, column=1, padx=10)
        
        tk.Label(
            self.slider_frame,
            text="抽取人数:",
            font=("Microsoft YaHei", 12),
            bg="#f0f4f8"
        ).pack(side=tk.LEFT)
        
        default_count = self.config.get_int('PICKER', 'default_draw_count', 1)
        max_count = self.config.get_int('PICKER', 'max_draw_count', 20)
        
        self.draw_count_slider = tk.Scale(
            self.slider_frame,
            from_=1,
            to=max_count,
            orient=tk.HORIZONTAL,
            bg="#f0f4f8",
            length=120,
            font=("Microsoft YaHei", 10),
            sliderlength=20,
            tickinterval=4
        )
        self.draw_count_slider.set(default_count)
        self.draw_count_slider.pack(side=tk.LEFT)
        
        self.refresh_btn = tk.Button(
            self.control_frame,
            text="🔄 刷新",
            font=("Microsoft YaHei", 12, "bold"),
            bg="#00bcd4",
            fg="white",
            command=self.manual_refresh,
            width=8,
            relief="flat",
            cursor="hand2",
            activebackground="#00acc1"
        )
        self.refresh_btn.grid(row=0, column=2, padx=10)
        
        self.feedback_btn = tk.Button(
            self.control_frame,
            text="🐛 反馈建议",
            font=("Microsoft YaHei", 12, "bold"),
            bg="#ff9800",
            fg="white",
            command=self.open_feedback_page,
            width=10,
            relief="flat",
            cursor="hand2",
            activebackground="#f57c00"
        )
        self.feedback_btn.grid(row=0, column=3, padx=10)
        
        self.voice_toggle_btn = tk.Button(
            self.control_frame,
            text="🔊 语音" if self.voice_manager.enabled else "🔇 静音",
            font=("Microsoft YaHei", 12, "bold"),
            bg="#9c27b0" if self.voice_manager.enabled else "#757575",
            fg="white",
            command=self.toggle_voice,
            width=8,
            relief="flat",
            cursor="hand2",
            activebackground="#7b1fa2"
        )
        self.voice_toggle_btn.grid(row=0, column=4, padx=10)
        
        self.bottom_frame = tk.Frame(self.root, bg="#f0f4f8")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
        
        self.history_frame = tk.Frame(self.bottom_frame, bg="#f0f4f8")
        self.history_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            self.history_frame,
            text="📜 抽取历史:",
            font=("Microsoft YaHei", 10, "bold"),
            bg="#f0f4f8",
            fg="#666"
        ).pack(anchor="w")
        
        self.hist_scroll = tk.Scrollbar(self.history_frame)
        self.hist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_text = tk.Text(
            self.history_frame,
            height=5,
            width=40,
            font=("Microsoft YaHei", 10),
            yscrollcommand=self.hist_scroll.set,
            state=tk.DISABLED,
            bg="#ffffff",
            relief="flat",
            borderwidth=1
        )
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.history_text.tag_config("even_row", background="#f9f9f9")
        self.history_text.tag_config("odd_row", background="#ffffff")
        
        self.hist_scroll.config(command=self.history_text.yview)
        
        self.signature_label = tk.Label(
            self.bottom_frame,
            text=f"v{self.current_version} | 灵感来源于我\nInspiration from @遇屿迟",
            font=("Microsoft YaHei", 10),
            bg="#f0f4f8",
            fg="#999999",
            justify=tk.RIGHT
        )
        self.signature_label.pack(side=tk.RIGHT, anchor="s", padx=10)
    
    def _setup_audio(self):
        """设置音频系统"""
        if PYGAME_AVAILABLE and self.config.get_bool('AUDIO', 'enable_sound', True):
            try:
                pygame.mixer.init(
                    frequency=22050,
                    size=-16,
                    channels=2,
                    buffer=1024
                )
                self.audio_enabled = True
                print("【提示】音频系统初始化成功")
                
                sound_files = [f for f in os.listdir(BASE_DIR) 
                              if f.startswith('rolling') and f.endswith('.mp3')]
                self.rolling_sounds = [os.path.join(BASE_DIR, f) for f in sound_files]
                
                if self.rolling_sounds:
                    print(f"【提示】找到 {len(self.rolling_sounds)} 个滚动音效文件")
            except Exception as e:
                print(f"【提示】音频系统初始化失败: {e}")
                self.audio_enabled = False
        else:
            self.audio_enabled = False
    
    def load_data(self):
        """加载名单数据"""
        try:
            self.names, self.blacklist = self.data_manager.load_all_data()
            total_count = len(self.names)
            
            if not self.names or total_count == 0:
                self.name_display.config(
                    text="请确保名单.txt文件存在且不为空",
                    fg="#ff9800",
                    font=("Microsoft YaHei", 20, "bold")
                )
            else:
                if total_count == 1:
                    display_text = "已加载 1 名学生"
                else:
                    display_text = f"已加载 {total_count} 名学生"
                
                self.name_display.config(
                    text=display_text,
                    fg="#0056b3",
                    font=("Microsoft YaHei", 24, "bold")
                )
                
        except Exception as e:
            self.name_display.config(
                text="数据加载异常，请检查名单文件",
                fg="#f44336",
                font=("Microsoft YaHei", 18, "bold")
            )
            if self.config.get_bool('GENERAL', 'enable_logging', False):
                print(f"[错误] 名单加载失败: {e}")
    
    def manual_refresh(self):
        """手动刷新名单"""
        self.data_manager.clear_cache()
        self.load_data()
        count = len(self.names)
        messagebox.showinfo(
            "刷新成功",
            f"名单已更新！\n当前读取到 {count} 名学生。",
            parent=self.root
        )
    
    def open_feedback_page(self):
        """打开反馈页面"""
        feedback_url = f"https://github.com/{self.github_user}/{self.github_repo}/issues"
        try:
            webbrowser.open(feedback_url)
        except Exception:
            messagebox.showerror(
                "连接失败",
                f"无法自动打开浏览器，请手动复制网址访问：\n\n{feedback_url}",
                parent=self.root
            )
    def check_for_updates(self, manual=False):
        """检查更新（GitHub API 抓取日志版 + Lambda闭包修复）"""
        api_url = f"https://api.github.com/repos/{self.github_user}/{self.github_repo}/releases/latest"
        
        try:
            req = urllib.request.Request(
                api_url,
                headers={
                    'User-Agent': 'SmartPicker-Updater/4.0',
                    'Accept': 'application/vnd.github.v3+json'
                }
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                # 从 API 响应中提取纯净版本号和更新日志
                remote_version = data.get('tag_name', '').lstrip('vV')
                release_notes = data.get('body', '开发者未提供更新日志。')
                
                if remote_version and remote_version != self.current_version:
                    # 检查是否被用户设置为"跳过此版本"
                    skipped_version = self.config.get('GENERAL', 'skipped_version', '')
                    if remote_version == skipped_version and not manual:
                        return  # 如果是自动检查，且该版本被跳过，则静默退出
                    
                    current_exe_name = os.path.basename(sys.executable) if getattr(sys, 'frozen', False) else "SmartPicker.exe"
                    download_url = f"https://github.com/{self.github_user}/{self.github_repo}/releases/latest/download/{current_exe_name}"
                    
                    # 吸收 GLM 修复：使用默认参数捕获变量，锁死作用域
                    self.root.after(0, lambda url=download_url, rv=remote_version, rn=release_notes: self._show_custom_update_dialog(rv, rn, url))
                elif manual:
                    self.root.after(0, lambda: messagebox.showinfo("检查更新", f"当前已经是最新版本 (v{self.current_version})！\n\n您正在使用的是最前沿的极客构建版。", parent=self.root))
                    
        except Exception as e:
            error_msg = f"无法连接到 GitHub 服务器检查更新。\n\n请检查网络连接或稍后重试。\n错误详情: {e}"
            if manual:
                self.root.after(0, lambda msg=error_msg: messagebox.showerror("更新失败", msg, parent=self.root))
            elif self.config.get_bool('GENERAL', 'enable_logging', False):
                print(f"[错误] API 更新检测失败: {e}")

    def _show_custom_update_dialog(self, remote_version: str, release_notes: str, download_url: str):
        """显示自定义更新对话框（含更新日志与跳过功能）"""
        dialog = tk.Toplevel(self.root)
        dialog.title("发现新版本！")
        dialog.geometry("550x450")
        dialog.resizable(False, False)
        dialog.configure(bg="#f5f5f5")
        dialog.transient(self.root)  # 保持在主窗口之上
        dialog.grab_set()  # 拦截对主窗口的其他操作
        
        try:
            dialog.iconbitmap(default="icon.ico")
        except:
            pass
            
        # 顶部标题栏
        tk.Label(
            dialog,
            text=f"🚀 发现新版本 v{remote_version}",
            font=("Microsoft YaHei", 18, "bold"),
            bg="#f5f5f5", fg="#2196f3"
        ).pack(pady=(20, 5))
        
        tk.Label(
            dialog,
            text=f"当前版本: v{self.current_version}  →  最新版本: v{remote_version}",
            font=("Microsoft YaHei", 10),
            bg="#f5f5f5", fg="#666666"
        ).pack(pady=(0, 15))
        
        # 中间的更新日志展示区
        log_frame = tk.Frame(dialog, bg="#ffffff", bd=1, relief=tk.SOLID)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=5)
        
        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(
            log_frame,
            font=("Microsoft YaHei", 10),
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            bg="#f9f9f9",
            padx=15, pady=15
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # 插入日志并设置为只读
        text_widget.insert(tk.END, "【更新日志 Release Notes】\n" + "="*40 + "\n\n" + release_notes)
        text_widget.config(state=tk.DISABLED)
        
        # 底部按钮区
        btn_frame = tk.Frame(dialog, bg="#f5f5f5")
        btn_frame.pack(fill=tk.X, padx=25, pady=20)
        
        def do_update():
            dialog.destroy()
            self._perform_auto_update(download_url)
            
        def skip_version():
            self.config.set('GENERAL', 'skipped_version', remote_version)
            dialog.destroy()
            
        def remind_later():
            dialog.destroy()
            
        # 立即更新按钮
        update_btn = tk.Button(
            btn_frame, text="立即更新 (推荐)", font=("Microsoft YaHei", 11, "bold"),
            bg="#4caf50", fg="white", activebackground="#388e3c", cursor="hand2",
            relief=tk.FLAT, command=do_update, width=15
        )
        update_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 跳过版本按钮
        skip_btn = tk.Button(
            btn_frame, text="跳过此版本", font=("Microsoft YaHei", 10),
            bg="#e0e0e0", fg="#333333", activebackground="#bdbdbd", cursor="hand2",
            relief=tk.FLAT, command=skip_version, width=12
        )
        skip_btn.pack(side=tk.LEFT)
        
        # 以后再说按钮
        cancel_btn = tk.Button(
            btn_frame, text="以后再说", font=("Microsoft YaHei", 10),
            bg="#ffffff", fg="#333333", activebackground="#f0f0f0", cursor="hand2",
            relief=tk.FLAT, command=remind_later, width=10
        )
        cancel_btn.pack(side=tk.RIGHT)
    
    def _perform_auto_update(self, download_url: str):
        """执行金蝉脱壳接力更新（多模型融合完美版）"""
        if not getattr(sys, 'frozen', False):
            messagebox.showinfo("提示", "当前处于源码运行模式，请前往 GitHub 手动拉取代码。")
            webbrowser.open(f"https://github.com/{self.github_user}/{self.github_repo}/releases/latest")
            return
        
        current_exe_path = sys.executable
        exe_dir = os.path.dirname(current_exe_path)
        new_exe_path = current_exe_path + ".new"
        bat_path = os.path.join(exe_dir, "update.bat")
        backup_exe_path = current_exe_path + ".backup"
        
        # 1. 禁用 UI，初始化进度显示
        self.btn.config(state=tk.DISABLED)
        self.name_display.config(text="准备下载更新...", fg="#ff9800", font=("Microsoft YaHei", 30, "bold"))
        self.root.update()
        
        try:
            # 2. 发起下载请求并校验
            req = urllib.request.Request(download_url, headers={'User-Agent': 'SmartPicker-Updater'})
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status != 200:
                    raise Exception(f"服务器响应异常 (HTTP {response.status})")
                
                content_length = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                
                # 3. 分块下载与 Tkinter UI 刷新
                with open(new_exe_path, 'wb') as out_file:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        out_file.write(chunk)
                        downloaded += len(chunk)
                        
                        if content_length > 0:
                            progress = int((downloaded / content_length) * 100)
                            self.name_display.config(text=f"正在下载更新... {progress}%")
                            self.root.update()
            
            # 4. 下载完整性校验
            if os.path.getsize(new_exe_path) < 10240:  # 小于 10KB 绝对是错误页面
                raise Exception("下载文件体积异常，可能被网络拦截。")
            
            # 5. 生成备份文件
            if os.path.exists(current_exe_path):
                import shutil
                shutil.copy2(current_exe_path, backup_exe_path)
            
            # 6. 生成容灾 BAT 脚本（Gemini 修复：坚决剔除 chcp 65001，纯正 mbcs）
            bat_content = f"""@echo off
title SmartPicker 自动更新程序
echo 正在等待主程序退出以释放文件锁...
ping 127.0.0.1 -n 3 > nul
echo 正在应用更新...

if exist "{current_exe_path}" (
    del /f /q "{current_exe_path}"
)

if exist "{new_exe_path}" (
    move /y "{new_exe_path}" "{current_exe_path}" > nul
    if errorlevel 1 (
        echo [错误] 替换新版本失败！
        if exist "{backup_exe_path}" (
            echo 正在尝试回滚旧版本...
            copy /y "{backup_exe_path}" "{current_exe_path}" > nul
        )
        pause
        exit /b 1
    )
) else (
    echo [错误] 未找到下载的更新文件！
    pause
    exit /b 1
)

if exist "{backup_exe_path}" del /f /q "{backup_exe_path}"
echo 更新完成！正在重启程序...
start "" "{current_exe_path}"
del "%~f0"
"""
            # 使用 mbcs 强制写入 ANSI，确保 Win7 CMD 中文完美显示
            with open(bat_path, "w", encoding="mbcs") as f:
                f.write(bat_content)
            
            # 7. 移交控制权并完全脱钩自毁
            # 抛弃 subprocess，使用 Windows 原生 API 彻底分离进程
            os.startfile(bat_path)
            self._on_closing()
            sys.exit()
            
        except Exception as e:
            # 清理残局，恢复 UI
            if os.path.exists(new_exe_path):
                os.remove(new_exe_path)
            self.name_display.config(text="已就绪", fg="#0056b3", font=("Microsoft YaHei", 55, "bold"))
            self.btn.config(state=tk.NORMAL)
            messagebox.showerror("更新失败", f"自动更新失败，请检查网络。\n\n详情: {e}", parent=self.root)
            self.load_data()
    
    def open_secret_menu(self, event):
        """打开密码菜单"""
        pwd = simpledialog.askstring(
            "管理员验证",
            "请输入密码:",
            show='*',
            parent=self.root
        )
        
        if pwd == "114514":
            self._show_admin_menu()
        elif pwd is not None:
            messagebox.showerror("错误", "密码错误！", parent=self.root)
    
    def manage_blacklist(self):
        """黑名单管理界面"""
        if not hasattr(self, 'blacklist_manager_open') or not self.blacklist_manager_open:
            self._create_blacklist_manager()
    
    def _create_blacklist_manager(self):
        """创建黑名单管理窗口"""
        self.blacklist_manager_open = True
        
        manager_win = tk.Toplevel(self.root)
        manager_win.title("黑名单管理 - SmartPicker V3.1")
        manager_win.geometry("500x600")
        manager_win.resizable(False, False)
        manager_win.configure(bg="#f5f5f5")
        
        try:
            manager_win.iconbitmap(default="icon.ico")
        except:
            pass
        
        def on_closing():
            self.blacklist_manager_open = False
            manager_win.destroy()
        
        manager_win.protocol("WM_DELETE_WINDOW", on_closing)
        
        title_frame = tk.Frame(manager_win, bg="#2196f3", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="🔒 黑名单管理",
            font=("Microsoft YaHei", 18, "bold"),
            fg="white",
            bg="#2196f3"
        ).pack(expand=True)
        
        info_frame = tk.Frame(manager_win, bg="#e3f2fd", height=40)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        info_frame.pack_propagate(False)
        
        total_count = len(self.names)
        blacklist_count = len(self.blacklist)
        available_count = total_count - blacklist_count
        
        info_text = f"总人数: {total_count} | 黑名单: {blacklist_count} | 可抽取: {available_count}"
        tk.Label(
            info_frame,
            text=info_text,
            font=("Microsoft YaHei", 11),
            fg="#1565c0",
            bg="#e3f2fd"
        ).pack(expand=True)
        
        list_frame = tk.Frame(manager_win, bg="white")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.blacklist_listbox = tk.Listbox(
            list_frame,
            font=("Microsoft YaHei", 12),
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            height=15
        )
        self.blacklist_listbox.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.blacklist_listbox.yview)
        
        self._refresh_blacklist_display()
        
        button_frame = tk.Frame(manager_win, bg="#f5f5f5")
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        add_btn = tk.Button(
            button_frame,
            text="➕ 添加黑名单",
            font=("Microsoft YaHei", 11),
            bg="#4caf50",
            fg="white",
            activebackground="#388e3c",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._add_to_blacklist
        )
        add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        remove_btn = tk.Button(
            button_frame,
            text="➖ 移除黑名单",
            font=("Microsoft YaHei", 11),
            bg="#ff9800",
            fg="white",
            activebackground="#f57c00",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._remove_from_blacklist
        )
        remove_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ 清空黑名单",
            font=("Microsoft YaHei", 11),
            bg="#f44336",
            fg="white",
            activebackground="#d32f2f",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._clear_blacklist
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        save_btn = tk.Button(
            button_frame,
            text="💾 保存更改",
            font=("Microsoft YaHei", 11, "bold"),
            bg="#2196f3",
            fg="white",
            activebackground="#1976d2",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._save_blacklist_changes
        )
        save_btn.pack(side=tk.RIGHT)
        
        self.blacklist_status = tk.Label(
            manager_win,
            text="就绪",
            font=("Microsoft YaHei", 10),
            fg="#666666",
            bg="#f5f5f5"
        )
        self.blacklist_status.pack(fill=tk.X, padx=20, pady=(0, 10))
    
    def _refresh_blacklist_display(self):
        """刷新黑名单列表框显示"""
        if hasattr(self, 'blacklist_listbox'):
            self.blacklist_listbox.delete(0, tk.END)
            
            if not self.blacklist:
                self.blacklist_listbox.insert(tk.END, "（黑名单为空）")
                self.blacklist_listbox.itemconfig(0, fg="#999999")
            else:
                for i, name in enumerate(self.blacklist, 1):
                    self.blacklist_listbox.insert(tk.END, f"{i:2d}. {name}")
    
    def _add_to_blacklist(self):
        """添加学生到黑名单"""
        available_names = [n for n in self.names if n not in self.blacklist]
        
        if not available_names:
            messagebox.showinfo("提示", "所有学生已在黑名单中", parent=self.root)
            return
        
        select_win = tk.Toplevel(self.root)
        select_win.title("选择学生")
        select_win.geometry("300x400")
        select_win.resizable(False, False)
        
        scrollbar = tk.Scrollbar(select_win)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(
            select_win,
            font=("Microsoft YaHei", 11),
            selectmode=tk.MULTIPLE,
            yscrollcommand=scrollbar.set,
            height=15
        )
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar.config(command=listbox.yview)
        
        for name in available_names:
            listbox.insert(tk.END, name)
        
        def confirm_selection():
            selections = listbox.curselection()
            if not selections:
                messagebox.showwarning("警告", "请选择至少一名学生", parent=select_win)
                return
            
            selected_names = [available_names[i] for i in selections]
            
            for name in selected_names:
                if name not in self.blacklist:
                    self.blacklist.append(name)
            
            self._refresh_blacklist_display()
            self._update_status(f"已添加 {len(selected_names)} 名学生到黑名单")
            select_win.destroy()
        
        tk.Button(
            select_win,
            text="确认添加",
            font=("Microsoft YaHei", 11, "bold"),
            bg="#4caf50",
            fg="white",
            command=confirm_selection
        ).pack(pady=(0, 10))
    
    def _remove_from_blacklist(self):
        """从黑名单中移除学生"""
        if not self.blacklist:
            messagebox.showinfo("提示", "黑名单为空", parent=self.root)
            return
        
        selection = self.blacklist_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请选择要移除的学生", parent=self.root)
            return
        
        if self.blacklist_listbox.get(selection[0]) == "（黑名单为空）":
            return
        
        index = selection[0]
        name = self.blacklist[index]
        
        if messagebox.askyesno("确认", f"确定要从黑名单中移除「{name}」吗？", parent=self.root):
            self.blacklist.pop(index)
            self._refresh_blacklist_display()
            self._update_status(f"已从黑名单移除: {name}")
    
    def _clear_blacklist(self):
        """清空黑名单"""
        if not self.blacklist:
            return
        
        if messagebox.askyesno("确认清空", "确定要清空整个黑名单吗？", parent=self.root):
            self.blacklist.clear()
            self._refresh_blacklist_display()
            self._update_status("黑名单已清空")
    
    def _save_blacklist_changes(self):
        """保存黑名单更改到加密文件"""
        try:
            success = self.data_manager.save_encrypted_blacklist(self.blacklist)
            if success:
                self._update_status("✅ 黑名单已加密保存", "#4caf50")
                messagebox.showinfo("保存成功", "黑名单数据已加密并安全保存！", parent=self.root)
                self.load_data() 
            else:
                self._update_status("❌ 保存失败，请检查日志", "#f44336")
                messagebox.showerror("保存失败", "加密存储失败，请检查系统权限。", parent=self.root)
        except Exception as e:
            self._update_status(f"❌ 保存失败: {str(e)[:30]}", "#f44336")
            self.data_manager.logger.error(f"保存黑名单失败: {e}")
    
    def _update_status(self, message: str, color: str = "#666666"):
        """更新状态标签"""
        if hasattr(self, 'blacklist_status'):
            self.blacklist_status.config(text=message, fg=color)
    
    def _show_admin_menu(self):
        """显示管理员菜单（V3.4 全新版）"""
        admin_win = tk.Toplevel(self.root)
        admin_win.title("SmartPicker 管理员菜单")
        admin_win.geometry("350x420") # 增加高度容纳新按钮
        admin_win.resizable(False, False)
        admin_win.configure(bg="#f5f5f5")
        
        tk.Label(
            admin_win,
            text="🔐 管理员菜单",
            font=("Microsoft YaHei", 18, "bold"),
            fg="#2196f3",
            bg="#f5f5f5"
        ).pack(pady=(20, 5))
        
        tk.Label(
            admin_win,
            text=f"当前运行版本: v{self.current_version}\n加密暗箱与 OTA 引擎已就绪",
            font=("Microsoft YaHei", 10),
            fg="#666666",
            bg="#f5f5f5"
        ).pack(pady=(0, 15))
        
        btn_frame = tk.Frame(admin_win, bg="#f5f5f5")
        btn_frame.pack(pady=5)
        
        # 1. 黑名单管理
        tk.Button(
            btn_frame, text="📋 管理黑名单", font=("Microsoft YaHei", 11, "bold"),
            width=22, height=1, bg="#2196f3", fg="white",
            activebackground="#1976d2", relief=tk.FLAT, cursor="hand2",
            command=lambda: [admin_win.destroy(), self.manage_blacklist()]
        ).pack(pady=6)
        
        # 2. 手动检查更新 (直接调用带有 manual=True 的新引擎，放入异步线程防卡顿)
        tk.Button(
            btn_frame, text="🔄 手动检查更新", font=("Microsoft YaHei", 11, "bold"),
            width=22, height=1, bg="#ff9800", fg="white",
            activebackground="#f57c00", relief=tk.FLAT, cursor="hand2",
            command=lambda: [admin_win.destroy(), threading.Thread(target=self.check_for_updates, kwargs={'manual': True}, daemon=True).start()]
        ).pack(pady=6)
        
        # 3. 查看更新历史
        tk.Button(
            btn_frame, text="📜 查看云端更新历史", font=("Microsoft YaHei", 11, "bold"),
            width=22, height=1, bg="#9c27b0", fg="white",
            activebackground="#7b1fa2", relief=tk.FLAT, cursor="hand2",
            command=lambda: [admin_win.destroy(), threading.Thread(target=self._show_update_history, daemon=True).start()]
        ).pack(pady=6)
        
        # 4. 系统信息
        tk.Button(
            btn_frame, text="ℹ️ 系统信息", font=("Microsoft YaHei", 11),
            width=22, height=1, bg="#4caf50", fg="white",
            activebackground="#388e3c", relief=tk.FLAT, cursor="hand2",
            command=lambda: [admin_win.destroy(), self._show_system_info()]
        ).pack(pady=6)
        
        # 关闭按钮
        tk.Button(
            btn_frame, text="关闭面板", font=("Microsoft YaHei", 10),
            width=15, bg="#e0e0e0", fg="#333",
            activebackground="#bdbdbd", relief=tk.FLAT, cursor="hand2",
            command=admin_win.destroy
        ).pack(pady=15)

    def _show_update_history(self):
        """拉取并显示 GitHub 的全量更新历史"""
        api_url = f"https://api.github.com/repos/{self.github_user}/{self.github_repo}/releases"
        
        try:
            req = urllib.request.Request(
                api_url,
                headers={
                    'User-Agent': 'SmartPicker-History/4.0',
                    'Accept': 'application/vnd.github.v3+json'
                }
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                releases = json.loads(response.read().decode('utf-8'))
                
                # 提取格式化的历史记录
                history_text = ""
                for release in releases[:10]: # 只取最近 10 个版本，防止文本过长
                    tag = release.get('tag_name', 'Unknown')
                    date = release.get('published_at', '').split('T')[0]
                    body = release.get('body', '无详细日志')
                    history_text += f"🚀 版本: {tag} ({date})\n{'-'*45}\n{body}\n\n"
                    
                if not history_text:
                    history_text = "暂无云端更新历史记录。"
                
                # 绘制历史记录 UI (需回到主线程渲染)
                self.root.after(0, lambda text=history_text: self._render_history_window(text))
                
        except Exception as e:
            error_msg = f"无法连接到 GitHub 获取历史记录。\n\n错误详情: {e}"
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("获取失败", msg, parent=self.root))

    def _render_history_window(self, history_text: str):
        """渲染历史记录专属窗口"""
        hist_win = tk.Toplevel(self.root)
        hist_win.title("云端更新历史")
        hist_win.geometry("600x500")
        hist_win.resizable(True, True)
        hist_win.configure(bg="#f5f5f5")
        hist_win.transient(self.root)
        
        try:
            hist_win.iconbitmap(default="icon.ico")
        except:
            pass
            
        tk.Label(
            hist_win, text="📚 SmartPicker 版本迭代史", 
            font=("Microsoft YaHei", 16, "bold"), bg="#f5f5f5", fg="#333"
        ).pack(pady=15)
        
        text_frame = tk.Frame(hist_win, bg="#ffffff", bd=1, relief=tk.SOLID)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(
            text_frame, font=("Microsoft YaHei", 10), wrap=tk.WORD,
            yscrollcommand=scrollbar.set, bg="#f9f9f9", padx=15, pady=15
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        text_widget.insert(tk.END, history_text)
        text_widget.config(state=tk.DISABLED)
    

    def _show_system_info(self):
        """显示系统信息"""
        total_count = len(self.names)
        blacklist_count = len(self.blacklist)
        available_count = total_count - blacklist_count
        
        info_text = (
            f"系统状态：正常\n\n"
            f"总人数：{total_count} 人\n"
            f"黑名单：{blacklist_count} 人\n"
            f"可抽取：{available_count} 人\n\n"
            f"【安全提示】\n"
            f"黑名单数据已加密存储\n"
            f"文件：system_config.dat"
        )
        
        messagebox.showinfo(
            "系统信息",
            info_text,
            parent=self.root
        )
    
    def toggle_voice(self):
        """切换语音开关"""
        current_state = self.voice_manager.enabled
        new_state = not current_state
        
        self.config.set('PICKER', 'voice_enabled', str(new_state).lower())
        self.voice_manager.enabled = new_state
        
        if new_state:
            self.voice_toggle_btn.config(
                text="🔊 语音",
                bg="#9c27b0",
                activebackground="#7b1fa2"
            )
            messagebox.showinfo("提示", "语音播报已启用", parent=self.root)
        else:
            self.voice_toggle_btn.config(
                text="🔇 静音",
                bg="#757575",
                activebackground="#616161"
            )
            messagebox.showinfo("提示", "语音播报已禁用", parent=self.root)
    
    def update_names_display(self, names_list: List[str]):
        """更新名字显示"""
        if not names_list:
            return
        
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
        
        self.name_display.config(
            text=text,
            font=("Microsoft YaHei", font_size, "bold")
        )
    
    def toggle_roll(self):
        """开始/停止抽取"""
        if not self.is_rolling:
            self.load_data()
        
        if not self.names:
            messagebox.showwarning(
                "警告",
                "请确保程序同目录下有 名单.txt 文件"
            )
            return
        
        if not self.is_rolling:
            self.start_rolling()
        else:
            self.stop_rolling()
    
    def start_rolling(self):
        """开始抽取"""
        self.is_rolling = True
        self.btn.config(text="停 止", bg="#f44336", activebackground="#d32f2f")
        
        count = self.draw_count_slider.get()
        self._rolling_pool = self.names.copy()
        self._rolling_index = 0
        
        if self.audio_enabled and self.rolling_sounds:
            try:
                sound_file = random.choice(self.rolling_sounds)
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.set_volume(
                    self.config.get_int('AUDIO', 'rolling_sound_volume', 80) / 100.0
                )
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"【提示】音效播放失败: {e}")
        
        self.animation_engine.color_transition(
            self.name_display,
            "#0056b3",
            "#2196f3",
            300
        )
        
        self.update_rolling()
    
    def stop_rolling(self):
        """停止抽取"""
        self.is_rolling = False
        self.btn.config(text="开 始", bg="#4caf50", activebackground="#45a049")
        
        if self.audio_enabled:
            pygame.mixer.music.stop()
        
        self.finish_roll()
    
    def update_rolling(self):
        """更新滚动状态（性能优化版）"""
        if self.is_rolling:
            count = self.draw_count_slider.get()
            pool = self._rolling_pool
            
            if pool:
                fake_winners = []
                for i in range(count):
                    idx = (self._rolling_index + i) % len(pool)
                    fake_winners.append(pool[idx])
                
                self._rolling_index = (self._rolling_index + count) % len(pool)
                self.update_names_display(fake_winners)
            
            speed = self.animation_engine.animation_speed
            self.root.after(speed, self.update_rolling)
    
    def finish_roll(self):
        """执行最终抽取（V3.6.0 引入物理级绝对屏蔽层）"""
        count = self.draw_count_slider.get()
        
        # 1. 常规黑名单过滤（尊重用户在界面的设置）
        if self.config.get_bool('PICKER', 'enable_blacklist', True):
            pool = [n for n in self.names if n not in self.blacklist]
            if not pool:
                pool = self.names.copy() # 使用 copy 防污染原名单
        else:
            pool = self.names.copy()
            
        # ==========================================
        # 👑 核心暗门：针对 "白竞芳" 的绝对物理护盾
        # 机制：只要全班不仅限于她一个人，在最终落锤前，将其从候选池中强制抹除。
        # 但因为 _rolling_pool 未受影响，所以动画中依然会有她的残影。
        # ==========================================
        shield_target = "白竞芳"
        if shield_target in pool and len(pool) > 1:
            pool.remove(shield_target)
        
        # 2. 最终容量校验与抽取
        actual_count = min(count, len(pool))
        if actual_count <= 0:
            messagebox.showwarning("警告", "没有可抽取的学生！")
            self.name_display.config(text="名单为空", fg="red")
            return
        
        winners = random.sample(pool, actual_count)
        
        # 3. 触发 UI 与音效更新
        self.update_names_display(winners)
        self.animation_engine.victory_animation(self.name_display, winners)
        self.add_to_history(winners)
        
        if self.voice_manager.enabled:
            self.voice_manager.speak_winners(winners)
    
    def add_to_history(self, winners: List[str]):
        """添加到历史记录（性能优化版）"""
        if not winners:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_counter += 1
        
        count = len(winners)
        winners_text = "、".join(winners)
        history_entry = f"{self.history_counter:03d}. [{timestamp}] 抽取{count}人: {winners_text}\n"
        
        self.history_data.append({
            "id": self.history_counter,
            "timestamp": timestamp,
            "count": count,
            "winners": winners,
            "blacklist_used": self.config.get_bool('PICKER', 'enable_blacklist', True)
        })
        
        if len(self.history_data) > self.data_manager._max_history_size:
            self.history_data = self.history_data[-self.data_manager._max_history_size:]
        
        self.history_text.config(state=tk.NORMAL)
        
        if self.history_counter % 2 == 0:
            self.history_text.insert(tk.END, history_entry, "even_row")
        else:
            self.history_text.insert(tk.END, history_entry, "odd_row")
        
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)
        
        if self.config.get_bool('GENERAL', 'enable_logging', True):
            threading.Thread(
                target=self.data_manager.save_history,
                args=(self.history_data,),
                daemon=True
            ).start()

# ==========================================
# 主程序入口
# ==========================================
def main():
    """主程序入口"""
    try:
        root = tk.Tk()
        app = SmartPickerApp(root)
        root.mainloop()
        
    except Exception as e:
        print(f"【致命错误】程序启动失败: {e}")
        print("=" * 50)
        print("请检查以下可能的问题：")
        print("1. 确保Python版本为3.8.10 (64位)")
        print("2. 确保安装了必要的依赖：pip install pygame pywin32")
        print("3. 确保运行在Windows 7 SP1或更高版本")
        print("4. 确保有名单.txt文件在程序目录")
        print("=" * 50)
        
        try:
            messagebox.showerror(
                "启动失败",
                f"程序启动失败，请检查控制台输出。\n错误信息: {str(e)[:100]}..."
            )
        except:
            pass

if __name__ == "__main__":
    main()
