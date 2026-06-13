#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SmartPicker Pro V5.0 - 全功能智慧课堂点名系统
【版本】5.0.0-Pro
【功能定位】集点名、考勤、统计、互动于一体的全能课堂管理工具
【环境要求】Python 3.8.10 (64位) + Windows 7 SP1
【作者】@遇屿迟
【核心特性】
- 多种抽取模式：普通抽取、加权抽取、随机抽取、分组抽取、竟答抽取
- 班级管理：多班级切换、学期管理、学生档案
- 考勤系统：出勤、请假、迟到、缺勤自动记录
- 数据统计：出勤率分析、点名历史、成绩趋势
- 互动功能：积分系统、奖惩记录、PK模式
- 自定义皮肤：多种主题、自定义背景
- 媒体支持：背景音乐、音效系统、视频背景
- 数据导出：Excel、CSV、PDF、截图分享
- 云同步：本地备份、云端同步（可选）
- 多语言：中文、英文、日文、韩文
"""

import tkinter as tk
from tkinter import ttk  # <--- 必须加上这致命的一行！
from tkinter import simpledialog, messagebox, font as tkfont, filedialog
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
import hashlib
import base64
import pickle
import sqlite3
import csv
import re
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Callable, Set
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
import struct
import zlib

# ==========================================
# 可选依赖导入
# ==========================================
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("[提示] pygame 未安装，音频功能将禁用")

try:
    import win32com.client
    WIN32COM_AVAILABLE = True
except ImportError:
    WIN32COM_AVAILABLE = False
    print("[提示] pywin32 未安装，语音播报功能将禁用")

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[提示] Pillow 未安装，高级图像功能将禁用")

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("[提示] matplotlib 未安装，图表功能将禁用")

try:
    from docx import Document
    from docx.shared import Inches, Pt
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("[提示] python-docx 未安装，Word导出将禁用")

# ==========================================
# 全局常量定义
# ==========================================
VERSION = "5.0.0"
APP_NAME = "SmartPicker Pro"
AUTHOR = "@遇屿迟"
SUPPORTED_LANGUAGES = ["简体中文", "English", "日本語", "한국어"]

# 主题颜色配置
THEMES = {
    "默认蓝色": {
        "primary": "#1976d2", "secondary": "#2196f3", "accent": "#64b5f6",
        "background": "#f5f5f5", "surface": "#ffffff", "text": "#333333",
        "success": "#4caf50", "warning": "#ff9800", "danger": "#f44336",
        "info": "#00bcd4"
    },
    "暗夜模式": {
        "primary": "#bb86fc", "secondary": "#3700b3", "accent": "#03dac6",
        "background": "#121212", "surface": "#1e1e1e", "text": "#e1e1e1",
        "success": "#00e676", "warning": "#ffab00", "danger": "#cf6679",
        "info": "#018786"
    },
    "森林绿": {
        "primary": "#2e7d32", "secondary": "#4caf50", "accent": "#81c784",
        "background": "#e8f5e9", "surface": "#ffffff", "text": "#1b5e20",
        "success": "#66bb6a", "warning": "#ffb300", "danger": "#ef5350",
        "info": "#26a69a"
    },
    "商务灰": {
        "primary": "#455a64", "secondary": "#607d8b", "accent": "#90a4ae",
        "background": "#eceff1", "surface": "#ffffff", "text": "#263238",
        "success": "#26a69a", "warning": "#ffa726", "danger": "#ef5350",
        "info": "#42a5f5"
    },
    "浪漫粉": {
        "primary": "#e91e63", "secondary": "#f06292", "accent": "#f8bbd9",
        "background": "#fce4ec", "surface": "#ffffff", "text": "#880e4f",
        "success": "#66bb6a", "warning": "#ffb74d", "danger": "#ef5350",
        "info": "#4dd0e1"
    },
    "活力橙": {
        "primary": "#ff5722", "secondary": "#ff7043", "accent": "#ffab91",
        "background": "#fff3e0", "surface": "#ffffff", "text": "#bf360c",
        "success": "#66bb6a", "warning": "#ffb300", "danger": "#d32f2f",
        "info": "#29b6f6"
    },
    "科技蓝": {
        "primary": "#00bcd4", "secondary": "#26c6da", "accent": "#80deea",
        "background": "#e0f7fa", "surface": "#ffffff", "text": "#006064",
        "success": "#66bb6a", "warning": "#ffca28", "danger": "#ef5350",
        "info": "#42a5f5"
    },
    "清新绿": {
        "primary": "#8bc34a", "secondary": "#9ccc65", "accent": "#c5e1a5",
        "background": "#f1f8e9", "surface": "#ffffff", "text": "#33691e",
        "success": "#7cb342", "warning": "#ffc107", "danger": "#ff7043",
        "info": "#26a69a"
    }
}

# 抽取模式枚举
class DrawMode(Enum):
    NORMAL = auto()      # 普通抽取
    WEIGHTED = auto()    # 加权抽取
    RANDOM = auto()      # 完全随机
    GROUP = auto()       # 分组抽取
    CONTEST = auto()     # 竞赛模式
    WHEEL = auto()      # 轮盘模式
    LOTTERY = auto()     # 抽奖模式
    SEQUENCE = auto()    # 顺序模式
    RANDOM_GROUP = auto() # 随机分组
    ELIMINATION = auto() # 淘汰模式

# 考勤状态枚举
class AttendanceStatus(Enum):
    PRESENT = auto()     # 出勤
    ABSENT = auto()      # 缺勤
    LATE = auto()        # 迟到
    LEAVE = auto()       # 请假
    EARLY_LEAVE = auto() # 早退

# 学生状态枚举
class StudentState(Enum):
    NORMAL = auto()       # 正常
    SUSPENDED = auto()   # 停课
    GRADUATED = auto()   # 已毕业
    TRANSFERRED = auto() # 已转学

# 奖励类型枚举
class RewardType(Enum):
    STAR = auto()        # 星星
    BADGE = auto()       # 徽章
    SCORE = auto()       # 积分
    LEVEL = auto()       # 等级

# 惩罚类型枚举
class PunishmentType(Enum):
    WARNING = auto()     # 警告
    DEDUCT = auto()      # 扣分
    SUSPEND = auto()     # 暂停点名

# 语言包
LANGUAGE_PACKS = {
    "简体中文": {
        "app_title": "智慧课堂点名系统",
        "start": "开始",
        "stop": "停止",
        "reset": "重置",
        "settings": "设置",
        "class_manager": "班级管理",
        "student_manager": "学生管理",
        "statistics": "数据统计",
        "attendance": "考勤记录",
        "history": "历史记录",
        "export": "导出数据",
        "import": "导入数据",
        "about": "关于",
        "help": "帮助",
        "exit": "退出",
        "save": "保存",
        "cancel": "取消",
        "confirm": "确认",
        "delete": "删除",
        "edit": "编辑",
        "add": "添加",
        "search": "搜索",
        "filter": "筛选",
        "refresh": "刷新",
        "total": "总计",
        "present": "出勤",
        "absent": "缺勤",
        "late": "迟到",
        "leave": "请假",
        "name": "姓名",
        "number": "学号",
        "gender": "性别",
        "phone": "电话",
        "email": "邮箱",
        "address": "地址",
        "birthday": "生日",
        "parent": "家长",
        "note": "备注",
        "grade": "年级",
        "class_name": "班级",
        "seat": "座位",
        "draw_count": "抽取人数",
        "draw_mode": "抽取模式",
        "history_count": "历史记录数",
        "success_rate": "出勤率",
        "points": "积分",
        "level": "等级",
        "stars": "星星",
        "badges": "徽章",
        "rewards": "奖励",
        "punishments": "惩罚",
        "no_students": "暂无学生",
        "no_records": "暂无记录",
        "load_success": "加载成功",
        "save_success": "保存成功",
        "delete_success": "删除成功",
        "import_success": "导入成功",
        "export_success": "导出成功",
        "error": "错误",
        "warning": "警告",
        "info": "提示",
        "confirm_delete": "确认删除？",
        "confirm_reset": "确认重置？",
        "file_not_found": "文件不存在",
        "invalid_format": "无效格式",
        "network_error": "网络错误",
        "unknown_error": "未知错误",
    },
    "English": {
        "app_title": "Smart Classroom Attendance System",
        "start": "Start",
        "stop": "Stop",
        "reset": "Reset",
        "settings": "Settings",
        "class_manager": "Class Manager",
        "student_manager": "Student Manager",
        "statistics": "Statistics",
        "attendance": "Attendance",
        "history": "History",
        "export": "Export",
        "import": "Import",
        "about": "About",
        "help": "Help",
        "exit": "Exit",
        "save": "Save",
        "cancel": "Cancel",
        "confirm": "Confirm",
        "delete": "Delete",
        "edit": "Edit",
        "add": "Add",
        "search": "Search",
        "filter": "Filter",
        "refresh": "Refresh",
        "total": "Total",
        "present": "Present",
        "absent": "Absent",
        "late": "Late",
        "leave": "Leave",
        "name": "Name",
        "number": "Number",
        "gender": "Gender",
        "phone": "Phone",
        "email": "Email",
        "address": "Address",
        "birthday": "Birthday",
        "parent": "Parent",
        "note": "Note",
        "grade": "Grade",
        "class_name": "Class",
        "seat": "Seat",
        "draw_count": "Draw Count",
        "draw_mode": "Draw Mode",
        "history_count": "History Count",
        "success_rate": "Attendance Rate",
        "points": "Points",
        "level": "Level",
        "stars": "Stars",
        "badges": "Badges",
        "rewards": "Rewards",
        "punishments": "Punishments",
        "no_students": "No Students",
        "no_records": "No Records",
        "load_success": "Load Success",
        "save_success": "Save Success",
        "delete_success": "Delete Success",
        "import_success": "Import Success",
        "export_success": "Export Success",
        "error": "Error",
        "warning": "Warning",
        "info": "Info",
        "confirm_delete": "Confirm Delete?",
        "confirm_reset": "Confirm Reset?",
        "file_not_found": "File Not Found",
        "invalid_format": "Invalid Format",
        "network_error": "Network Error",
        "unknown_error": "Unknown Error",
    }
}

# ==========================================
# 路径和基础配置
# ==========================================
def get_base_path() -> str:
    """获取程序基准目录"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()
DATA_DIR = os.path.join(BASE_DIR, "data")
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")
BACKGROUNDS_DIR = os.path.join(BASE_DIR, "backgrounds")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

# 创建必要目录
for directory in [DATA_DIR, SOUNDS_DIR, BACKGROUNDS_DIR, EXPORT_DIR, BACKUP_DIR]:
    os.makedirs(directory, exist_ok=True)

MY_APP_ID = 'yuyuchi.smartpicker.pro.5.0.0'
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(MY_APP_ID)
except (AttributeError, OSError):
    pass

# ==========================================
# 数据类定义
# ==========================================
@dataclass
class Student:
    """学生数据类"""
    id: str = ""
    number: str = ""  # 学号
    name: str = ""
    gender: str = "男"
    phone: str = ""
    email: str = ""
    address: str = ""
    birthday: str = ""
    parent_name: str = ""
    parent_phone: str = ""
    note: str = ""
    photo_path: str = ""
    state: int = StudentState.NORMAL.value
    weight: float = 100.0
    points: int = 0
    stars: int = 0
    badges: List[str] = field(default_factory=list)
    attendance_count: int = 0
    absent_count: int = 0
    late_count: int = 0
    leave_count: int = 0
    draw_count: int = 0
    last_draw_time: str = ""
    rewards: List[Dict] = field(default_factory=list)
    punishments: List[Dict] = field(default_factory=list)
    custom_fields: Dict = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Student':
        return cls(**data)

@dataclass
class ClassInfo:
    """班级数据类"""
    id: str = ""
    name: str = ""
    grade: str = ""
    year: str = ""
    semester: str = ""
    teacher: str = ""
    room: str = ""
    capacity: int = 50
    color: str = "#1976d2"
    icon: str = "📚"
    note: str = ""
    subjects: List[str] = field(default_factory=list)
    schedule: Dict = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'ClassInfo':
        return cls(**data)

@dataclass
class AttendanceRecord:
    """考勤记录数据类"""
    id: str = ""
    student_id: str = ""
    student_name: str = ""
    class_id: str = ""
    date: str = ""
    status: int = AttendanceStatus.PRESENT.value
    check_in_time: str = ""
    check_out_time: str = ""
    note: str = ""
    photo_path: str = ""
    location: str = ""
    device: str = ""
    operator: str = ""
    created_at: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'AttendanceRecord':
        return cls(**data)

@dataclass
class DrawRecord:
    """抽取记录数据类"""
    id: str = ""
    class_id: str = ""
    mode: int = DrawMode.NORMAL.value
    winners: List[Dict] = field(default_factory=list)
    draw_count: int = 1
    date: str = ""
    time: str = ""
    duration: float = 0.0
    note: str = ""
    created_at: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'DrawRecord':
        return cls(**data)

@dataclass
class SeatInfo:
    """座位信息数据类"""
    student_id: str = ""
    row: int = 0
    col: int = 0
    class_id: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'SeatInfo':
        return cls(**data)

# ==========================================
# 数据库管理器
# ==========================================
class DatabaseManager:
    """SQLite数据库管理器"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(DATA_DIR, "smartpicker.db")
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"[错误] 数据库连接失败: {e}")

    def _create_tables(self):
        """创建数据表"""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                number TEXT UNIQUE,
                name TEXT NOT NULL,
                gender TEXT DEFAULT '男',
                phone TEXT,
                email TEXT,
                address TEXT,
                birthday TEXT,
                parent_name TEXT,
                parent_phone TEXT,
                note TEXT,
                photo_path TEXT,
                state INTEGER DEFAULT 1,
                weight REAL DEFAULT 100.0,
                points INTEGER DEFAULT 0,
                stars INTEGER DEFAULT 0,
                badges TEXT DEFAULT '[]',
                attendance_count INTEGER DEFAULT 0,
                absent_count INTEGER DEFAULT 0,
                late_count INTEGER DEFAULT 0,
                leave_count INTEGER DEFAULT 0,
                draw_count INTEGER DEFAULT 0,
                last_draw_time TEXT,
                rewards TEXT DEFAULT '[]',
                punishments TEXT DEFAULT '[]',
                custom_fields TEXT DEFAULT '{}',
                created_at TEXT,
                updated_at TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS classes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                grade TEXT,
                year TEXT,
                semester TEXT,
                teacher TEXT,
                room TEXT,
                capacity INTEGER DEFAULT 50,
                color TEXT DEFAULT '#1976d2',
                icon TEXT DEFAULT '📚',
                note TEXT,
                subjects TEXT DEFAULT '[]',
                schedule TEXT DEFAULT '{}',
                created_at TEXT,
                updated_at TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS class_students (
                class_id TEXT,
                student_id TEXT,
                seat_row INTEGER,
                seat_col INTEGER,
                enrolled_date TEXT,
                PRIMARY KEY (class_id, student_id),
                FOREIGN KEY (class_id) REFERENCES classes(id),
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS attendance_records (
                id TEXT PRIMARY KEY,
                student_id TEXT,
                student_name TEXT,
                class_id TEXT,
                date TEXT,
                status INTEGER,
                check_in_time TEXT,
                check_out_time TEXT,
                note TEXT,
                photo_path TEXT,
                location TEXT,
                device TEXT,
                operator TEXT,
                created_at TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (class_id) REFERENCES classes(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS draw_records (
                id TEXT PRIMARY KEY,
                class_id TEXT,
                mode INTEGER,
                winners TEXT,
                draw_count INTEGER,
                date TEXT,
                time TEXT,
                duration REAL,
                note TEXT,
                created_at TEXT,
                FOREIGN KEY (class_id) REFERENCES classes(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS rewards_history (
                id TEXT PRIMARY KEY,
                student_id TEXT,
                type INTEGER,
                name TEXT,
                description TEXT,
                points INTEGER,
                operator TEXT,
                created_at TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS punishments_history (
                id TEXT PRIMARY KEY,
                student_id TEXT,
                type INTEGER,
                name TEXT,
                description TEXT,
                points INTEGER,
                operator TEXT,
                created_at TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS badges (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                icon TEXT,
                requirement TEXT,
                rarity INTEGER DEFAULT 1,
                created_at TEXT
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_students_name ON students(name)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_students_number ON students(number)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance_records(date)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_draw_date ON draw_records(date)
            """
        ]

        for sql in tables:
            try:
                self.cursor.execute(sql)
            except Exception as e:
                print(f"[错误] 创建表失败: {e}")
        self.conn.commit()

    def execute(self, sql: str, params: Tuple = None) -> sqlite3.Cursor:
        """执行SQL语句"""
        try:
            if params:
                return self.cursor.execute(sql, params)
            return self.cursor.execute(sql)
        except Exception as e:
            print(f"[错误] SQL执行失败: {e}")
            return None

    def commit(self):
        """提交事务"""
        try:
            self.conn.commit()
        except Exception as e:
            print(f"[错误] 提交失败: {e}")
            self.conn.rollback()

    def fetchall(self, sql: str, params: Tuple = None) -> List:
        """获取所有结果"""
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"[错误] 查询失败: {e}")
            return []

    def fetchone(self, sql: str, params: Tuple = None):
        """获取单条结果"""
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"[错误] 查询失败: {e}")
            return None

    def insert(self, table: str, data: Dict) -> bool:
        """插入数据"""
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            sql = f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(sql, tuple(data.values()))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[错误] 插入失败: {e}")
            self.conn.rollback()
            return False

    def update(self, table: str, data: Dict, where: str, where_params: Tuple = None) -> bool:
        """更新数据"""
        try:
            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
            params = tuple(data.values()) + (where_params if where_params else ())
            self.cursor.execute(sql, params)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[错误] 更新失败: {e}")
            self.conn.rollback()
            return False

    def delete(self, table: str, where: str, where_params: Tuple = None) -> bool:
        """删除数据"""
        try:
            sql = f"DELETE FROM {table} WHERE {where}"
            params = where_params if where_params else ()
            self.cursor.execute(sql, params)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[错误] 删除失败: {e}")
            self.conn.rollback()
            return False

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

# ==========================================
# 学生管理器
# ==========================================
class StudentManager:
    """学生数据管理器"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_student(self, student: Student) -> bool:
        """添加学生"""
        data = student.to_dict()
        if not data.get('id'):
            data['id'] = self._generate_id()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['created_at'] = now
        data['updated_at'] = now
        data['badges'] = json.dumps(data.get('badges', []))
        data['rewards'] = json.dumps(data.get('rewards', []))
        data['punishments'] = json.dumps(data.get('punishments', []))
        data['custom_fields'] = json.dumps(data.get('custom_fields', {}))
        return self.db.insert('students', data)

    def update_student(self, student: Student) -> bool:
        """更新学生信息"""
        data = student.to_dict()
        data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['badges'] = json.dumps(data.get('badges', []))
        data['rewards'] = json.dumps(data.get('rewards', []))
        data['punishments'] = json.dumps(data.get('punishments', []))
        data['custom_fields'] = json.dumps(data.get('custom_fields', {}))
        return self.db.update('students', data, 'id = ?', (student.id,))

    def delete_student(self, student_id: str) -> bool:
        """删除学生"""
        return self.db.delete('students', 'id = ?', (student_id,))

    def get_student(self, student_id: str) -> Optional[Student]:
        """获取学生信息"""
        row = self.db.fetchone('SELECT * FROM students WHERE id = ?', (student_id,))
        if row:
            return self._row_to_student(row)
        return None

    def get_all_students(self) -> List[Student]:
        """获取所有学生"""
        rows = self.db.fetchall('SELECT * FROM students ORDER BY number, name')
        return [self._row_to_student(row) for row in rows]

    def search_students(self, keyword: str) -> List[Student]:
        """搜索学生"""
        keyword = f"%{keyword}%"
        rows = self.db.fetchall(
            'SELECT * FROM students WHERE name LIKE ? OR number LIKE ? OR phone LIKE ? ORDER BY name',
            (keyword, keyword, keyword)
        )
        return [self._row_to_student(row) for row in rows]

    def import_students(self, file_path: str) -> Tuple[int, int]:
        """批量导入学生"""
        success_count = 0
        fail_count = 0
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.csv':
            success_count, fail_count = self._import_from_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            success_count, fail_count = self._import_from_excel(file_path)
        elif ext == '.json':
            success_count, fail_count = self._import_from_json(file_path)
        elif ext == '.txt':
            success_count, fail_count = self._import_from_txt(file_path)

        return success_count, fail_count

    def _import_from_csv(self, file_path: str) -> Tuple[int, int]:
        """从CSV导入"""
        success_count = 0
        fail_count = 0
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        student = Student(
                            id=self._generate_id(),
                            number=row.get('学号', row.get('number', '')),
                            name=row.get('姓名', row.get('name', '')),
                            gender=row.get('性别', row.get('gender', '男')),
                            phone=row.get('电话', row.get('phone', '')),
                            email=row.get('邮箱', row.get('email', '')),
                            address=row.get('地址', row.get('address', '')),
                            birthday=row.get('生日', row.get('birthday', '')),
                            parent_name=row.get('家长', row.get('parent', '')),
                            parent_phone=row.get('家长电话', row.get('parent_phone', '')),
                            note=row.get('备注', row.get('note', ''))
                        )
                        if self.add_student(student):
                            success_count += 1
                        else:
                            fail_count += 1
                    except Exception:
                        fail_count += 1
        except Exception:
            fail_count = 1
        return success_count, fail_count

    def _import_from_excel(self, file_path: str) -> Tuple[int, int]:
        """从Excel导入"""
        success_count = 0
        fail_count = 0
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active
            headers = [cell.value for cell in ws[1]]

            for row in ws.iter_rows(min_row=2):
                try:
                    data = {headers[i]: row[i].value for i in range(len(headers))}
                    student = Student(
                        id=self._generate_id(),
                        number=data.get('学号', data.get('number', '')),
                        name=data.get('姓名', data.get('name', '')),
                        gender=data.get('性别', data.get('gender', '男')),
                        phone=data.get('电话', data.get('phone', '')),
                        email=data.get('邮箱', data.get('email', '')),
                        address=data.get('地址', data.get('address', '')),
                        birthday=str(data.get('生日', data.get('birthday', ''))),
                        parent_name=data.get('家长', data.get('parent', '')),
                        parent_phone=data.get('家长电话', data.get('parent_phone', '')),
                        note=data.get('备注', data.get('note', ''))
                    )
                    if self.add_student(student):
                        success_count += 1
                    else:
                        fail_count += 1
                except Exception:
                    fail_count += 1
        except Exception:
            fail_count = 1
        return success_count, fail_count

    def _import_from_json(self, file_path: str) -> Tuple[int, int]:
        """从JSON导入"""
        success_count = 0
        fail_count = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        try:
                            student = Student(**item)
                            student.id = self._generate_id()
                            if self.add_student(student):
                                success_count += 1
                            else:
                                fail_count += 1
                        except Exception:
                            fail_count += 1
        except Exception:
            fail_count = 1
        return success_count, fail_count

    def _import_from_txt(self, file_path: str) -> Tuple[int, int]:
        """从Txt导入（每行一个姓名）"""
        success_count = 0
        fail_count = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    name = line.strip()
                    if name:
                        student = Student(
                            id=self._generate_id(),
                            number=str(i),
                            name=name
                        )
                        if self.add_student(student):
                            success_count += 1
                        else:
                            fail_count += 1
        except Exception:
            fail_count = 1
        return success_count, fail_count

    def export_students(self, file_path: str, format: str = 'csv') -> bool:
        """导出学生数据"""
        students = self.get_all_students()
        if not students:
            return False

        ext = os.path.splitext(file_path)[1].lower()

        if format == 'csv' or ext == '.csv':
            return self._export_to_csv(file_path, students)
        elif format == 'json' or ext == '.json':
            return self._export_to_json(file_path, students)
        elif format == 'excel' or ext in ['.xlsx', '.xls']:
            return self._export_to_excel(file_path, students)
        elif format == 'txt' or ext == '.txt':
            return self._export_to_txt(file_path, students)
        return False

    def _export_to_csv(self, file_path: str, students: List[Student]) -> bool:
        """导出为CSV"""
        try:
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                fieldnames = ['学号', '姓名', '性别', '电话', '邮箱', '地址', '生日', '家长', '家长电话', '备注', '积分', '星星']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for s in students:
                    writer.writerow({
                        '学号': s.number,
                        '姓名': s.name,
                        '性别': s.gender,
                        '电话': s.phone,
                        '邮箱': s.email,
                        '地址': s.address,
                        '生日': s.birthday,
                        '家长': s.parent_name,
                        '家长电话': s.parent_phone,
                        '备注': s.note,
                        '积分': s.points,
                        '星星': s.stars
                    })
            return True
        except Exception:
            return False

    def _export_to_json(self, file_path: str, students: List[Student]) -> bool:
        """导出为JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([s.to_dict() for s in students], f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def _export_to_excel(self, file_path: str, students: List[Student]) -> bool:
        """导出为Excel"""
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "学生信息"

            headers = ['学号', '姓名', '性别', '电话', '邮箱', '地址', '生日', '家长', '家长电话', '备注', '积分', '星星', '出勤次数', '缺勤次数']
            ws.append(headers)

            for s in students:
                ws.append([
                    s.number, s.name, s.gender, s.phone, s.email,
                    s.address, s.birthday, s.parent_name, s.parent_phone,
                    s.note, s.points, s.stars, s.attendance_count, s.absent_count
                ])

            wb.save(file_path)
            return True
        except Exception:
            return False

    def _export_to_txt(self, file_path: str, students: List[Student]) -> bool:
        """导出为Txt"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for s in students:
                    f.write(f"{s.number}\t{s.name}\n")
            return True
        except Exception:
            return False

    def _row_to_student(self, row) -> Student:
        """将数据库行转换为Student对象"""
        try:
            badges = json.loads(row['badges']) if row['badges'] else []
            rewards = json.loads(row['rewards']) if row['rewards'] else []
            punishments = json.loads(row['punishments']) if row['punishments'] else []
            custom_fields = json.loads(row['custom_fields']) if row['custom_fields'] else {}
        except (json.JSONDecodeError, TypeError):
            badges, rewards, punishments, custom_fields = [], [], [], {}

        return Student(
            id=row['id'], number=row['number'], name=row['name'],
            gender=row['gender'], phone=row['phone'], email=row['email'],
            address=row['address'], birthday=row['birthday'],
            parent_name=row['parent_name'], parent_phone=row['parent_phone'],
            note=row['note'], photo_path=row['photo_path'],
            state=row['state'], weight=row['weight'], points=row['points'],
            stars=row['stars'], badges=badges, attendance_count=row['attendance_count'],
            absent_count=row['absent_count'], late_count=row['late_count'],
            leave_count=row['leave_count'], draw_count=row['draw_count'],
            last_draw_time=row['last_draw_time'], rewards=rewards,
            punishments=punishments, custom_fields=custom_fields,
            created_at=row['created_at'], updated_at=row['updated_at']
        )

    def _generate_id(self) -> str:
        """生成唯一ID"""
        return hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:16]

# ==========================================
# 班级管理器
# ==========================================
class ClassManager:
    """班级数据管理器"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_class(self, class_info: ClassInfo) -> bool:
        """添加班级"""
        data = class_info.to_dict()
        if not data.get('id'):
            data['id'] = self._generate_id()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['created_at'] = now
        data['updated_at'] = now
        data['subjects'] = json.dumps(data.get('subjects', []))
        data['schedule'] = json.dumps(data.get('schedule', {}))
        return self.db.insert('classes', data)

    def update_class(self, class_info: ClassInfo) -> bool:
        """更新班级信息"""
        data = class_info.to_dict()
        data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['subjects'] = json.dumps(data.get('subjects', []))
        data['schedule'] = json.dumps(data.get('schedule', {}))
        return self.db.update('classes', data, 'id = ?', (class_info.id,))

    def delete_class(self, class_id: str) -> bool:
        """删除班级"""
        self.db.delete('class_students', 'class_id = ?', (class_id,))
        return self.db.delete('classes', 'id = ?', (class_id,))

    def get_class(self, class_id: str) -> Optional[ClassInfo]:
        """获取班级信息"""
        row = self.db.fetchone('SELECT * FROM classes WHERE id = ?', (class_id,))
        if row:
            return self._row_to_class(row)
        return None

    def get_all_classes(self) -> List[ClassInfo]:
        """获取所有班级"""
        rows = self.db.fetchall('SELECT * FROM classes ORDER BY grade, name')
        return [self._row_to_class(row) for row in rows]

    def get_class_students(self, class_id: str) -> List[str]:
        """获取班级学生ID列表"""
        rows = self.db.fetchall(
            'SELECT student_id FROM class_students WHERE class_id = ? ORDER BY seat_row, seat_col',
            (class_id,)
        )
        return [row['student_id'] for row in rows]

    def add_student_to_class(self, class_id: str, student_id: str, seat_row: int = 0, seat_col: int = 0) -> bool:
        """添加学生到班级"""
        data = {
            'class_id': class_id,
            'student_id': student_id,
            'seat_row': seat_row,
            'seat_col': seat_col,
            'enrolled_date': datetime.now().strftime("%Y-%m-%d")
        }
        try:
            sql = """INSERT OR IGNORE INTO class_students 
                    (class_id, student_id, seat_row, seat_col, enrolled_date) 
                    VALUES (?, ?, ?, ?, ?)"""
            self.db.execute(sql, (class_id, student_id, seat_row, seat_col, data['enrolled_date']))
            self.db.commit()
            return True
        except Exception:
            return False

    def remove_student_from_class(self, class_id: str, student_id: str) -> bool:
        """从班级移除学生"""
        return self.db.delete('class_students', 'class_id = ? AND student_id = ?', (class_id, student_id))

    def _row_to_class(self, row) -> ClassInfo:
        """将数据库行转换为ClassInfo对象"""
        try:
            subjects = json.loads(row['subjects']) if row['subjects'] else []
            schedule = json.loads(row['schedule']) if row['schedule'] else {}
        except (json.JSONDecodeError, TypeError):
            subjects, schedule = [], {}

        return ClassInfo(
            id=row['id'], name=row['name'], grade=row['grade'],
            year=row['year'], semester=row['semester'],
            teacher=row['teacher'], room=row['room'],
            capacity=row['capacity'], color=row['color'],
            icon=row['icon'], note=row['note'], subjects=subjects,
            schedule=schedule, created_at=row['created_at'], updated_at=row['updated_at']
        )

    def _generate_id(self) -> str:
        """生成唯一ID"""
        return hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:16]

# ==========================================
# 考勤管理器
# ==========================================
class AttendanceManager:
    """考勤数据管理器"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_attendance(self, record: AttendanceRecord) -> bool:
        """添加考勤记录"""
        data = record.to_dict()
        if not data.get('id'):
            data['id'] = self._generate_id()
        data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.db.insert('attendance_records', data)

    def get_attendance(self, student_id: str, date: str) -> Optional[AttendanceRecord]:
        """获取特定学生某天的考勤记录"""
        row = self.db.fetchone(
            'SELECT * FROM attendance_records WHERE student_id = ? AND date = ?',
            (student_id, date)
        )
        if row:
            return self._row_to_record(row)
        return None

    def get_student_attendance_history(self, student_id: str, start_date: str = None, end_date: str = None) -> List[AttendanceRecord]:
        """获取学生考勤历史"""
        if start_date and end_date:
            rows = self.db.fetchall(
                'SELECT * FROM attendance_records WHERE student_id = ? AND date BETWEEN ? AND ? ORDER BY date DESC',
                (student_id, start_date, end_date)
            )
        else:
            rows = self.db.fetchall(
                'SELECT * FROM attendance_records WHERE student_id = ? ORDER BY date DESC',
                (student_id,)
            )
        return [self._row_to_record(row) for row in rows]

    def get_class_attendance(self, class_id: str, date: str) -> List[AttendanceRecord]:
        """获取班级某天考勤记录"""
        rows = self.db.fetchall(
            'SELECT * FROM attendance_records WHERE class_id = ? AND date = ? ORDER BY student_name',
            (class_id, date)
        )
        return [self._row_to_record(row) for row in rows]

    def get_attendance_statistics(self, class_id: str = None, start_date: str = None, end_date: str = None) -> Dict:
        """获取考勤统计"""
        stats = {
            'total': 0, 'present': 0, 'absent': 0, 'late': 0, 'leave': 0,
            'present_rate': 0.0, 'absent_rate': 0.0, 'late_rate': 0.0, 'leave_rate': 0.0
        }

        if class_id:
            if start_date and end_date:
                rows = self.db.fetchall(
                    'SELECT status, COUNT(*) as count FROM attendance_records WHERE class_id = ? AND date BETWEEN ? AND ? GROUP BY status',
                    (class_id, start_date, end_date)
                )
            else:
                rows = self.db.fetchall(
                    'SELECT status, COUNT(*) as count FROM attendance_records WHERE class_id = ? GROUP BY status',
                    (class_id,)
                )
        else:
            if start_date and end_date:
                rows = self.db.fetchall(
                    'SELECT status, COUNT(*) as count FROM attendance_records WHERE date BETWEEN ? AND ? GROUP BY status',
                    (start_date, end_date)
                )
            else:
                rows = self.db.fetchall(
                    'SELECT status, COUNT(*) as count FROM attendance_records GROUP BY status'
                )

        for row in rows:
            status = row['status']
            count = row['count']
            stats['total'] += count

            if status == AttendanceStatus.PRESENT.value:
                stats['present'] = count
            elif status == AttendanceStatus.ABSENT.value:
                stats['absent'] = count
            elif status == AttendanceStatus.LATE.value:
                stats['late'] = count
            elif status == AttendanceStatus.LEAVE.value:
                stats['leave'] = count

        if stats['total'] > 0:
            stats['present_rate'] = round(stats['present'] / stats['total'] * 100, 2)
            stats['absent_rate'] = round(stats['absent'] / stats['total'] * 100, 2)
            stats['late_rate'] = round(stats['late'] / stats['total'] * 100, 2)
            stats['leave_rate'] = round(stats['leave'] / stats['total'] * 100, 2)

        return stats

    def batch_add_attendance(self, records: List[AttendanceRecord]) -> Tuple[int, int]:
        """批量添加考勤记录"""
        success_count = 0
        fail_count = 0
        for record in records:
            if self.add_attendance(record):
                success_count += 1
            else:
                fail_count += 1
        return success_count, fail_count

    def export_attendance_report(self, class_id: str, start_date: str, end_date: str, file_path: str) -> bool:
        """导出考勤报表"""
        records = self.get_class_attendance(class_id, start_date)
        stats = self.get_attendance_statistics(class_id, start_date, end_date)

        try:
            if file_path.endswith('.xlsx'):
                import openpyxl
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "考勤报表"

                ws.append([f"考勤报表 - {start_date} 至 {end_date}"])
                ws.append([])
                ws.append(["统计信息"])
                ws.append(["总人数", stats['total']])
                ws.append(["出勤人数", stats['present'], f"{stats['present_rate']}%"])
                ws.append(["缺勤人数", stats['absent'], f"{stats['absent_rate']}%"])
                ws.append(["迟到人数", stats['late'], f"{stats['late_rate']}%"])
                ws.append(["请假人数", stats['leave'], f"{stats['leave_rate']}%"])
                ws.append([])

                headers = ['学号', '姓名', '日期', '状态', '签到时间', '备注']
                ws.append(headers)

                status_names = {
                    AttendanceStatus.PRESENT.value: '出勤',
                    AttendanceStatus.ABSENT.value: '缺勤',
                    AttendanceStatus.LATE.value: '迟到',
                    AttendanceStatus.LEAVE.value: '请假'
                }

                for record in records:
                    ws.append([
                        record.student_id, record.student_name, record.date,
                        status_names.get(record.status, '未知'),
                        record.check_in_time, record.note
                    ])

                wb.save(file_path)
                return True

            elif file_path.endswith('.csv'):
                return self._export_to_csv(file_path, records, stats, start_date, end_date)

        except Exception:
            return False

        return False

    def _export_to_csv(self, file_path: str, records: List[AttendanceRecord], stats: Dict, start_date: str, end_date: str) -> bool:
        """导出为CSV"""
        try:
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([f"考勤报表 - {start_date} 至 {end_date}"])
                writer.writerow([])
                writer.writerow(["统计信息"])
                writer.writerow(["总人数", stats['total']])
                writer.writerow(["出勤人数", stats['present'], f"{stats['present_rate']}%"])
                writer.writerow(["缺勤人数", stats['absent'], f"{stats['absent_rate']}%"])
                writer.writerow(["迟到人数", stats['late'], f"{stats['late_rate']}%"])
                writer.writerow(["请假人数", stats['leave'], f"{stats['leave_rate']}%"])
                writer.writerow([])

                headers = ['学号', '姓名', '日期', '状态', '签到时间', '备注']
                writer.writerow(headers)

                status_names = {
                    AttendanceStatus.PRESENT.value: '出勤',
                    AttendanceStatus.ABSENT.value: '缺勤',
                    AttendanceStatus.LATE.value: '迟到',
                    AttendanceStatus.LEAVE.value: '请假'
                }

                for record in records:
                    writer.writerow([
                        record.student_id, record.student_name, record.date,
                        status_names.get(record.status, '未知'),
                        record.check_in_time, record.note
                    ])
            return True
        except Exception:
            return False

    def _row_to_record(self, row) -> AttendanceRecord:
        """将数据库行转换为AttendanceRecord对象"""
        return AttendanceRecord(
            id=row['id'], student_id=row['student_id'], student_name=row['student_name'],
            class_id=row['class_id'], date=row['date'], status=row['status'],
            check_in_time=row['check_in_time'], check_out_time=row['check_out_time'],
            note=row['note'], photo_path=row['photo_path'], location=row['location'],
            device=row['device'], operator=row['operator'], created_at=row['created_at']
        )

    def _generate_id(self) -> str:
        """生成唯一ID"""
        return hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:16]

# ==========================================
# 抽取记录管理器
# ==========================================
class DrawRecordManager:
    """抽取记录管理器"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_record(self, record: DrawRecord) -> bool:
        """添加抽取记录"""
        data = record.to_dict()
        if not data.get('id'):
            data['id'] = self._generate_id()
        data['winners'] = json.dumps(data.get('winners', []))
        data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.db.insert('draw_records', data)

    def get_history(self, class_id: str = None, start_date: str = None, end_date: str = None, limit: int = 100) -> List[DrawRecord]:
        """获取抽取历史"""
        conditions = []
        params = []

        if class_id:
            conditions.append("class_id = ?")
            params.append(class_id)
        if start_date:
            conditions.append("date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("date <= ?")
            params.append(end_date)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f'SELECT * FROM draw_records WHERE {where_clause} ORDER BY created_at DESC LIMIT ?'
        params.append(limit)

        rows = self.db.fetchall(sql, tuple(params))
        return [self._row_to_record(row) for row in rows]

    def get_student_draw_history(self, student_id: str) -> List[DrawRecord]:
        """获取学生被抽取历史"""
        rows = self.db.fetchall(
            'SELECT * FROM draw_records ORDER BY created_at DESC',
        )
        records = []
        for row in rows:
            record = self._row_to_record(row)
            winners = record.winners
            for w in winners:
                if isinstance(w, dict) and w.get('id') == student_id:
                    records.append(record)
                    break
                elif isinstance(w, str) and w == student_id:
                    records.append(record)
                    break
        return records

    def get_statistics(self, class_id: str = None) -> Dict:
        """获取抽取统计"""
        if class_id:
            rows = self.db.fetchall(
                'SELECT COUNT(*) as total, SUM(draw_count) as total_draws FROM draw_records WHERE class_id = ?',
                (class_id,)
            )
        else:
            rows = self.db.fetchall('SELECT COUNT(*) as total, SUM(draw_count) as total_draws FROM draw_records')

        if rows and rows[0]:
            return {
                'total_records': rows[0]['total'] or 0,
                'total_draws': rows[0]['total_draws'] or 0
            }
        return {'total_records': 0, 'total_draws': 0}

    def _row_to_record(self, row) -> DrawRecord:
        """将数据库行转换为DrawRecord对象"""
        try:
            winners = json.loads(row['winners']) if row['winners'] else []
        except (json.JSONDecodeError, TypeError):
            winners = []

        return DrawRecord(
            id=row['id'], class_id=row['class_id'], mode=row['mode'],
            winners=winners, draw_count=row['draw_count'],
            date=row['date'], time=row['time'], duration=row['duration'],
            note=row['note'], created_at=row['created_at']
        )

    def _generate_id(self) -> str:
        """生成唯一ID"""
        return hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:16]

# ==========================================
# 积分奖励管理器
# ==========================================
class RewardManager:
    """积分奖励管理器"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_reward(self, student_id: str, reward_type: RewardType, name: str, 
                   description: str = "", points: int = 0, operator: str = "系统") -> bool:
        """添加奖励"""
        data = {
            'id': self._generate_id(),
            'student_id': student_id,
            'type': reward_type.value,
            'name': name,
            'description': description,
            'points': points,
            'operator': operator,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return self.db.insert('rewards_history', data)

    def add_punishment(self, student_id: str, punishment_type: PunishmentType, name: str,
                       description: str = "", points: int = 0, operator: str = "系统") -> bool:
        """添加惩罚"""
        data = {
            'id': self._generate_id(),
            'student_id': student_id,
            'type': punishment_type.value,
            'name': name,
            'description': description,
            'points': points,
            'operator': operator,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return self.db.insert('punishments_history', data)

    def get_rewards(self, student_id: str, limit: int = 50) -> List[Dict]:
        """获取学生奖励记录"""
        rows = self.db.fetchall(
            'SELECT * FROM rewards_history WHERE student_id = ? ORDER BY created_at DESC LIMIT ?',
            (student_id, limit)
        )
        return [dict(row) for row in rows]

    def get_punishments(self, student_id: str, limit: int = 50) -> List[Dict]:
        """获取学生惩罚记录"""
        rows = self.db.fetchall(
            'SELECT * FROM punishments_history WHERE student_id = ? ORDER BY created_at DESC LIMIT ?',
            (student_id, limit)
        )
        return [dict(row) for row in rows]

    def get_leaderboard(self, class_id: str = None, limit: int = 20) -> List[Dict]:
        """获取积分排行榜"""
        if class_id:
            rows = self.db.fetchall('''
                SELECT s.id, s.name, s.points, s.stars, s.badges, s.draw_count,
                       (SELECT COUNT(*) FROM rewards_history r WHERE r.student_id = s.id) as reward_count
                FROM students s
                INNER JOIN class_students cs ON s.id = cs.student_id
                WHERE cs.class_id = ?
                ORDER BY s.points DESC, s.stars DESC
                LIMIT ?
            ''', (class_id, limit))
        else:
            rows = self.db.fetchall('''
                SELECT id, name, points, stars, badges, draw_count,
                       (SELECT COUNT(*) FROM rewards_history WHERE student_id = id) as reward_count
                FROM students
                ORDER BY points DESC, stars DESC
                LIMIT ?
            ''', (limit,))

        return [dict(row) for row in rows]

    def award_points(self, student_id: str, points: int, reason: str = "") -> bool:
        """奖励积分"""
        row = self.db.fetchone('SELECT points FROM students WHERE id = ?', (student_id,))
        if row:
            new_points = row['points'] + points
            self.db.update('students', {'points': new_points}, 'id = ?', (student_id,))
            return True
        return False

    def deduct_points(self, student_id: str, points: int, reason: str = "") -> bool:
        """扣除积分"""
        row = self.db.fetchone('SELECT points FROM students WHERE id = ?', (student_id,))
        if row:
            new_points = max(0, row['points'] - points)
            self.db.update('students', {'points': new_points}, 'id = ?', (student_id,))
            return True
        return False

    def award_star(self, student_id: str) -> bool:
        """奖励星星"""
        row = self.db.fetchone('SELECT stars FROM students WHERE id = ?', (student_id,))
        if row:
            new_stars = row['stars'] + 1
            self.db.update('students', {'stars': new_stars}, 'id = ?', (student_id,))

            # 检查是否达到升级条件
            if new_stars >= 10 and new_stars % 10 == 0:
                self._check_badge_awards(student_id, new_stars)

            return True
        return False

    def _check_badge_awards(self, student_id: str, stars: int):
        """检查并颁发徽章"""
        badges_to_award = []

        if stars >= 10:
            badges_to_award.append({'id': 'star_10', 'name': '🌟 新星', 'stars': 10})
        if stars >= 50:
            badges_to_award.append({'id': 'star_50', 'name': '⭐ 明星', 'stars': 50})
        if stars >= 100:
            badges_to_award.append({'id': 'star_100', 'name': '🌠 巨星', 'stars': 100})
        if stars >= 500:
            badges_to_award.append({'id': 'star_500', 'name': '💫 传奇', 'stars': 500})

        for badge in badges_to_award:
            self.add_reward(student_id, RewardType.BADGE, badge['name'], f"获得{badge['stars']}颗星星", 0)

    def _generate_id(self) -> str:
        """生成唯一ID"""
        return hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:16]

# ==========================================
# 配置管理器
# ==========================================
class ConfigManager:
    """配置管理器"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.config_path = os.path.join(DATA_DIR, "config.json")
        self.config = self._load_config()
        self._initialized = True

    def _load_config(self) -> Dict:
        """加载配置"""
        default_config = {
            'version': VERSION,
            'language': '简体中文',
            'theme': '默认蓝色',
            'animation_speed': 'medium',
            'animation_enabled': True,
            'sound_enabled': True,
            'voice_enabled': True,
            'voice_rate': 0,
            'voice_volume': 100,
            'default_draw_count': 1,
            'max_draw_count': 20,
            'auto_backup': True,
            'backup_interval': 24,
            'cloud_sync': False,
            'auto_check_update': True,
            'shortcut_keys': {
                'start_stop': 'space',
                'reset': 'r',
                'settings': 's',
                'history': 'h'
            },
            'recent_classes': [],
            'window_geometry': '800x650',
            'last_update_check': ''
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                default_config.update(loaded_config)
            except Exception:
                pass

        return default_config

    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[错误] 保存配置失败: {e}")

    def get(self, key: str, default=None):
        """获取配置值"""
        return self.config.get(key, default)

    def set(self, key: str, value):
        """设置配置值"""
        self.config[key] = value
        self.save_config()

    def get_theme(self) -> Dict:
        """获取当前主题"""
        theme_name = self.config.get('theme', '默认蓝色')
        return THEMES.get(theme_name, THEMES['默认蓝色'])

    def set_theme(self, theme_name: str):
        """设置主题"""
        if theme_name in THEMES:
            self.config['theme'] = theme_name
            self.save_config()

    def get_language(self) -> str:
        """获取当前语言"""
        return self.config.get('language', '简体中文')

    def set_language(self, language: str):
        """设置语言"""
        if language in SUPPORTED_LANGUAGES:
            self.config['language'] = language
            self.save_config()

    def get_text(self, key: str) -> str:
        """获取翻译文本"""
        lang = self.get_language()
        return LANGUAGE_PACKS.get(lang, LANGUAGE_PACKS['简体中文']).get(key, key)

# ==========================================
# 音效管理器
# ==========================================
class SoundManager:
    """音效管理器"""

    def __init__(self):
        self.config = ConfigManager()
        self.enabled = PYGAME_AVAILABLE and self.config.get('sound_enabled', True)
        self.voice_enabled = WIN32COM_AVAILABLE and self.config.get('voice_enabled', True)
        self.sounds = {}
        self.speaker = None
        self._init_mixer()
        self._init_voice()
        self._load_sounds()

    def _init_mixer(self):
        """初始化混音器"""
        if self.enabled:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except Exception as e:
                print(f"[提示] 音频初始化失败: {e}")
                self.enabled = False

    def _init_voice(self):
        """初始化语音"""
        if self.voice_enabled:
            try:
                self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
                rate = self.config.get('voice_rate', 0)
                volume = self.config.get('voice_volume', 100)
                if -10 <= rate <= 10:
                    self.speaker.Rate = rate
                if 0 <= volume <= 100:
                    self.speaker.Volume = volume
            except Exception:
                self.voice_enabled = False

    def _load_sounds(self):
        """加载音效文件"""
        if not self.enabled or not os.path.exists(SOUNDS_DIR):
            return

        valid_ext = {'.mp3', '.wav', '.ogg'}
        for filename in os.listdir(SOUNDS_DIR):
            if os.path.isfile(os.path.join(SOUNDS_DIR, filename)):
                ext = os.path.splitext(filename)[1].lower()
                if ext in valid_ext:
                    name = os.path.splitext(filename)[0]
                    self.sounds[name] = os.path.join(SOUNDS_DIR, filename)

    def play_sound(self, name: str, volume: float = 1.0, loop: bool = False):
        """播放音效"""
        if not self.enabled or name not in self.sounds:
            return

        try:
            pygame.mixer.music.load(self.sounds[name])
            pygame.mixer.music.set_volume(volume)
            loops = -1 if loop else 0
            pygame.mixer.music.play(loops)
        except Exception as e:
            print(f"[提示] 音效播放失败: {e}")

    def stop_sound(self):
        """停止音效"""
        if self.enabled:
            try:
                pygame.mixer.music.stop()
            except:
                pass

    def speak(self, text: str, async_mode: bool = True):
        """语音播报"""
        if not self.voice_enabled or not self.speaker or not text:
            return

        try:
            flags = 1 if async_mode else 0
            self.speaker.Speak(text, flags)
        except Exception as e:
            print(f"[提示] 语音播放失败: {e}")

    def speak_winners(self, winners: List[str]):
        """播报中奖者"""
        if not winners:
            return

        if len(winners) == 1:
            text = f"恭喜 {winners[0]}"
        else:
            names = "、".join(winners)
            text = f"恭喜以下同学：{names}"

        self.speak(text)

# ==========================================
# 备份管理器
# ==========================================
class BackupManager:
    """备份管理器"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.backup_dir = BACKUP_DIR

    def create_backup(self, name: str = None) -> str:
        """创建备份"""
        if name is None:
            name = datetime.now().strftime("%Y%m%d_%H%M%S")

        backup_path = os.path.join(self.backup_dir, f"backup_{name}.zip")

        try:
            import zipfile
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 备份数据库
                if os.path.exists(self.db.db_path):
                    zipf.write(self.db.db_path, "smartpicker.db")

                # 备份配置文件
                config_path = os.path.join(DATA_DIR, "config.json")
                if os.path.exists(config_path):
                    zipf.write(config_path, "config.json")

                # 备份weights
                weights_path = os.path.join(DATA_DIR, "weights.json")
                if os.path.exists(weights_path):
                    zipf.write(weights_path, "weights.json")

            return backup_path
        except Exception as e:
            print(f"[错误] 备份创建失败: {e}")
            return None

    def restore_backup(self, backup_path: str) -> bool:
        """恢复备份"""
        if not os.path.exists(backup_path):
            return False

        try:
            import zipfile
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(DATA_DIR)
            return True
        except Exception as e:
            print(f"[错误] 备份恢复失败: {e}")
            return False

    def list_backups(self) -> List[Dict]:
        """列出所有备份"""
        backups = []
        if os.path.exists(self.backup_dir):
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.zip'):
                    filepath = os.path.join(self.backup_dir, filename)
                    stat = os.stat(filepath)
                    backups.append({
                        'name': filename,
                        'path': filepath,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                    })
        return sorted(backups, key=lambda x: x['created'], reverse=True)

    def delete_backup(self, backup_path: str) -> bool:
        """删除备份"""
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
            return True
        except Exception:
            return False

# ==========================================
# 导入管理器
# ==========================================
class ImportExportManager:
    """导入导出管理器"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.student_manager = StudentManager(db)
        self.class_manager = ClassManager(db)
        self.attendance_manager = AttendanceManager(db)

    def import_data(self, file_path: str, data_type: str = 'students') -> Tuple[int, int]:
        """导入数据"""
        if data_type == 'students':
            return self.student_manager.import_students(file_path)
        elif data_type == 'attendance':
            return self._import_attendance(file_path)
        elif data_type == 'classes':
            return self._import_classes(file_path)

        return 0, 1

    def export_data(self, file_path: str, data_type: str = 'students', **kwargs) -> bool:
        """导出数据"""
        if data_type == 'students':
            return self.student_manager.export_students(file_path)
        elif data_type == 'attendance':
            class_id = kwargs.get('class_id')
            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')
            return self.attendance_manager.export_attendance_report(class_id, start_date, end_date, file_path)
        elif data_type == 'classes':
            return self._export_classes(file_path)

        return False

    def _import_attendance(self, file_path: str) -> Tuple[int, int]:
        """导入考勤数据"""
        success_count = 0
        fail_count = 0

        try:
            if file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            record = AttendanceRecord(
                                id='',
                                student_id=row.get('学号', row.get('student_id', '')),
                                student_name=row.get('姓名', row.get('name', '')),
                                class_id=row.get('班级', row.get('class_id', '')),
                                date=row.get('日期', row.get('date', '')),
                                status=int(row.get('状态', row.get('status', 1))),
                                check_in_time=row.get('签到时间', row.get('check_in_time', '')),
                                note=row.get('备注', row.get('note', ''))
                            )
                            if self.attendance_manager.add_attendance(record):
                                success_count += 1
                            else:
                                fail_count += 1
                        except Exception:
                            fail_count += 1
            elif file_path.endswith('.xlsx'):
                import openpyxl
                wb = openpyxl.load_workbook(file_path)
                ws = wb.active
                headers = [cell.value for cell in ws[1]]

                for row in ws.iter_rows(min_row=2):
                    try:
                        data = {headers[i]: row[i].value for i in range(len(headers))}
                        record = AttendanceRecord(
                            id='',
                            student_id=data.get('学号', ''),
                            student_name=data.get('姓名', ''),
                            class_id=data.get('班级', ''),
                            date=str(data.get('日期', '')),
                            status=int(data.get('状态', 1)),
                            check_in_time=data.get('签到时间', ''),
                            note=data.get('备注', '')
                        )
                        if self.attendance_manager.add_attendance(record):
                            success_count += 1
                        else:
                            fail_count += 1
                    except Exception:
                        fail_count += 1
        except Exception:
            fail_count = 1

        return success_count, fail_count

    def _import_classes(self, file_path: str) -> Tuple[int, int]:
        """导入班级数据"""
        success_count = 0
        fail_count = 0

        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            try:
                                class_info = ClassInfo(**item)
                                class_info.id = ''
                                if self.class_manager.add_class(class_info):
                                    success_count += 1
                                else:
                                    fail_count += 1
                            except Exception:
                                fail_count += 1
        except Exception:
            fail_count = 1

        return success_count, fail_count

    def _export_classes(self, file_path: str) -> bool:
        """导出班级数据"""
        classes = self.class_manager.get_all_classes()
        if not classes:
            return False

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([c.to_dict() for c in classes], f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

# ==========================================
# 统计分析器
# ==========================================
class StatisticsAnalyzer:
    """统计分析器"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.attendance_manager = AttendanceManager(db)
        self.draw_record_manager = DrawRecordManager(db)

    def get_attendance_trend(self, class_id: str, days: int = 30) -> Dict:
        """获取考勤趋势"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        rows = self.db.fetchall('''
            SELECT date, 
                   SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) as present,
                   SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) as absent,
                   SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) as late,
                   SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) as leave,
                   COUNT(*) as total
            FROM attendance_records
            WHERE class_id = ? AND date BETWEEN ? AND ?
            GROUP BY date
            ORDER BY date
        ''', (
            AttendanceStatus.PRESENT.value,
            AttendanceStatus.ABSENT.value,
            AttendanceStatus.LATE.value,
            AttendanceStatus.LEAVE.value,
            class_id, start_date, end_date
        ))

        trend = []
        for row in rows:
            present_rate = (row['present'] / row['total'] * 100) if row['total'] > 0 else 0
            trend.append({
                'date': row['date'],
                'present': row['present'],
                'absent': row['absent'],
                'late': row['late'],
                'leave': row['leave'],
                'total': row['total'],
                'present_rate': round(present_rate, 2)
            })

        return {'trend': trend, 'days': days}

    def get_draw_statistics(self, class_id: str = None) -> Dict:
        """获取抽取统计"""
        stats = self.draw_record_manager.get_statistics(class_id)

        mode_stats = {}
        rows = self.db.fetchall('''
            SELECT mode, COUNT(*) as count, SUM(draw_count) as total
            FROM draw_records
            GROUP BY mode
        ''')
        for row in rows:
            mode_stats[row['mode']] = {
                'count': row['count'],
                'total_draws': row['total']
            }

        stats['mode_distribution'] = mode_stats
        return stats

    def get_student_analysis(self, student_id: str) -> Dict:
        """获取学生分析"""
        student = self.db.fetchone('SELECT * FROM students WHERE id = ?', (student_id,))
        if not student:
            return {}

        attendance_history = self.attendance_manager.get_student_attendance_history(student_id)
        draw_history = self.draw_record_manager.get_student_draw_history(student_id)
        rewards = self.db.fetchall('SELECT * FROM rewards_history WHERE student_id = ?', (student_id,))
        punishments = self.db.fetchall('SELECT * FROM punishments_history WHERE student_id = ?', (student_id,))

        total_attendance = len(attendance_history)
        present_count = sum(1 for r in attendance_history if r.status == AttendanceStatus.PRESENT.value)
        absent_count = sum(1 for r in attendance_history if r.status == AttendanceStatus.ABSENT.value)
        late_count = sum(1 for r in attendance_history if r.status == AttendanceStatus.LATE.value)

        return {
            'student': dict(student),
            'attendance': {
                'total': total_attendance,
                'present': present_count,
                'absent': absent_count,
                'late': late_count,
                'present_rate': round(present_count / total_attendance * 100, 2) if total_attendance > 0 else 0
            },
            'draw': {
                'total': student['draw_count'],
                'history_count': len(draw_history)
            },
            'points': student['points'],
            'stars': student['stars'],
            'badges': json.loads(student['badges']) if student['badges'] else [],
            'rewards_count': len(rewards),
            'punishments_count': len(punishments)
        }

    def generate_report(self, class_id: str, start_date: str, end_date: str) -> Dict:
        """生成综合报表"""
        class_info = self.db.fetchone('SELECT * FROM classes WHERE id = ?', (class_id,))
        attendance_stats = self.attendance_manager.get_attendance_statistics(class_id, start_date, end_date)
        attendance_trend = self.get_attendance_trend(class_id, 30)
        draw_stats = self.get_draw_statistics(class_id)

        # 获取学生出勤排名
        student_attendance = []
        rows = self.db.fetchall('''
            SELECT s.id, s.name, s.number, 
                   COUNT(a.id) as total,
                   SUM(CASE WHEN a.status = 1 THEN 1 ELSE 0 END) as present
            FROM students s
            INNER JOIN class_students cs ON s.id = cs.student_id
            LEFT JOIN attendance_records a ON s.id = a.student_id AND a.date BETWEEN ? AND ?
            WHERE cs.class_id = ?
            GROUP BY s.id
            ORDER BY present DESC
        ''', (start_date, end_date, class_id))

        for row in rows:
            rate = (row['present'] / row['total'] * 100) if row['total'] > 0 else 0
            student_attendance.append({
                'id': row['id'],
                'name': row['name'],
                'number': row['number'],
                'present': row['present'],
                'total': row['total'],
                'rate': round(rate, 2)
            })

        return {
            'class': dict(class_info) if class_info else {},
            'period': {'start': start_date, 'end': end_date},
            'attendance': attendance_stats,
            'trend': attendance_trend,
            'draw': draw_stats,
            'students': student_attendance,
            'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def create_chart(self, data: Dict, chart_type: str = 'line', title: str = '') -> Optional[str]:
        """生成图表"""
        if not MATPLOTLIB_AVAILABLE:
            return None

        try:
            fig, ax = plt.subplots(figsize=(12, 6))

            if chart_type == 'line' and 'dates' in data:
                for label, values in data.items():
                    if label != 'dates':
                        ax.plot(data['dates'], values, marker='o', label=label, linewidth=2)
                ax.set_xlabel('日期')
                ax.set_ylabel('人数')
                ax.legend()
                ax.grid(True, alpha=0.3)

            elif chart_type == 'pie' and 'labels' in data and 'values' in data:
                ax.pie(data['values'], labels=data['labels'], autopct='%1.1f%%', startangle=90)
                ax.set_ylabel('')

            elif chart_type == 'bar' and 'labels' in data and 'values' in data:
                ax.bar(data['labels'], data['values'], color='skyblue')
                ax.set_xlabel('')
                ax.set_ylabel('数量')

            if title:
                ax.set_title(title, fontsize=14, fontweight='bold')

            plt.tight_layout()

            chart_path = os.path.join(EXPORT_DIR, f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            return chart_path
        except Exception as e:
            print(f"[错误] 图表生成失败: {e}")
            return None

# ==========================================
# 工具函数
# ==========================================
def generate_unique_id() -> str:
    """生成唯一ID"""
    return hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:16]

def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))

def format_datetime(dt_str: str, format: str = '%Y-%m-%d %H:%M:%S') -> str:
    """格式化日期时间"""
    try:
        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        return dt.strftime(format)
    except:
        return dt_str

def format_date(dt_str: str) -> str:
    """格式化日期"""
    return format_datetime(dt_str, '%Y-%m-%d')

def calculate_age(birthday: str) -> int:
    """计算年龄"""
    try:
        birth = datetime.strptime(birthday, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birth.year
        if today.month < birth.month or (today.month == birth.month and today.day < birth.day):
            age -= 1
        return age
    except:
        return 0

def get_weekday_name(weekday: int, language: str = 'zh') -> str:
    """获取星期名称"""
    if language == 'zh':
        weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    else:
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return weekdays[weekday] if 0 <= weekday < 7 else ''

def get_date_range(start_date: str, end_date: str) -> List[str]:
    """获取日期范围内的所有日期"""
    dates = []
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        current = start
        while current <= end:
            dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
    except:
        pass
    return dates

def compress_image(image_path: str, max_size: Tuple[int, int] = (800, 600), quality: int = 85) -> str:
    """压缩图片"""
    if not PIL_AVAILABLE:
        return image_path

    try:
        img = Image.open(image_path)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        compressed_path = os.path.join(
            os.path.dirname(image_path),
            f"compressed_{os.path.basename(image_path)}"
        )
        img.save(compressed_path, quality=quality, optimize=True)
        return compressed_path
    except:
        return image_path

def create_thumbnail(image_path: str, size: Tuple[int, int] = (200, 200)) -> Optional[str]:
    """创建缩略图"""
    if not PIL_AVAILABLE:
        return None

    try:
        img = Image.open(image_path)
        img.thumbnail(size, Image.Resampling.LANCZOS)

        thumb_path = os.path.join(
            os.path.dirname(image_path),
            f"thumb_{os.path.basename(image_path)}"
        )
        img.save(thumb_path)
        return thumb_path
    except:
        return None

# ==========================================
# UI组件库
# ==========================================
class UIComponents:
    """UI组件库"""

    @staticmethod
    def create_button(parent, text: str, command: Callable, **kwargs) -> tk.Button:
        """创建按钮"""
        default_style = {
            'font': ('Microsoft YaHei', 10),
            'relief': tk.FLAT,
            'cursor': 'hand2',
            'padx': 15,
            'pady': 5
        }
        default_style.update(kwargs)

        btn = tk.Button(parent, text=text, command=command, **default_style)
        return btn

    @staticmethod
    def create_label(parent, text: str, **kwargs) -> tk.Label:
        """创建标签"""
        default_style = {
            'font': ('Microsoft YaHei', 10),
            'bg': parent.cget('bg') if hasattr(parent, 'cget') else '#f5f5f5'
        }
        default_style.update(kwargs)

        label = tk.Label(parent, text=text, **default_style)
        return label

    @staticmethod
    def create_entry(parent, textvariable: tk.StringVar = None, **kwargs) -> tk.Entry:
        """创建输入框"""
        default_style = {
            'font': ('Microsoft YaHei', 10),
            'relief': tk.SOLID,
            'bd': 1
        }
        default_style.update(kwargs)

        entry = tk.Entry(parent, textvariable=textvariable, **default_style)
        return entry

    @staticmethod
    def create_text(parent, **kwargs) -> tk.Text:
        """创建文本框"""
        default_style = {
            'font': ('Microsoft YaHei', 10),
            'relief': tk.SOLID,
            'bd': 1
        }
        default_style.update(kwargs)

        text = tk.Text(parent, **default_style)
        return text

    @staticmethod
    def create_listbox(parent, **kwargs) -> tk.Listbox:
        """创建列表框"""
        default_style = {
            'font': ('Microsoft YaHei', 10),
            'relief': tk.SOLID,
            'bd': 1,
            'selectmode': tk.SINGLE,
            'activestyle': 'none'
        }
        default_style.update(kwargs)

        listbox = tk.Listbox(parent, **default_style)
        return listbox

    @staticmethod
    def create_combobox(parent, values: List[str], textvariable: tk.StringVar = None, **kwargs) -> tk.ttk.Combobox:
        """创建下拉框"""
        try:
            combobox = tk.ttk.Combobox(parent, values=values, textvariable=textvariable, **kwargs)
            return combobox
        except:
            var = tk.StringVar(value=values[0] if values else '')
            return UIComponents._create_simple_combobox(parent, var, values)

    @staticmethod
    def _create_simple_combobox(parent, var, values):
        """简单下拉框实现"""
        frame = tk.Frame(parent)

        def on_select(value):
            var.set(value)

        btn = tk.Menubutton(frame, textvariable=var, relief=tk.RAISED)
        menu = tk.Menu(btn, tearoff=0)
        btn.config(menu=menu)

        for value in values:
            menu.add_command(label=value, command=lambda v=value: on_select(v))

        def get_value():
            return var.get()

        def set_value(value):
            var.set(value)

        frame.get_value = get_value
        frame.set_value = set_value
        frame.winfo_toplevel = lambda: frame

        return frame

    @staticmethod
    def create_scrolled_frame(parent, **kwargs) -> tk.Frame:
        """创建滚动框架"""
        canvas = tk.Canvas(parent, **kwargs)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas)

        frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        return frame, canvas, scrollbar

    @staticmethod
    def create_notebook(parent) -> tk.ttk.Notebook:
        """创建选项卡"""
        try:
            return tk.ttk.Notebook(parent)
        except:
            return UIComponents._create_simple_notebook(parent)

    @staticmethod
    def _create_simple_notebook(parent):
        """简单选项卡实现"""
        class SimpleNotebook:
            def __init__(self, parent):
                self.parent = parent
                self.tabs = []
                self.current_index = 0

            def add(self, child, **kwargs):
                tab = tk.Frame(child)
                self.tabs.append(tab)
                return tab

            def select(self, index):
                self.current_index = index
                for i, tab in enumerate(self.tabs):
                    if i == index:
                        tab.pack(fill=tk.BOTH, expand=True)
                    else:
                        tab.pack_forget()

        return SimpleNotebook(parent)

    @staticmethod
    def create_progressbar(parent, **kwargs) -> tk.ttk.Progressbar:
        """创建进度条"""
        try:
            return tk.ttk.Progressbar(parent, **kwargs)
        except:
            canvas = tk.Canvas(parent, height=20, bg='white')
            canvas.progress_rect = None

            def set_progress(value):
                canvas.delete('progress')
                width = canvas.winfo_width() or 100
                canvas.create_rectangle(0, 0, width * value / 100, 20, fill='green', tags='progress')

            canvas.set_progress = set_progress
            return canvas

    @staticmethod
    def create_treeview(parent, columns: List[str], headings: List[str] = None, **kwargs) -> tk.ttk.Treeview:
        """创建树形视图"""
        try:
            tree = tk.ttk.Treeview(parent, columns=columns, show='headings', **kwargs)

            if headings is None:
                headings = columns

            for col, heading in zip(columns, headings):
                tree.heading(col, text=heading)
                tree.column(col, width=100)

            return tree
        except:
            frame = tk.Frame(parent)
            listbox = UIComponents.create_listbox(frame)
            listbox.pack(fill=tk.BOTH, expand=True)

            def insert(**kwargs):
                values = [kwargs.get(col, '') for col in columns]
                listbox.insert(tk.END, ' | '.join(str(v) for v in values))

            frame.insert = insert
            return frame

# 由于代码量较大，我会将主应用类和其他UI组件保存到单独的文件中
# 这里先保存核心功能模块



# ==========================================
# 安全回调调度器
# ==========================================
def safe_after_call(root, delay_ms: int, func: Callable, *args, **kwargs):
    """安全的异步回调调度器"""
    def safe_wrapper():
        try:
            if not root.winfo_exists():
                print(f"[安全] 窗口已销毁，取消回调: {func.__name__}")
                return
            func(*args, **kwargs)
        except tk.TclError as e:
            if "invalid command name" in str(e) or "application has been destroyed" in str(e):
                return
            raise
        except Exception as e:
            print(f"[错误] 回调异常: {e}")
            raise
    return root.after(delay_ms, safe_wrapper)

# ==========================================
# 动画引擎
# ==========================================
class AnimationEngine:
    """动画引擎"""

    def __init__(self):
        self.config = ConfigManager()
        speed_map = {'slow': 80, 'medium': 50, 'fast': 30}
        speed = self.config.get('animation_speed', 'medium')
        self.animation_speed = speed_map.get(speed, 50)
        self.animation_colors = [
            "#f44336", "#e91e63", "#9c27b0", "#673ab7", "#3f51b5",
            "#2196f3", "#00bcd4", "#009688", "#4caf50", "#ff9800", "#ff5722",
            "#795548", "#607d8b", "#ffeb3b", "#ffc107", "#ff9800", "#ff5722"
        ]
        self._active_animations = set()

    def victory_animation(self, widget, winners: List[str] = None):
        """胜利动画"""
        if not self.config.get('animation_enabled', True):
            return

        def animate(step=0):
            if step < 30:
                try:
                    if widget.winfo_exists():
                        widget.config(fg=self.animation_colors[step % len(self.animation_colors)])
                        widget.after(80, lambda: animate(step + 1))
                except tk.TclError:
                    return

        animate()

    def rolling_animation(self, widget, names: List[str], callback: Callable = None):
        """滚动动画"""
        if not self.config.get('animation_enabled', True) or not names:
            if callback:
                callback()
            return

        index = [0]
        total_steps = random.randint(20, 40)

        def animate():
            if index[0] < total_steps:
                name = random.choice(names)
                try:
                    widget.config(text=name)
                except tk.TclError:
                    return
                index[0] += 1
                widget.after(self.animation_speed, animate)
            else:
                if callback:
                    callback()

        animate()

    def color_transition(self, widget, color1: str, color2: str, duration: int = 500):
        """颜色渐变"""
        if not self.config.get('animation_enabled', True):
            try:
                widget.config(fg=color2)
            except tk.TclError:
                pass
            return

        def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
            return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

        start_rgb = hex_to_rgb(color1)
        end_rgb = hex_to_rgb(color2)
        steps = max(1, int(duration / 16))

        def animate(step=0):
            if step <= steps:
                try:
                    ratio = step / steps
                    current_rgb = tuple(int(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * ratio) for i in range(3))
                    widget.config(fg=rgb_to_hex(current_rgb))
                    if step < steps:
                        widget.after(16, lambda: animate(step + 1))
                except tk.TclError:
                    return

        animate()

    def pulse_animation(self, widget, base_color: str, pulse_color: str, cycles: int = 3):
        """脉冲动画"""
        if not self.config.get('animation_enabled', True):
            return

        def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
            return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

        start_rgb = hex_to_rgb(base_color)
        end_rgb = hex_to_rgb(pulse_color)

        step = [0]

        def animate():
            if step[0] < cycles * 2:
                try:
                    if step[0] % 2 == 0:
                        ratio = step[0] / (cycles * 2)
                    else:
                        ratio = 1 - step[0] / (cycles * 2)

                    current_rgb = tuple(int(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * ratio) for i in range(3))
                    widget.config(fg=rgb_to_hex(current_rgb))
                    step[0] += 1
                    widget.after(150, animate)
                except tk.TclError:
                    return

        animate()

    def shake_animation(self, widget, intensity: int = 5):
        """震动动画"""
        if not self.config.get('animation_enabled', True):
            return

        try:
            original_x = widget.winfo_x()
            original_y = widget.winfo_y()
        except:
            return

        step = [0]

        def animate():
            if step[0] < intensity * 2:
                offset = random.randint(-5, 5)
                try:
                    widget.place_configure(x=original_x + offset)
                    widget.after(30, animate)
                except tk.TclError:
                    return
                step[0] += 1
            else:
                try:
                    widget.place_configure(x=original_x, y=original_y)
                except:
                    pass

        animate()

    def bounce_animation(self, widget):
        """弹跳动画"""
        if not self.config.get('animation_enabled', True):
            return

        try:
            original_y = widget.winfo_y()
        except:
            return

        step = [0]
        max_bounce = 20

        def animate():
            if step[0] < 10:
                try:
                    if step[0] % 2 == 0:
                        offset = -max_bounce * (step[0] / 10)
                    else:
                        offset = -max_bounce * (1 - step[0] / 10)
                    widget.place_configure(y=original_y + offset)
                    widget.after(50, animate)
                except tk.TclError:
                    return
                step[0] += 1
            else:
                try:
                    widget.place_configure(y=original_y)
                except:
                    pass

        animate()

    def fade_in_animation(self, widget, duration: int = 500):
        """淡入动画"""
        if not self.config.get('animation_enabled', True):
            widget.place(tk.NORMAL)
            return

        alpha = [0.0]
        step = 0.05

        def animate():
            if alpha[0] < 1.0:
                try:
                    widget.attributes('-alpha', alpha[0])
                    alpha[0] += step
                    widget.after(int(duration * step), animate)
                except tk.TclError:
                    return

        widget.attributes('-alpha', 0)
        widget.place(tk.NORMAL)
        animate()

    def fade_out_animation(self, widget, duration: int = 500, callback: Callable = None):
        """淡出动画"""
        if not self.config.get('animation_enabled', True):
            widget.place(tk.HIDDEN)
            if callback:
                callback()
            return

        alpha = [1.0]
        step = 0.05

        def animate():
            if alpha[0] > 0:
                try:
                    widget.attributes('-alpha', alpha[0])
                    alpha[0] -= step
                    widget.after(int(duration * step), animate)
                except tk.TclError:
                    return
            else:
                widget.place(tk.HIDDEN)
                if callback:
                    callback()

        animate()

# ==========================================
# 主应用类
# ==========================================
class SmartPickerProApp:
    """SmartPicker Pro 主应用"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.config = ConfigManager()

        # 初始化数据库
        self.db = DatabaseManager()
        self.student_manager = StudentManager(self.db)
        self.class_manager = ClassManager(self.db)
        self.attendance_manager = AttendanceManager(self.db)
        self.draw_record_manager = DrawRecordManager(self.db)
        self.reward_manager = RewardManager(self.db)
        self.backup_manager = BackupManager(self.db)
        self.import_export_manager = ImportExportManager(self.db)
        self.statistics_analyzer = StatisticsAnalyzer(self.db)
        self.sound_manager = SoundManager()
        self.animation_engine = AnimationEngine()

        # 状态变量
        self.current_class_id = None
        self.current_class = None
        self.students = []
        self.blacklist = []
        self.weights = {}
        self.is_rolling = False
        self.history_counter = 0
        self.history_data = []
        self.draw_mode = DrawMode.NORMAL
        self._rolling_pool = []
        self._rolling_index = 0

        # 主题
        self.theme = self.config.get_theme()

        # 初始化UI
        self._setup_window()
        self._setup_ui()
        self._bind_shortcuts()
        self._load_initial_data()

        # 自动检查更新
        if self.config.get('auto_check_update', True):
            threading.Thread(target=self._check_for_updates, daemon=True).start()

        # 自动备份
        if self.config.get('auto_backup', True):
            threading.Thread(target=self._auto_backup, daemon=True).start()

    def _setup_window(self):
        """设置窗口"""
        self.root.title(f"{APP_NAME} V{VERSION}")
        self.root.geometry(self.config.get('window_geometry', '1200x800'))
        self.root.minsize(800, 600)
        self.root.configure(bg=self.theme['background'])

        try:
            self.root.iconbitmap(default=os.path.join(BASE_DIR, "icon.ico"))
        except:
            pass

    def _setup_ui(self):
        """设置UI"""
        # 主容器
        self.main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self.theme['background'])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 左侧导航栏
        self.left_panel = self._create_left_panel()

        # 右侧内容区
        self.right_panel = self._create_right_panel()

        self.main_container.add(self.left_panel, width=200)
        self.main_container.add(self.right_panel)

        # 状态栏
        self._create_status_bar()

    def _create_left_panel(self) -> tk.Frame:
        """创建左侧导航面板"""
        panel = tk.Frame(self.root, bg=self.theme['primary'], width=200)

        # Logo区域
        logo_frame = tk.Frame(panel, bg=self.theme['primary'], height=100)
        logo_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            logo_frame, text="📚",
            font=("Microsoft YaHei", 40),
            bg=self.theme['primary'], fg='white'
        ).pack(pady=(20, 5))

        tk.Label(
            logo_frame, text=APP_NAME,
            font=("Microsoft YaHei", 14, "bold"),
            bg=self.theme['primary'], fg='white'
        ).pack()

        # 导航按钮
        nav_buttons = [
            ("🎯 点名", lambda: self._show_page('draw')),
            ("👥 学生", lambda: self._show_page('students')),
            ("🏫 班级", lambda: self._show_page('classes')),
            ("📋 考勤", lambda: self._show_page('attendance')),
            ("📊 统计", lambda: self._show_page('statistics')),
            ("📜 历史", lambda: self._show_page('history')),
            ("⚙️ 设置", lambda: self._show_page('settings')),
            ("ℹ️ 关于", lambda: self._show_page('about')),
        ]

        for text, command in nav_buttons:
            btn = tk.Button(
                panel, text=text,
                font=("Microsoft YaHei", 11),
                bg=self.theme['primary'], fg='white',
                relief=tk.FLAT, cursor='hand2',
                activebackground=self.theme['secondary'],
                activeforeground='white',
                anchor='w', padx=20,
                command=command
            )
            btn.pack(fill=tk.X, padx=5, pady=2)

        # 底部信息
        bottom_frame = tk.Frame(panel, bg=self.theme['primary'])
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        tk.Label(
            bottom_frame, text=f"V{VERSION}",
            font=("Microsoft YaHei", 9),
            bg=self.theme['primary'], fg='white', alpha=0.7
        ).pack()

        return panel

    def _create_right_panel(self) -> tk.Frame:
        """创建右侧内容面板"""
        panel = tk.Frame(self.root, bg=self.theme['background'])

        # 内容页容器
        self.pages = {}
        self.page_container = tk.Frame(panel, bg=self.theme['background'])
        self.page_container.pack(fill=tk.BOTH, expand=True)

        # 创建各页面
        self._create_draw_page()
        self._create_students_page()
        self._create_classes_page()
        self._create_attendance_page()
        self._create_statistics_page()
        self._create_history_page()
        self._create_settings_page()
        self._create_about_page()

        # 默认显示点名页面
        self._show_page('draw')

        return panel

    def _create_draw_page(self):
        """创建点名页面"""
        page = tk.Frame(self.page_container, bg=self.theme['background'])
        self.pages['draw'] = page

        # 标题栏
        title_frame = tk.Frame(page, bg=self.theme['background'])
        title_frame.pack(fill=tk.X, pady=20, padx=20)

        tk.Label(
            title_frame, text="🎯 随机点名",
            font=("Microsoft YaHei", 24, "bold"),
            fg=self.theme['primary'], bg=self.theme['background']
        ).pack(side=tk.LEFT)

        # 班级选择
        self.class_var = tk.StringVar()
        class_frame = tk.Frame(title_frame, bg=self.theme['background'])
        class_frame.pack(side=tk.RIGHT)

        tk.Label(
            class_frame, text="班级:",
            font=("Microsoft YaHei", 11),
            bg=self.theme['background']
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.class_combobox = tk.ttk.Combobox(
            class_frame, textvariable=self.class_var,
            font=("Microsoft YaHei", 10), width=15,
            state='readonly'
        )
        self.class_combobox.pack(side=tk.LEFT)
        self.class_combobox.bind('<<ComboboxSelected>>', self._on_class_changed)

        # 主显示区
        display_frame = tk.Frame(
            page, bg=self.theme['surface'],
            bd=2, relief=tk.SOLID
        )
        display_frame.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)

        # 名字显示
        self.name_display = tk.Label(
            display_frame, text="点击「开始」进行点名",
            font=("Microsoft YaHei", 55, "bold"),
            fg=self.theme['primary'], bg=self.theme['surface'],
            wraplength=800, justify='center'
        )
        self.name_display.pack(pady=60, padx=20, expand=True)

        # 控制面板
        control_frame = tk.Frame(page, bg=self.theme['background'])
        control_frame.pack(pady=20, fill=tk.X, padx=40)

        # 抽取模式选择
        mode_frame = tk.Frame(control_frame, bg=self.theme['background'])
        mode_frame.pack(side=tk.LEFT)

        tk.Label(
            mode_frame, text="抽取模式:",
            font=("Microsoft YaHei", 11),
            bg=self.theme['background']
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.mode_var = tk.StringVar(value="普通抽取")
        modes = [
            "普通抽取", "加权抽取", "完全随机", "分组抽取",
            "竞赛模式", "轮盘模式", "抽奖模式", "顺序模式",
            "随机分组", "淘汰模式"
        ]
        self.mode_combobox = tk.ttk.Combobox(
            mode_frame, textvariable=self.mode_var,
            values=modes, font=("Microsoft YaHei", 10), width=12,
            state='readonly'
        )
        self.mode_combobox.pack(side=tk.LEFT)

        # 抽取人数
        count_frame = tk.Frame(control_frame, bg=self.theme['background'])
        count_frame.pack(side=tk.LEFT, padx=30)

        tk.Label(
            count_frame, text="抽取人数:",
            font=("Microsoft YaHei", 11),
            bg=self.theme['background']
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.draw_count_slider = tk.Scale(
            count_frame, from_=1, to=20,
            orient=tk.HORIZONTAL,
            font=("Microsoft YaHei", 10), length=150,
            bg=self.theme['background'], highlightthickness=0,
            troughcolor=self.theme['accent']
        )
        self.draw_count_slider.pack(side=tk.LEFT)
        self.draw_count_slider.set(self.config.get('default_draw_count', 1))

        # 开始/停止按钮
        self.draw_button = tk.Button(
            control_frame, text="▶ 开始",
            font=("Microsoft YaHei", 16, "bold"),
            width=12, height=2,
            bg=self.theme['success'], fg='white',
            relief=tk.FLAT, cursor='hand2',
            activebackground='#388e3c',
            command=self._toggle_draw
        )
        self.draw_button.pack(side=tk.RIGHT)

        # 历史记录
        history_frame = tk.LabelFrame(
            page, text="抽取历史",
            font=("Microsoft YaHei", 12, "bold"),
            bg=self.theme['background'], padx=10, pady=5
        )
        history_frame.pack(pady=10, padx=40, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_text = tk.Text(
            history_frame, font=("Microsoft YaHei", 10), height=8,
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED, bg=self.theme['surface']
        )
        self.history_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_text.yview)

        self.history_text.tag_configure("even_row", background="#e8f5e9")
        self.history_text.tag_configure("odd_row", background="#ffffff")

    def _create_students_page(self):
        """创建学生管理页面"""
        page = tk.Frame(self.page_container, bg=self.theme['background'])
        self.pages['students'] = page

        # 标题栏
        title_frame = tk.Frame(page, bg=self.theme['background'])
        title_frame.pack(fill=tk.X, pady=20, padx=20)

        tk.Label(
            title_frame, text="👥 学生管理",
            font=("Microsoft YaHei", 24, "bold"),
            fg=self.theme['primary'], bg=self.theme['background']
        ).pack(side=tk.LEFT)

        # 操作按钮
        btn_frame = tk.Frame(title_frame, bg=self.theme['background'])
        btn_frame.pack(side=tk.RIGHT)

        for text, cmd, color in [
            ("➕ 添加", self._add_student, self.theme['success']),
            ("📥 导入", self._import_students, self.theme['info']),
            ("📤 导出", self._export_students, self.theme['warning']),
            ("🔄 刷新", self._refresh_students, self.theme['primary']),
        ]:
            tk.Button(
                btn_frame, text=text,
                font=("Microsoft YaHei", 10),
                bg=color, fg='white',
                relief=tk.FLAT, cursor='hand2',
                padx=15, pady=5,
                command=cmd
            ).pack(side=tk.LEFT, padx=5)

        # 搜索栏
        search_frame = tk.Frame(page, bg=self.theme['background'])
        search_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        tk.Label(
            search_frame, text="🔍",
            font=("Microsoft YaHei", 12),
            bg=self.theme['background']
        ).pack(side=tk.LEFT)

        self.student_search_var = tk.StringVar()
        self.student_search_entry = tk.Entry(
            search_frame, textvariable=self.student_search_var,
            font=("Microsoft YaHei", 11), width=30,
            relief=tk.SOLID, bd=1
        )
        self.student_search_entry.pack(side=tk.LEFT, padx=10)
        self.student_search_entry.bind('<KeyRelease>', self._on_student_search)

        # 学生列表
        list_frame = tk.Frame(page, bg=self.theme['surface'], bd=1, relief=tk.SOLID)
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # 表头
        header_frame = tk.Frame(list_frame, bg=self.theme['primary'])
        header_frame.pack(fill=tk.X)

        headers = ['学号', '姓名', '性别', '电话', '积分', '星星', '出勤率', '操作']
        widths = [80, 100, 60, 120, 60, 60, 80, 150]

        for i, (header, width) in enumerate(zip(headers, widths)):
            tk.Label(
                header_frame, text=header,
                font=("Microsoft YaHei", 10, "bold"),
                bg=self.theme['primary'], fg='white',
                width=width // 8, pady=8
            ).pack(side=tk.LEFT, padx=1)

        # 列表容器
        self.student_list_frame = tk.Frame(list_frame, bg=self.theme['surface'])
        self.student_list_frame.pack(fill=tk.BOTH, expand=True)

        # 滚动条
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_classes_page(self):
        """创建班级管理页面"""
        page = tk.Frame(self.page_container, bg=self.theme['background'])
        self.pages['classes'] = page

        # 标题栏
        title_frame = tk.Frame(page, bg=self.theme['background'])
        title_frame.pack(fill=tk.X, pady=20, padx=20)

        tk.Label(
            title_frame, text="🏫 班级管理",
            font=("Microsoft YaHei", 24, "bold"),
            fg=self.theme['primary'], bg=self.theme['background']
        ).pack(side=tk.LEFT)

        btn_frame = tk.Frame(title_frame, bg=self.theme['background'])
        btn_frame.pack(side=tk.RIGHT)

        for text, cmd, color in [
            ("➕ 添加班级", self._add_class, self.theme['success']),
            ("📥 导入", self._import_classes, self.theme['info']),
            ("📤 导出", self._export_classes, self.theme['warning']),
            ("🔄 刷新", self._refresh_classes, self.theme['primary']),
        ]:
            tk.Button(
                btn_frame, text=text,
                font=("Microsoft YaHei", 10),
                bg=color, fg='white',
                relief=tk.FLAT, cursor='hand2',
                padx=15, pady=5,
                command=cmd
            ).pack(side=tk.LEFT, padx=5)

        # 班级列表
        self.classes_list_frame = tk.Frame(page, bg=self.theme['background'])
        self.classes_list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    def _create_attendance_page(self):
        """创建考勤管理页面"""
        page = tk.Frame(self.page_container, bg=self.theme['background'])
        self.pages['attendance'] = page

        # 标题栏
        title_frame = tk.Frame(page, bg=self.theme['background'])
        title_frame.pack(fill=tk.X, pady=20, padx=20)

        tk.Label(
            title_frame, text="📋 考勤管理",
            font=("Microsoft YaHei", 24, "bold"),
            fg=self.theme['primary'], bg=self.theme['background']
        ).pack(side=tk.LEFT)

        # 考勤操作
        btn_frame = tk.Frame(title_frame, bg=self.theme['background'])
        btn_frame.pack(side=tk.RIGHT)

        for text, cmd, color in [
            ("✅ 一键考勤", self._quick_attendance, self.theme['success']),
            ("📊 考勤报表", self._show_attendance_report, self.theme['info']),
            ("📤 导出报表", self._export_attendance, self.theme['warning']),
        ]:
            tk.Button(
                btn_frame, text=text,
                font=("Microsoft YaHei", 10),
                bg=color, fg='white',
                relief=tk.FLAT, cursor='hand2',
                padx=15, pady=5,
                command=cmd
            ).pack(side=tk.LEFT, padx=5)

        # 考勤统计
        stats_frame = tk.Frame(page, bg=self.theme['surface'], bd=1, relief=tk.SOLID)
        stats_frame.pack(pady=10, padx=20, fill=tk.X)

        self.attendance_stats_labels = {}
        stats_items = [
            ('total', '📊 总人数', '0'),
            ('present', '✅ 出勤', '0'),
            ('absent', '❌ 缺勤', '0'),
            ('late', '⏰ 迟到', '0'),
            ('leave', '📝 请假', '0'),
        ]

        for key, text, default in stats_items:
            frame = tk.Frame(stats_frame, bg=self.theme['surface'], padx=20, pady=15)
            frame.pack(side=tk.LEFT, expand=True)

            label = tk.Label(
                frame, text=text,
                font=("Microsoft YaHei", 10),
                bg=self.theme['surface']
            )
            label.pack()

            value_label = tk.Label(
                frame, text=default,
                font=("Microsoft YaHei", 20, "bold"),
                bg=self.theme['surface'], fg=self.theme['primary']
            )
            value_label.pack()

            self.attendance_stats_labels[key] = value_label

        # 考勤列表
        list_frame = tk.LabelFrame(
            page, text="今日考勤",
            font=("Microsoft YaHei", 12, "bold"),
            bg=self.theme['background'], padx=10, pady=5
        )
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.attendance_listbox = tk.Listbox(
            list_frame, font=("Microsoft YaHei", 10),
            yscrollcommand=scrollbar.set,
            bg=self.theme['surface']
        )
        self.attendance_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.attendance_listbox.yview)

    def _create_statistics_page(self):
        """创建统计分析页面"""
        page = tk.Frame(self.page_container, bg=self.theme['background'])
        self.pages['statistics'] = page

        # 标题栏
        title_frame = tk.Frame(page, bg=self.theme['background'])
        title_frame.pack(fill=tk.X, pady=20, padx=20)

        tk.Label(
            title_frame, text="📊 数据统计",
            font=("Microsoft YaHei", 24, "bold"),
            fg=self.theme['primary'], bg=self.theme['background']
        ).pack(side=tk.LEFT)

        # 统计卡片
        cards_frame = tk.Frame(page, bg=self.theme['background'])
        cards_frame.pack(pady=10, padx=20, fill=tk.X)

        self.stats_cards = {}
        stats_cards_data = [
            ('students', '👥 学生总数', '0'),
            ('classes', '🏫 班级总数', '0'),
            ('draws', '🎯 抽取次数', '0'),
            ('attendance', '📋 考勤次数', '0'),
        ]

        for key, text, default in stats_cards_data:
            card = tk.Frame(
                cards_frame, bg=self.theme['surface'],
                bd=1, relief=tk.SOLID, padx=20, pady=15
            )
            card.pack(side=tk.LEFT, expand=True, padx=5)

            tk.Label(
                card, text=text,
                font=("Microsoft YaHei", 10),
                bg=self.theme['surface']
            ).pack()

            value_label = tk.Label(
                card, text=default,
                font=("Microsoft YaHei", 24, "bold"),
                bg=self.theme['surface'], fg=self.theme['primary']
            )
            value_label.pack()

            self.stats_cards[key] = value_label

        # 排行榜
        leaderboard_frame = tk.LabelFrame(
            page, text="🏆 积分排行榜",
            font=("Microsoft YaHei", 12, "bold"),
            bg=self.theme['background'], padx=10, pady=5
        )
        leaderboard_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(leaderboard_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.leaderboard_listbox = tk.Listbox(
            leaderboard_frame, font=("Microsoft YaHei", 10),
            yscrollcommand=scrollbar.set,
            bg=self.theme['surface']
        )
        self.leaderboard_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.leaderboard_listbox.yview)

    def _create_history_page(self):
        """创建历史记录页面"""
        page = tk.Frame(self.page_container, bg=self.theme['background'])
        self.pages['history'] = page

        # 标题栏
        title_frame = tk.Frame(page, bg=self.theme['background'])
        title_frame.pack(fill=tk.X, pady=20, padx=20)

        tk.Label(
            title_frame, text="📜 历史记录",
            font=("Microsoft YaHei", 24, "bold"),
            fg=self.theme['primary'], bg=self.theme['background']
        ).pack(side=tk.LEFT)

        btn_frame = tk.Frame(title_frame, bg=self.theme['background'])
        btn_frame.pack(side=tk.RIGHT)

        tk.Button(
            btn_frame, text="🔄 刷新",
            font=("Microsoft YaHei", 10),
            bg=self.theme['primary'], fg='white',
            relief=tk.FLAT, cursor='hand2',
            padx=15, pady=5,
            command=self._refresh_history
        ).pack(side=tk.LEFT)

        # 历史列表
        list_frame = tk.Frame(page, bg=self.theme['surface'], bd=1, relief=tk.SOLID)
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_listbox = tk.Listbox(
            list_frame, font=("Microsoft YaHei", 10),
            yscrollcommand=scrollbar.set,
            bg=self.theme['surface']
        )
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)

    def _create_settings_page(self):
        """创建设置页面"""
        page = tk.Frame(self.page_container, bg=self.theme['background'])
        self.pages['settings'] = page

        # 标题栏
        title_frame = tk.Frame(page, bg=self.theme['background'])
        title_frame.pack(fill=tk.X, pady=20, padx=20)

        tk.Label(
            title_frame, text="⚙️ 系统设置",
            font=("Microsoft YaHei", 24, "bold"),
            fg=self.theme['primary'], bg=self.theme['background']
        ).pack(side=tk.LEFT)

        # 设置项
        settings_container = tk.Frame(page, bg=self.theme['background'])
        settings_container.pack(pady=10, padx=40, fill=tk.BOTH, expand=True)

        # 主题设置
        theme_frame = tk.LabelFrame(
            settings_container, text="🎨 界面主题",
            font=("Microsoft YaHei", 11, "bold"),
            bg=self.theme['background'], padx=15, pady=10
        )
        theme_frame.pack(fill=tk.X, pady=(0, 15))

        self.theme_var = tk.StringVar(value=self.config.get('theme', '默认蓝色'))
        theme_names = list(THEMES.keys())

        for theme_name in theme_names:
            tk.Radiobutton(
                theme_frame, text=theme_name,
                variable=self.theme_var, value=theme_name,
                font=("Microsoft YaHei", 10),
                bg=self.theme['background'],
                command=self._change_theme
            ).pack(anchor='w', pady=2)

        # 声音设置
        sound_frame = tk.LabelFrame(
            settings_container, text="🔊 声音设置",
            font=("Microsoft YaHei", 11, "bold"),
            bg=self.theme['background'], padx=15, pady=10
        )
        sound_frame.pack(fill=tk.X, pady=(0, 15))

        self.sound_enabled_var = tk.BooleanVar(value=self.config.get('sound_enabled', True))
        tk.Checkbutton(
            sound_frame, text="启用音效",
            variable=self.sound_enabled_var,
            font=("Microsoft YaHei", 10),
            bg=self.theme['background'],
            command=self._save_sound_settings
        ).pack(anchor='w', pady=2)

        self.voice_enabled_var = tk.BooleanVar(value=self.config.get('voice_enabled', True))
        tk.Checkbutton(
            sound_frame, text="启用语音播报",
            variable=self.voice_enabled_var,
            font=("Microsoft YaHei", 10),
            bg=self.theme['background'],
            command=self._save_sound_settings
        ).pack(anchor='w', pady=2)

        # 语言设置
        lang_frame = tk.LabelFrame(
            settings_container, text="🌐 语言设置",
            font=("Microsoft YaHei", 11, "bold"),
            bg=self.theme['background'], padx=15, pady=10
        )
        lang_frame.pack(fill=tk.X, pady=(0, 15))

        self.lang_var = tk.StringVar(value=self.config.get('language', '简体中文'))
        for lang in SUPPORTED_LANGUAGES:
            tk.Radiobutton(
                lang_frame, text=lang,
                variable=self.lang_var, value=lang,
                font=("Microsoft YaHei", 10),
                bg=self.theme['background'],
                command=self._change_language
            ).pack(anchor='w', pady=2)

        # 备份设置
        backup_frame = tk.LabelFrame(
            settings_container, text="💾 数据备份",
            font=("Microsoft YaHei", 11, "bold"),
            bg=self.theme['background'], padx=15, pady=10
        )
        backup_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Button(
            backup_frame, text="📦 创建备份",
            font=("Microsoft YaHei", 10),
            bg=self.theme['success'], fg='white',
            relief=tk.FLAT, cursor='hand2',
            padx=15, pady=5,
            command=self._create_backup
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            backup_frame, text="📥 恢复备份",
            font=("Microsoft YaHei", 10),
            bg=self.theme['warning'], fg='white',
            relief=tk.FLAT, cursor='hand2',
            padx=15, pady=5,
            command=self._restore_backup
        ).pack(side=tk.LEFT)

    def _create_about_page(self):
        """创建关于页面"""
        page = tk.Frame(self.page_container, bg=self.theme['background'])
        self.pages['about'] = page

        # Logo
        logo_frame = tk.Frame(page, bg=self.theme['background'])
        logo_frame.pack(pady=50)

        tk.Label(
            logo_frame, text="📚",
            font=("Microsoft YaHei", 80),
            bg=self.theme['background']
        ).pack()

        tk.Label(
            logo_frame, text=APP_NAME,
            font=("Microsoft YaHei", 28, "bold"),
            fg=self.theme['primary'], bg=self.theme['background']
        ).pack(pady=10)

        tk.Label(
            logo_frame, text=f"版本 {VERSION}",
            font=("Microsoft YaHei", 14),
            fg=self.theme['text'], bg=self.theme['background']
        ).pack()

        # 信息
        info_frame = tk.Frame(page, bg=self.theme['background'])
        info_frame.pack(pady=30)

        info_items = [
            f"作者: {AUTHOR}",
            "功能: 课堂点名、考勤管理、数据统计",
            "支持: Windows 7/8/10/11",
            "Python: 3.8+",
        ]

        for info in info_items:
            tk.Label(
                info_frame, text=info,
                font=("Microsoft YaHei", 11),
                fg=self.theme['text'], bg=self.theme['background']
            ).pack(pady=3)

        # 版权
        tk.Label(
            page, text="© 2024 All Rights Reserved",
            font=("Microsoft YaHei", 9),
            fg='gray', bg=self.theme['background']
        ).pack(side=tk.BOTTOM, pady=20)

    def _create_status_bar(self):
        """创建状态栏"""
        status_bar = tk.Frame(self.root, bg=self.theme['primary'], height=25)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = tk.Label(
            status_bar, text="就绪",
            font=("Microsoft YaHei", 9),
            bg=self.theme['primary'], fg='white',
            anchor='w', padx=10
        )
        self.status_label.pack(side=tk.LEFT)

        self.time_label = tk.Label(
            status_bar, text="",
            font=("Microsoft YaHei", 9),
            bg=self.theme['primary'], fg='white',
            padx=10
        )
        self.time_label.pack(side=tk.RIGHT)

        self._update_time()

    def _update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self._update_time)

    def _show_page(self, page_name: str):
        """显示指定页面"""
        for name, page in self.pages.items():
            if name == page_name:
                page.pack(fill=tk.BOTH, expand=True)
            else:
                page.pack_forget()

        self.current_page = page_name

        # 页面刷新
        if page_name == 'draw':
            self._refresh_draw_page()
        elif page_name == 'students':
            self._refresh_students()
        elif page_name == 'classes':
            self._refresh_classes()
        elif page_name == 'attendance':
            self._refresh_attendance()
        elif page_name == 'statistics':
            self._refresh_statistics()
        elif page_name == 'history':
            self._refresh_history()

    def _bind_shortcuts(self):
        """绑定快捷键"""
        self.root.bind('<space>', lambda e: self._toggle_draw())
        self.root.bind('<Return>', lambda e: self._toggle_draw())
        self.root.bind('<r>', lambda e: self._reset_draw())
        self.root.bind('<Escape>', lambda e: self.root.destroy())

    def _load_initial_data(self):
        """加载初始数据"""
        self._refresh_draw_page()
        self._refresh_statistics()

    def _refresh_draw_page(self):
        """刷新点名页面"""
        # 加载班级列表
        classes = self.class_manager.get_all_classes()
        class_names = [c.name for c in classes]

        self.class_combobox['values'] = class_names
        if class_names and not self.class_var.get():
            self.class_var.set(class_names[0])
            self._load_class_data()

    def _on_class_changed(self, event=None):
        """班级选择改变"""
        self._load_class_data()

    def _load_class_data(self):
        """加载班级数据"""
        class_name = self.class_var.get()
        if not class_name:
            return

        classes = self.class_manager.get_all_classes()
        selected_class = next((c for c in classes if c.name == class_name), None)

        if selected_class:
            self.current_class_id = selected_class.id
            self.current_class = selected_class

            # 获取班级学生
            student_ids = self.class_manager.get_class_students(self.current_class_id)
            self.students = []

            for sid in student_ids:
                student = self.student_manager.get_student(sid)
                if student:
                    self.students.append(student)

            # 加载权重
            for student in self.students:
                self.weights[student.id] = student.weight

    def _toggle_draw(self):
        """切换点名状态"""
        if self.is_rolling:
            self._stop_draw()
        else:
            self._start_draw()

    def _start_draw(self):
        """开始点名"""
        if not self.students:
            messagebox.showwarning("警告", "请先选择一个班级并添加学生")
            return

        self.is_rolling = True
        self.draw_button.config(text="⏹ 停止", bg=self.theme['danger'])

        # 播放音效
        self.sound_manager.play_sound('rolling', loop=True)

        # 初始化滚动池
        self._rolling_pool = [s.id for s in self.students]
        self._rolling_index = 0

        # 开始滚动动画
        self._update_rolling()

    def _stop_draw(self):
        """停止点名"""
        self.is_rolling = False
        self.draw_button.config(text="▶ 开始", bg=self.theme['success'])

        # 停止音效
        self.sound_manager.stop_sound()

        # 执行最终抽取
        self._finish_draw()

    def _update_rolling(self):
        """更新滚动状态"""
        if self.is_rolling:
            count = self.draw_count_slider.get()
            pool = self._rolling_pool

            if pool:
                fake_winners = []
                for i in range(count):
                    idx = (self._rolling_index + i) % len(pool)
                    student = next((s for s in self.students if s.id == pool[idx]), None)
                    if student:
                        fake_winners.append(student.name)

                self.name_display.config(text="、".join(fake_winners) if fake_winners else "准备中...")

                self._rolling_index = (self._rolling_index + count) % len(pool)

            self.root.after(self.animation_engine.animation_speed, self._update_rolling)

    def _finish_draw(self):
        """完成抽取"""
        count = self.draw_count_slider.get()

        # 获取抽取模式
        mode_name = self.mode_var.get()
        mode_map = {
            "普通抽取": DrawMode.NORMAL,
            "加权抽取": DrawMode.WEIGHTED,
            "完全随机": DrawMode.RANDOM,
            "分组抽取": DrawMode.GROUP,
            "竞赛模式": DrawMode.CONTEST,
            "轮盘模式": DrawMode.WHEEL,
            "抽奖模式": DrawMode.LOTTERY,
            "顺序模式": DrawMode.SEQUENCE,
            "随机分组": DrawMode.RANDOM_GROUP,
            "淘汰模式": DrawMode.ELIMINATION,
        }
        self.draw_mode = mode_map.get(mode_name, DrawMode.NORMAL)

        # 根据模式抽取
        pool = self._rolling_pool.copy()
        winners = []

        for _ in range(min(count, len(pool))):
            if self.draw_mode == DrawMode.WEIGHTED:
                # 加权抽取
                weights = [self.weights.get(sid, 100.0) for sid in pool]
                chosen_idx = random.choices(range(len(pool)), weights=weights, k=1)[0]
            else:
                # 普通随机
                chosen_idx = random.randint(0, len(pool) - 1)

            chosen_id = pool.pop(chosen_idx)
            student = next((s for s in self.students if s.id == chosen_id), None)
            if student:
                winners.append(student)

        # 更新权重
        for winner in winners:
            self.weights[winner.id] = max(20.0, self.weights.get(winner.id, 100.0) / 2.0)

        # 保存抽取记录
        winners_data = [{'id': w.id, 'name': w.name, 'points': w.points} for w in winners]
        record = DrawRecord(
            id='',
            class_id=self.current_class_id,
            mode=self.draw_mode.value,
            winners=winners_data,
            draw_count=len(winners),
            date=datetime.now().strftime("%Y-%m-%d"),
            time=datetime.now().strftime("%H:%M:%S"),
            duration=0.0
        )
        self.draw_record_manager.add_record(record)

        # 更新学生抽取次数
        for winner in winners:
            winner.draw_count += 1
            winner.last_draw_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.student_manager.update_student(winner)

        # 显示结果
        winner_names = [w.name for w in winners]
        self.name_display.config(text="、".join(winner_names))
        self.animation_engine.victory_animation(self.name_display)

        # 语音播报
        self.sound_manager.speak_winners(winner_names)

        # 添加到历史
        self._add_to_history(winner_names)

    def _reset_draw(self):
        """重置点名"""
        self.name_display.config(text="点击「开始」进行点名")
        self.is_rolling = False
        self.draw_button.config(text="▶ 开始", bg=self.theme['success'])
        self.sound_manager.stop_sound()

        # 重置所有权重
        for student in self.students:
            self.weights[student.id] = 100.0
            self.student_manager.update_student(student)

    def _add_to_history(self, winners: List[str]):
        """添加到历史记录"""
        self.history_counter += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        winners_text = "、".join(winners)

        self.history_text.config(state=tk.NORMAL)
        tag = "even_row" if self.history_counter % 2 == 0 else "odd_row"
        entry = f"{self.history_counter:03d}. [{timestamp}] 抽取{len(winners)}人: {winners_text}\n"
        self.history_text.insert(tk.END, entry, tag)
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)

    def _refresh_students(self):
        """刷新学生列表"""
        students = self.student_manager.get_all_students()

        # 清空现有列表
        for widget in self.student_list_frame.winfo_children():
            widget.destroy()

        # 显示学生
        for student in students:
            row_frame = tk.Frame(self.student_list_frame, bg=self.theme['surface'])
            row_frame.pack(fill=tk.X, pady=1)

            if student.state == StudentState.SUSPENDED.value:
                row_frame.config(bg='#ffebee')

            present_rate = 'N/A'
            if student.attendance_count > 0:
                rate = (student.attendance_count - student.absent_count) / student.attendance_count * 100
                present_rate = f"{rate:.1f}%"

            values = [
                student.number, student.name, student.gender, student.phone,
                str(student.points), str(student.stars), present_rate
            ]

            for value in values:
                tk.Label(
                    row_frame, text=value,
                    font=("Microsoft YaHei", 9),
                    bg=row_frame.cget('bg'), pady=5, width=10
                ).pack(side=tk.LEFT, padx=1)

            btn_frame = tk.Frame(row_frame, bg=row_frame.cget('bg'))
            btn_frame.pack(side=tk.RIGHT, padx=5)

            tk.Button(
                btn_frame, text="✏️",
                font=("Microsoft YaHei", 9),
                bg=self.theme['info'], fg='white',
                relief=tk.FLAT, cursor='hand2',
                command=lambda s=student: self._edit_student(s)
            ).pack(side=tk.LEFT, padx=2)

            tk.Button(
                btn_frame, text="🗑️",
                font=("Microsoft YaHei", 9),
                bg=self.theme['danger'], fg='white',
                relief=tk.FLAT, cursor='hand2',
                command=lambda s=student: self._delete_student(s)
            ).pack(side=tk.LEFT, padx=2)

    def _on_student_search(self, event=None):
        """学生搜索"""
        keyword = self.student_search_var.get()
        if keyword:
            students = self.student_manager.search_students(keyword)
        else:
            students = self.student_manager.get_all_students()

        # 清空现有列表
        for widget in self.student_list_frame.winfo_children():
            widget.destroy()

        # 显示搜索结果
        for student in students:
            row_frame = tk.Frame(self.student_list_frame, bg=self.theme['surface'])
            row_frame.pack(fill=tk.X, pady=1)

            values = [student.number, student.name, student.gender, student.phone,
                     str(student.points), str(student.stars), 'N/A']

            for value in values:
                tk.Label(
                    row_frame, text=value,
                    font=("Microsoft YaHei", 9),
                    bg=self.theme['surface'], pady=5, width=10
                ).pack(side=tk.LEFT, padx=1)

    def _add_student(self):
        """添加学生"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加学生")
        dialog.geometry("400x500")
        dialog.resizable(False, False)

        fields = ['number', 'name', 'gender', 'phone', 'email', 'address', 'parent_name', 'parent_phone', 'note']
        labels = ['学号', '姓名', '性别', '电话', '邮箱', '地址', '家长姓名', '家长电话', '备注']
        entries = {}

        for i, (field, label) in enumerate(zip(fields, labels)):
            tk.Label(dialog, text=label + ":", font=("Microsoft YaHei", 10)).grid(
                row=i, column=0, sticky='e', padx=10, pady=5
            )
            if field == 'gender':
                var = tk.StringVar(value='男')
                tk.Radiobutton(dialog, text='男', variable=var, value='男').grid(
                    row=i, column=1, sticky='w'
                )
                tk.Radiobutton(dialog, text='女', variable=var, value='女').grid(
                    row=i, column=2, sticky='w'
                )
                entries[field] = var
            else:
                entries[field] = tk.Entry(dialog, font=("Microsoft YaHei", 10), width=25)
                entries[field].grid(row=i, column=1, columnspan=2, sticky='w', padx=10, pady=5)

        def save():
            student = Student(
                id='',
                number=entries['number'].get(),
                name=entries['name'].get(),
                gender=entries['gender'].get(),
                phone=entries['phone'].get(),
                email=entries['email'].get(),
                address=entries['address'].get(),
                parent_name=entries['parent_name'].get(),
                parent_phone=entries['parent_phone'].get(),
                note=entries['note'].get()
            )

            if not student.name:
                messagebox.showwarning("警告", "姓名不能为空")
                return

            if self.student_manager.add_student(student):
                messagebox.showinfo("成功", "学生添加成功")
                dialog.destroy()
                self._refresh_students()
            else:
                messagebox.showerror("错误", "添加失败")

        tk.Button(
            dialog, text="保存",
            font=("Microsoft YaHei", 11),
            bg=self.theme['success'], fg='white',
            relief=tk.FLAT, cursor='hand2',
            padx=30, pady=5,
            command=save
        ).grid(row=len(fields), column=0, columnspan=3, pady=20)

    def _edit_student(self, student: Student):
        """编辑学生"""
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑学生")
        dialog.geometry("400x500")
        dialog.resizable(False, False)

        fields = ['number', 'name', 'gender', 'phone', 'email', 'address', 'parent_name', 'parent_phone', 'note']
        labels = ['学号', '姓名', '性别', '电话', '邮箱', '地址', '家长姓名', '家长电话', '备注']
        entries = {}

        for i, (field, label) in enumerate(zip(fields, labels)):
            tk.Label(dialog, text=label + ":", font=("Microsoft YaHei", 10)).grid(
                row=i, column=0, sticky='e', padx=10, pady=5
            )
            if field == 'gender':
                var = tk.StringVar(value=student.gender)
                tk.Radiobutton(dialog, text='男', variable=var, value='男').grid(
                    row=i, column=1, sticky='w'
                )
                tk.Radiobutton(dialog, text='女', variable=var, value='女').grid(
                    row=i, column=2, sticky='w'
                )
                entries[field] = var
            else:
                entries[field] = tk.Entry(dialog, font=("Microsoft YaHei", 10), width=25)
                entries[field].grid(row=i, column=1, columnspan=2, sticky='w', padx=10, pady=5)
                entries[field].insert(0, getattr(student, field, ''))

        def save():
            student.number = entries['number'].get()
            student.name = entries['name'].get()
            student.gender = entries['gender'].get()
            student.phone = entries['phone'].get()
            student.email = entries['email'].get()
            student.address = entries['address'].get()
            student.parent_name = entries['parent_name'].get()
            student.parent_phone = entries['parent_phone'].get()
            student.note = entries['note'].get()

            if not student.name:
                messagebox.showwarning("警告", "姓名不能为空")
                return

            if self.student_manager.update_student(student):
                messagebox.showinfo("成功", "学生更新成功")
                dialog.destroy()
                self._refresh_students()
            else:
                messagebox.showerror("错误", "更新失败")

        tk.Button(
            dialog, text="保存",
            font=("Microsoft YaHei", 11),
            bg=self.theme['success'], fg='white',
            relief=tk.FLAT, cursor='hand2',
            padx=30, pady=5,
            command=save
        ).grid(row=len(fields), column=0, columnspan=3, pady=20)

    def _delete_student(self, student: Student):
        """删除学生"""
        if messagebox.askyesno("确认", f"确定要删除学生「{student.name}」吗？"):
            if self.student_manager.delete_student(student.id):
                messagebox.showinfo("成功", "学生已删除")
                self._refresh_students()
            else:
                messagebox.showerror("错误", "删除失败")

    def _import_students(self):
        """导入学生"""
        file_path = filedialog.askopenfilename(
            title="导入学生",
            filetypes=[("支持格式", "*.csv;*.xlsx;*.xls;*.json;*.txt"), ("所有文件", "*.*")]
        )

        if file_path:
            success, fail = self.student_manager.import_students(file_path)
            messagebox.showinfo("导入结果", f"成功导入 {success} 名学生，失败 {fail} 名")
            self._refresh_students()

    def _export_students(self):
        """导出学生"""
        file_path = filedialog.asksaveasfilename(
            title="导出学生",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("Excel文件", "*.xlsx"), ("JSON文件", "*.json")]
        )

        if file_path:
            if self.student_manager.export_students(file_path):
                messagebox.showinfo("成功", "导出成功")
            else:
                messagebox.showerror("错误", "导出失败")

    def _refresh_classes(self):
        """刷新班级列表"""
        for widget in self.classes_list_frame.winfo_children():
            widget.destroy()

        classes = self.class_manager.get_all_classes()

        if not classes:
            tk.Label(
                self.classes_list_frame,
                text="暂无班级，点击「添加班级」创建",
                font=("Microsoft YaHei", 12),
                bg=self.theme['background'], fg='gray'
            ).pack(pady=50)
            return

        for class_info in classes:
            card = tk.Frame(
                self.classes_list_frame,
                bg=self.theme['surface'], bd=1, relief=tk.SOLID
            )
            card.pack(fill=tk.X, pady=5, padx=5)

            # 班级图标和名称
            tk.Label(
                card, text=f"{class_info.icon} {class_info.name}",
                font=("Microsoft YaHei", 14, "bold"),
                bg=class_info.color, fg='white',
                width=20, pady=10
            ).pack(side=tk.LEFT, padx=1)

            # 班级信息
            info_frame = tk.Frame(card, bg=self.theme['surface'])
            info_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

            tk.Label(
                info_frame, text=f"年级: {class_info.grade or '未设置'} | 教师: {class_info.teacher or '未设置'}",
                font=("Microsoft YaHei", 10),
                bg=self.theme['surface']
            ).pack(anchor='w')

            tk.Label(
                info_frame, text=f"教室: {class_info.room or '未设置'} | 人数: 待统计",
                font=("Microsoft YaHei", 9),
                bg=self.theme['surface'], fg='gray'
            ).pack(anchor='w')

            # 操作按钮
            btn_frame = tk.Frame(card, bg=self.theme['surface'])
            btn_frame.pack(side=tk.RIGHT, padx=10)

            tk.Button(
                btn_frame, text="👥 管理学生",
                font=("Microsoft YaHei", 9),
                bg=self.theme['primary'], fg='white',
                relief=tk.FLAT, cursor='hand2',
                padx=10, pady=3,
                command=lambda c=class_info: self._manage_class_students(c)
            ).pack(pady=2)

            tk.Button(
                btn_frame, text="✏️ 编辑",
                font=("Microsoft YaHei", 9),
                bg=self.theme['info'], fg='white',
                relief=tk.FLAT, cursor='hand2',
                padx=10, pady=3,
                command=lambda c=class_info: self._edit_class(c)
            ).pack(pady=2)

            tk.Button(
                btn_frame, text="🗑️ 删除",
                font=("Microsoft YaHei", 9),
                bg=self.theme['danger'], fg='white',
                relief=tk.FLAT, cursor='hand2',
                padx=10, pady=3,
                command=lambda c=class_info: self._delete_class(c)
            ).pack(pady=2)

    def _add_class(self):
        """添加班级"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加班级")
        dialog.geometry("400x400")
        dialog.resizable(False, False)

        fields = ['name', 'grade', 'teacher', 'room', 'year', 'semester', 'capacity']
        labels = ['班级名称', '年级', '班主任', '教室', '学年', '学期', '容量']
        entries = {}

        for i, (field, label) in enumerate(zip(fields, labels)):
            tk.Label(dialog, text=label + ":", font=("Microsoft YaHei", 10)).grid(
                row=i, column=0, sticky='e', padx=10, pady=5
            )
            entries[field] = tk.Entry(dialog, font=("Microsoft YaHei", 10), width=25)
            entries[field].grid(row=i, column=1, columnspan=2, sticky='w', padx=10, pady=5)

        tk.Label(dialog, text="图标:", font=("Microsoft YaHei", 10)).grid(
            row=len(fields), column=0, sticky='e', padx=10, pady=5
        )
        icon_var = tk.StringVar(value="📚")
        icons = ["📚", "🏫", "🎓", "📖", "✏️", "🧮", "🔬", "🌍", "🎨", "🎵"]
        for i, icon in enumerate(icons):
            tk.Radiobutton(dialog, text=icon, variable=icon_var, value=icon).grid(
                row=len(fields), column=1, columnspan=2, sticky='w', padx=5
            )

        def save():
            class_info = ClassInfo(
                id='',
                name=entries['name'].get(),
                grade=entries['grade'].get(),
                teacher=entries['teacher'].get(),
                room=entries['room'].get(),
                year=entries['year'].get(),
                semester=entries['semester'].get(),
                capacity=int(entries['capacity'].get()) if entries['capacity'].get().isdigit() else 50,
                icon=icon_var.get()
            )

            if not class_info.name:
                messagebox.showwarning("警告", "班级名称不能为空")
                return

            if self.class_manager.add_class(class_info):
                messagebox.showinfo("成功", "班级添加成功")
                dialog.destroy()
                self._refresh_classes()
            else:
                messagebox.showerror("错误", "添加失败")

        tk.Button(
            dialog, text="保存",
            font=("Microsoft YaHei", 11),
            bg=self.theme['success'], fg='white',
            relief=tk.FLAT, cursor='hand2',
            padx=30, pady=5,
            command=save
        ).grid(row=len(fields) + 1, column=0, columnspan=3, pady=20)

    def _edit_class(self, class_info: ClassInfo):
        """编辑班级"""
        messagebox.showinfo("编辑班级", f"编辑班级: {class_info.name}")

    def _delete_class(self, class_info: ClassInfo):
        """删除班级"""
        if messagebox.askyesno("确认", f"确定要删除班级「{class_info.name}」吗？"):
            if self.class_manager.delete_class(class_info.id):
                messagebox.showinfo("成功", "班级已删除")
                self._refresh_classes()
            else:
                messagebox.showerror("错误", "删除失败")

    def _manage_class_students(self, class_info: ClassInfo):
        """管理班级学生"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"管理 {class_info.name} 的学生")
        dialog.geometry("600x500")

        tk.Label(
            dialog, text=f"班级: {class_info.name}",
            font=("Microsoft YaHei", 14, "bold")
        ).pack(pady=10)

        # 学生列表
        list_frame = tk.Frame(dialog)
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(list_frame, font=("Microsoft YaHei", 10), yscrollcommand=scrollbar.set)
        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # 添加学生按钮
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)

        all_students = self.student_manager.get_all_students()
        current_student_ids = set(self.class_manager.get_class_students(class_info.id))

        available_students = [s for s in all_students if s.id not in current_student_ids]

        for student in available_students:
            listbox.insert(tk.END, f"{student.number} - {student.name}")

        def add_selected():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                student = available_students[index]
                self.class_manager.add_student_to_class(class_info.id, student.id)
                listbox.delete(index)
                messagebox.showinfo("成功", f"已添加 {student.name}")

        tk.Button(
            btn_frame, text="➕ 添加选中",
            font=("Microsoft YaHei", 10),
            bg=self.theme['success'], fg='white',
            relief=tk.FLAT, cursor='hand2',
            padx=15, pady=5,
            command=add_selected
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="关闭",
            font=("Microsoft YaHei", 10),
            bg='gray', fg='white',
            relief=tk.FLAT, cursor='hand2',
            padx=15, pady=5,
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

    def _import_classes(self):
        """导入班级"""
        file_path = filedialog.askopenfilename(
            title="导入班级",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )

        if file_path:
            success, fail = self.import_export_manager.import_data(file_path, 'classes')
            messagebox.showinfo("导入结果", f"成功导入 {success} 个班级，失败 {fail} 个")
            self._refresh_classes()

    def _export_classes(self):
        """导出班级"""
        file_path = filedialog.asksaveasfilename(
            title="导出班级",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json")]
        )

        if file_path:
            if self.import_export_manager.export_data(file_path, 'classes'):
                messagebox.showinfo("成功", "导出成功")
            else:
                messagebox.showerror("错误", "导出失败")

    def _refresh_attendance(self):
        """刷新考勤页面"""
        if not self.current_class_id:
            return

        today = datetime.now().strftime("%Y-%m-%d")
        stats = self.attendance_manager.get_attendance_statistics(self.current_class_id)

        self.attendance_stats_labels['total'].config(text=str(stats['total']))
        self.attendance_stats_labels['present'].config(text=str(stats['present']))
        self.attendance_stats_labels['absent'].config(text=str(stats['absent']))
        self.attendance_stats_labels['late'].config(text=str(stats['late']))
        self.attendance_stats_labels['leave'].config(text=str(stats['leave']))

    def _quick_attendance(self):
        """快速考勤"""
        if not self.current_class_id or not self.students:
            messagebox.showwarning("警告", "请先选择一个班级")
            return

        today = datetime.now().strftime("%Y-%m-%d")

        for student in self.students:
            record = AttendanceRecord(
                id='',
                student_id=student.id,
                student_name=student.name,
                class_id=self.current_class_id,
                date=today,
                status=AttendanceStatus.PRESENT.value,
                check_in_time=datetime.now().strftime("%H:%M:%S")
            )
            self.attendance_manager.add_attendance(record)

        messagebox.showinfo("成功", "考勤完成")
        self._refresh_attendance()

    def _show_attendance_report(self):
        """显示考勤报表"""
        messagebox.showinfo("考勤报表", "报表功能开发中...")

    def _export_attendance(self):
        """导出考勤"""
        if not self.current_class_id:
            messagebox.showwarning("警告", "请先选择一个班级")
            return

        file_path = filedialog.asksaveasfilename(
            title="导出考勤报表",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("CSV文件", "*.csv")]
        )

        if file_path:
            today = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            if self.attendance_manager.export_attendance_report(
                self.current_class_id, start_date, today, file_path
            ):
                messagebox.showinfo("成功", "导出成功")
            else:
                messagebox.showerror("错误", "导出失败")

    def _refresh_statistics(self):
        """刷新统计页面"""
        students = self.student_manager.get_all_students()
        classes = self.class_manager.get_all_classes()
        draw_stats = self.draw_record_manager.get_statistics()
        attendance_stats = self.attendance_manager.get_attendance_statistics()

        self.stats_cards['students'].config(text=str(len(students)))
        self.stats_cards['classes'].config(text=str(len(classes)))
        self.stats_cards['draws'].config(text=str(draw_stats.get('total_records', 0)))
        self.stats_cards['attendance'].config(text=str(attendance_stats.get('total', 0)))

        # 刷新排行榜
        self.leaderboard_listbox.delete(0, tk.END)
        leaderboard = self.reward_manager.get_leaderboard(limit=10)

        for i, item in enumerate(leaderboard, 1):
            name = item.get('name', '未知')
            points = item.get('points', 0)
            stars = item.get('stars', 0)
            self.leaderboard_listbox.insert(tk.END, f"{i}. {name} - {points}分 ⭐{stars}")

    def _refresh_history(self):
        """刷新历史记录"""
        self.history_listbox.delete(0, tk.END)

        records = self.draw_record_manager.get_history(
            class_id=self.current_class_id,
            limit=100
        )

        for record in records:
            winners_text = "、".join([w.get('name', '') if isinstance(w, dict) else str(w) for w in record.winners])
            mode_name = DrawMode(record.mode).name if hasattr(DrawMode, record.mode) else str(record.mode)
            self.history_listbox.insert(
                tk.END,
                f"[{record.date} {record.time}] {mode_name}: {winners_text} ({record.draw_count}人)"
            )

    def _change_theme(self):
        """更改主题"""
        theme_name = self.theme_var.get()
        self.config.set('theme', theme_name)
        self.theme = THEMES.get(theme_name, THEMES['默认蓝色'])

        # 更新UI
        messagebox.showinfo("提示", "主题已更改，部分效果可能需要重启程序")

    def _change_language(self):
        """更改语言"""
        lang = self.lang_var.get()
        self.config.set('language', lang)
        messagebox.showinfo("提示", "语言设置已保存")

    def _save_sound_settings(self):
        """保存声音设置"""
        self.config.set('sound_enabled', self.sound_enabled_var.get())
        self.config.set('voice_enabled', self.voice_enabled_var.get())

    def _create_backup(self):
        """创建备份"""
        backup_path = self.backup_manager.create_backup()

        if backup_path:
            messagebox.showinfo("成功", f"备份已创建:\n{backup_path}")
        else:
            messagebox.showerror("错误", "备份创建失败")

    def _restore_backup(self):
        """恢复备份"""
        backups = self.backup_manager.list_backups()

        if not backups:
            messagebox.showinfo("提示", "暂无备份")
            return

        backup_names = [f"{b['name']} ({b['created']})" for b in backups]
        backup_path = backups[0]['path']

        if messagebox.askyesno("确认", f"确定要恢复备份吗？\n{backups[0]['name']}"):
            if self.backup_manager.restore_backup(backup_path):
                messagebox.showinfo("成功", "恢复成功，请重启程序")
            else:
                messagebox.showerror("错误", "恢复失败")

    def _check_for_updates(self):
        """检查更新"""
        pass

    def _auto_backup(self):
        """自动备份"""
        interval = self.config.get('backup_interval', 24) * 3600  # 转换为秒

        while True:
            time.sleep(interval)
            self.backup_manager.create_backup()

    def _set_status(self, message: str):
        """设置状态栏消息"""
        self.status_label.config(text=message)


# ==========================================
# 主程序入口
# ==========================================
def main():
    """主程序入口"""
    try:
        root = tk.Tk()
        app = SmartPickerProApp(root)
        root.mainloop()
    except Exception as e:
        print(f"[致命错误] 程序启动失败: {e}")
        import traceback
        traceback.print_exc()

        try:
            messagebox.showerror(
                "启动失败",
                f"程序启动失败，请检查控制台输出。\n错误信息: {str(e)[:200]}..."
            )
        except:
            pass


if __name__ == "__main__":
    main()



# ==========================================
# 高级功能模块
# ==========================================

# ==========================================
# 预约点名系统
# ==========================================
class ScheduledAttendanceManager:
    """预约点名管理器"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self._create_table()

    def _create_table(self):
        """创建预约表"""
        sql = """
        CREATE TABLE IF NOT EXISTS scheduled_attendance (
            id TEXT PRIMARY KEY,
            class_id TEXT,
            student_id TEXT,
            scheduled_date TEXT,
            scheduled_time TEXT,
            status INTEGER DEFAULT 0,
            note TEXT,
            created_at TEXT
        )
        """
        self.db.execute(sql)
        self.db.commit()

    def add_scheduled(self, class_id: str, student_id: str, date: str, time: str, note: str = "") -> bool:
        """添加预约"""
        data = {
            'id': generate_unique_id(),
            'class_id': class_id,
            'student_id': student_id,
            'scheduled_date': date,
            'scheduled_time': time,
            'status': 0,
            'note': note,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return self.db.insert('scheduled_attendance', data)

    def get_scheduled_list(self, class_id: str, date: str) -> List[Dict]:
        """获取预约列表"""
        rows = self.db.fetchall(
            'SELECT * FROM scheduled_attendance WHERE class_id = ? AND scheduled_date = ? ORDER BY scheduled_time',
            (class_id, date)
        )
        return [dict(row) for row in rows]

    def update_status(self, schedule_id: str, status: int) -> bool:
        """更新状态"""
        return self.db.update('schedended_attendance', {'status': status}, 'id = ?', (schedule_id,))

    def delete_scheduled(self, schedule_id: str) -> bool:
        """删除预约"""
        return self.db.delete('scheduled_attendance', 'id = ?', (schedule_id,))


# ==========================================
# 分组系统
# ==========================================
class GroupManager:
    """分组管理器"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self._create_table()

    def _create_table(self):
        """创建分组表"""
        sql = """
        CREATE TABLE IF NOT EXISTS groups (
            id TEXT PRIMARY KEY,
            class_id TEXT,
            name TEXT,
            description TEXT,
            created_at TEXT
        )
        """
        self.db.execute(sql)

        sql2 = """
        CREATE TABLE IF NOT EXISTS group_members (
            group_id TEXT,
            student_id TEXT,
            PRIMARY KEY (group_id, student_id)
        )
        """
        self.db.execute(sql2)
        self.db.commit()

    def create_group(self, class_id: str, name: str, description: str = "") -> str:
        """创建分组"""
        group_id = generate_unique_id()
        data = {
            'id': group_id,
            'class_id': class_id,
            'name': name,
            'description': description,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.db.insert('groups', data)
        return group_id

    def add_member(self, group_id: str, student_id: str) -> bool:
        """添加成员"""
        data = {'group_id': group_id, 'student_id': student_id}
        try:
            self.db.execute(
                "INSERT OR IGNORE INTO group_members (group_id, student_id) VALUES (?, ?)",
                (group_id, student_id)
            )
            self.db.commit()
            return True
        except:
            return False

    def remove_member(self, group_id: str, student_id: str) -> bool:
        """移除成员"""
        return self.db.delete('group_members', 'group_id = ? AND student_id = ?', (group_id, student_id))

    def get_group_members(self, group_id: str) -> List[str]:
        """获取组成员"""
        rows = self.db.fetchall(
            'SELECT student_id FROM group_members WHERE group_id = ?',
            (group_id,)
        )
        return [row['student_id'] for row in rows]

    def random_group(self, class_id: str, group_count: int) -> List[List[str]]:
        """随机分组"""
        student_ids = self.db.fetchall(
            'SELECT student_id FROM class_students WHERE class_id = ?',
            (class_id,)
        )
        student_ids = [row['student_id'] for row in student_ids]
        random.shuffle(student_ids)

        groups = [[] for _ in range(group_count)]
        for i, sid in enumerate(student_ids):
            groups[i % group_count].append(sid)

        return groups

    def delete_group(self, group_id: str) -> bool:
        """删除分组"""
        self.db.delete('group_members', 'group_id = ?', (group_id,))
        return self.db.delete('groups', 'id = ?', (group_id,))


# ==========================================
# 座位管理系统
# ==========================================
class SeatManager:
    """座位管理器"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self._create_table()

    def _create_table(self):
        """创建座位表"""
        sql = """
        CREATE TABLE IF NOT EXISTS seats (
            id TEXT PRIMARY KEY,
            class_id TEXT,
            student_id TEXT,
            row INTEGER,
            col INTEGER,
            updated_at TEXT
        )
        """
        self.db.execute(sql)
        self.db.commit()

    def set_seat(self, class_id: str, student_id: str, row: int, col: int) -> bool:
        """设置座位"""
        # 清除该学生原有座位
        self.db.delete('seats', 'student_id = ?', (student_id,))

        # 清除该座位原有学生
        self.db.delete('seats', 'class_id = ? AND row = ? AND col = ?', (class_id, row, col))

        # 设置新座位
        data = {
            'id': generate_unique_id(),
            'class_id': class_id,
            'student_id': student_id,
            'row': row,
            'col': col,
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return self.db.insert('seats', data)

    def get_seat_map(self, class_id: str) -> Dict[Tuple[int, int], str]:
        """获取座位图"""
        rows = self.db.fetchall(
            'SELECT row, col, student_id FROM seats WHERE class_id = ?',
            (class_id,)
        )
        seat_map = {}
        for row in rows:
            seat_map[(row['row'], row['col'])] = row['student_id']
        return seat_map

    def clear_seats(self, class_id: str) -> bool:
        """清空座位"""
        return self.db.delete('seats', 'class_id = ?', (class_id,))

    def get_student_seat(self, student_id: str) -> Optional[Tuple[int, int]]:
        """获取学生座位"""
        row = self.db.fetchone(
            'SELECT row, col FROM seats WHERE student_id = ?',
            (student_id,)
        )
        if row:
            return (row['row'], row['col'])
        return None


# ==========================================
# 通知系统
# ==========================================
class NotificationManager:
    """通知管理器"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self._create_table()

    def _create_table(self):
        """创建通知表"""
        sql = """
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            title TEXT,
            content TEXT,
            type INTEGER,
            target TEXT,
            status INTEGER DEFAULT 0,
            created_at TEXT,
            read_at TEXT
        )
        """
        self.db.execute(sql)
        self.db.commit()

    def send_notification(self, title: str, content: str, notification_type: int = 1, target: str = "all") -> bool:
        """发送通知"""
        data = {
            'id': generate_unique_id(),
            'title': title,
            'content': content,
            'type': notification_type,
            'target': target,
            'status': 0,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return self.db.insert('notifications', data)

    def get_notifications(self, limit: int = 20) -> List[Dict]:
        """获取通知列表"""
        rows = self.db.fetchall(
            'SELECT * FROM notifications ORDER BY created_at DESC LIMIT ?',
            (limit,)
        )
        return [dict(row) for row in rows]

    def mark_as_read(self, notification_id: str) -> bool:
        """标记为已读"""
        return self.db.update(
            'notifications',
            {'status': 1, 'read_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            'id = ?',
            (notification_id,)
        )


# ==========================================
# 日志系统
# ==========================================
class LogManager:
    """日志管理器"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.log_dir = os.path.join(BASE_DIR, "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self._create_table()

    def _create_table(self):
        """创建日志表"""
        sql = """
        CREATE TABLE IF NOT EXISTS logs (
            id TEXT PRIMARY KEY,
            level TEXT,
            module TEXT,
            message TEXT,
            details TEXT,
            created_at TEXT
        )
        """
        self.db.execute(sql)
        self.db.commit()

    def log(self, level: str, module: str, message: str, details: str = ""):
        """记录日志"""
        data = {
            'id': generate_unique_id(),
            'level': level,
            'module': module,
            'message': message,
            'details': details,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.db.insert('logs', data)

        # 同时写入文件
        self._write_to_file(level, module, message, details)

    def _write_to_file(self, level: str, module: str, message: str, details: str):
        """写入日志文件"""
        log_file = os.path.join(self.log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [{module}] {message}"

        if details:
            log_entry += f"\n  Details: {details}"

        log_entry += "\n"

        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except:
            pass

    def get_logs(self, level: str = None, module: str = None, limit: int = 100) -> List[Dict]:
        """获取日志列表"""
        conditions = []
        params = []

        if level:
            conditions.append("level = ?")
            params.append(level)
        if module:
            conditions.append("module = ?")
            params.append(module)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM logs WHERE {where_clause} ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        rows = self.db.fetchall(sql, tuple(params))
        return [dict(row) for row in rows]


# ==========================================
# 插件系统
# ==========================================
class PluginManager:
    """插件管理器"""

    def __init__(self):
        self.plugin_dir = os.path.join(BASE_DIR, "plugins")
        os.makedirs(self.plugin_dir, exist_ok=True)
        self.plugins = {}
        self._load_plugins()

    def _load_plugins(self):
        """加载插件"""
        if not os.path.exists(self.plugin_dir):
            return

        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                plugin_name = filename[:-3]
                try:
                    module_name = f"plugins.{plugin_name}"
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        module_name,
                        os.path.join(self.plugin_dir, filename)
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        if hasattr(module, 'Plugin'):
                            plugin = module.Plugin()
                            self.plugins[plugin_name] = plugin
                            print(f"[插件] 已加载: {plugin_name}")
                except Exception as e:
                    print(f"[错误] 插件加载失败 {filename}: {e}")

    def get_plugin(self, name: str):
        """获取插件"""
        return self.plugins.get(name)

    def list_plugins(self) -> List[str]:
        """列出所有插件"""
        return list(self.plugins.keys())


# ==========================================
# 主题管理器
# ==========================================
class ThemeManager:
    """主题管理器"""

    def __init__(self):
        self.themes = THEMES
        self.current_theme = '默认蓝色'

    def set_theme(self, theme_name: str):
        """设置主题"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return self.themes[theme_name]
        return self.themes['默认蓝色']

    def get_theme(self, theme_name: str = None) -> Dict:
        """获取主题配置"""
        name = theme_name or self.current_theme
        return self.themes.get(name, self.themes['默认蓝色'])

    def list_themes(self) -> List[str]:
        """列出所有主题"""
        return list(self.themes.keys())

    def create_custom_theme(self, name: str, primary: str, secondary: str,
                          accent: str, background: str, text: str) -> bool:
        """创建自定义主题"""
        if name in self.themes:
            return False

        self.themes[name] = {
            'primary': primary,
            'secondary': secondary,
            'accent': accent,
            'background': background,
            'surface': background,
            'text': text,
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'info': '#00bcd4'
        }
        return True

    def delete_custom_theme(self, name: str) -> bool:
        """删除自定义主题"""
        if name in ['默认蓝色', '暗夜模式', '森林绿', '商务灰']:
            return False

        if name in self.themes:
            del self.themes[name]
            return True
        return False


# ==========================================
# 国际化管理器
# ==========================================
class I18nManager:
    """国际化管理器"""

    def __init__(self, language: str = '简体中文'):
        self.current_language = language
        self.translations = LANGUAGE_PACKS
        self._add_custom_translations()

    def _add_custom_translations(self):
        """添加自定义翻译"""
        # 日语
        self.translations['日本語'] = {
            'app_title': 'スマート教室点名システム',
            'start': 'スタート',
            'stop': 'ストップ',
            'reset': 'リセット',
            'settings': '設定',
            'class_manager': 'クラス管理',
            'student_manager': '学生管理',
            'statistics': '統計',
            'attendance': '出席',
            'history': '履歴',
            'export': 'エクスポート',
            'import': 'インポート',
            'about': '情報',
            'help': 'ヘルプ',
            'exit': '終了',
            'save': '保存',
            'cancel': 'キャンセル',
            'confirm': '確認',
            'delete': '削除',
            'edit': '編集',
            'add': '追加',
            'search': '検索',
            'filter': 'フィルター',
            'refresh': '更新',
            'total': '合計',
            'present': '出席',
            'absent': '欠席',
            'late': '遅刻',
            'leave': '请假',
            'name': '名前',
            'number': '番号',
            'gender': '性別',
            'phone': '電話',
            'email': 'メール',
            'address': '住所',
            'birthday': '誕生日',
            'parent': '保護者',
            'note': 'メモ',
            'grade': '学年',
            'class_name': 'クラス',
            'seat': '座席',
            'draw_count': '点名人数',
            'draw_mode': '点名モード',
            'history_count': '履歴数',
            'success_rate': '出席率',
            'points': 'ポイント',
            'level': 'レベル',
            'stars': '星',
            'badges': 'バッジ',
            'rewards': '報酬',
            'punishments': '罰則',
            'no_students': '学生なし',
            'no_records': '記録なし',
            'load_success': 'ロード成功',
            'save_success': '保存成功',
            'delete_success': '削除成功',
            'import_success': 'インポート成功',
            'export_success': 'エクスポート成功',
            'error': 'エラー',
            'warning': '警告',
            'info': '情報',
            'confirm_delete': '削除しますか？',
            'confirm_reset': 'リセットしますか？',
            'file_not_found': 'ファイルが見つかりません',
            'invalid_format': '無効な形式',
            'network_error': 'ネットワークエラー',
            'unknown_error': '不明なエラー',
        }

        # 韩语
        self.translations['한국어'] = {
            'app_title': '스마트 교실 점명 시스템',
            'start': '시작',
            'stop': '중지',
            'reset': '초기화',
            'settings': '설정',
            'class_manager': '반 관리',
            'student_manager': '학생 관리',
            'statistics': '통계',
            'attendance': '출석',
            'history': '기록',
            'export': '내보내기',
            'import': '가져오기',
            'about': '정보',
            'help': '도움말',
            'exit': '종료',
            'save': '저장',
            'cancel': '취소',
            'confirm': '확인',
            'delete': '삭제',
            'edit': '편집',
            'add': '추가',
            'search': '검색',
            'filter': '필터',
            'refresh': '새로고침',
            'total': '총계',
            'present': '출석',
            'absent': '결석',
            'late': '지각',
            'leave': '휴가',
            'name': '이름',
            'number': '번호',
            'gender': '성별',
            'phone': '전화',
            'email': '이메일',
            'address': '주소',
            'birthday': '생일',
            'parent': '학부모',
            'note': '메모',
            'grade': '학년',
            'class_name': '반',
            'seat': '자리',
            'draw_count': '점명 인원',
            'draw_mode': '점명 모드',
            'history_count': '기록 수',
            'success_rate': '출석률',
            'points': '포인트',
            'level': '레벨',
            'stars': '별',
            'badges': '배지',
            'rewards': '보상',
            'punishments': '처벌',
            'no_students': '학생 없음',
            'no_records': '기록 없음',
            'load_success': '로드 성공',
            'save_success': '저장 성공',
            'delete_success': '삭제 성공',
            'import_success': '가져오기 성공',
            'export_success': '내보내기 성공',
            'error': '오류',
            'warning': '경고',
            'info': '정보',
            'confirm_delete': '삭제하시겠습니까?',
            'confirm_reset': '초기화하시겠습니까?',
            'file_not_found': '파일을 찾을 수 없습니다',
            'invalid_format': '잘못된 형식',
            'network_error': '네트워크 오류',
            'unknown_error': '알 수 없는 오류',
        }

    def get_text(self, key: str, default: str = None) -> str:
        """获取翻译文本"""
        translations = self.translations.get(self.current_language, self.translations['简体中文'])
        return translations.get(key, default or key)

    def set_language(self, language: str):
        """设置语言"""
        if language in self.translations:
            self.current_language = language

    def list_languages(self) -> List[str]:
        """列出支持的语言"""
        return list(self.translations.keys())


# ==========================================
# 数据验证器
# ==========================================
class Validator:
    """数据验证器"""

    @staticmethod
    def validate_student_number(number: str) -> Tuple[bool, str]:
        """验证学号"""
        if not number:
            return False, "学号不能为空"
        if len(number) < 2:
            return False, "学号长度不能少于2位"
        if len(number) > 20:
            return False, "学号长度不能超过20位"
        return True, ""

    @staticmethod
    def validate_student_name(name: str) -> Tuple[bool, str]:
        """验证学生姓名"""
        if not name:
            return False, "姓名不能为空"
        if len(name) < 2:
            return False, "姓名长度不能少于2个字符"
        if len(name) > 20:
            return False, "姓名长度不能超过20个字符"
        return True, ""

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """验证手机号"""
        if not phone:
            return True, ""  # 电话可选

        pattern = r'^1[3-9]\d{9}$'
        if not re.match(pattern, phone):
            return False, "手机号格式不正确"
        return True, ""

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """验证邮箱"""
        if not email:
            return True, ""  # 邮箱可选

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "邮箱格式不正确"
        return True, ""

    @staticmethod
    def validate_date(date_str: str) -> Tuple[bool, str]:
        """验证日期"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True, ""
        except:
            return False, "日期格式不正确，应为 YYYY-MM-DD"

    @staticmethod
    def validate_time(time_str: str) -> Tuple[bool, str]:
        """验证时间"""
        try:
            datetime.strptime(time_str, '%H:%M:%S')
            return True, ""
        except:
            try:
                datetime.strptime(time_str, '%H:%M')
                return True, ""
            except:
                return False, "时间格式不正确，应为 HH:MM 或 HH:MM:SS"

    @staticmethod
    def validate_class_name(name: str) -> Tuple[bool, str]:
        """验证班级名称"""
        if not name:
            return False, "班级名称不能为空"
        if len(name) > 50:
            return False, "班级名称长度不能超过50个字符"
        return True, ""


# ==========================================
# 加密工具
# ==========================================
class CryptoUtils:
    """加密工具"""

    @staticmethod
    def md5(text: str) -> str:
        """MD5加密"""
        return hashlib.md5(text.encode()).hexdigest()

    @staticmethod
    def sha256(text: str) -> str:
        """SHA256加密"""
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def base64_encode(text: str) -> str:
        """Base64编码"""
        return base64.b64encode(text.encode()).decode()

    @staticmethod
    def base64_decode(encoded: str) -> str:
        """Base64解码"""
        return base64.b64decode(encoded.encode()).decode()

    @staticmethod
    def encrypt_data(data: str, key: str) -> str:
        """简单数据加密"""
        encrypted = []
        for i, char in enumerate(data):
            encrypted.append(chr(ord(char) ^ ord(key[i % len(key)])))
        return base64.b64encode(''.join(encrypted).encode()).decode()

    @staticmethod
    def decrypt_data(encrypted: str, key: str) -> str:
        """简单数据解密"""
        try:
            decoded = base64.b64decode(encrypted.encode()).decode()
            decrypted = []
            for i, char in enumerate(decoded):
                decrypted.append(chr(ord(char) ^ ord(key[i % len(key)])))
            return ''.join(decrypted)
        except:
            return ""


# ==========================================
# 文件处理工具
# ==========================================
class FileUtils:
    """文件处理工具"""

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小（字节）"""
        try:
            return os.path.getsize(file_path)
        except:
            return 0

    @staticmethod
    def format_size(size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """获取文件扩展名"""
        return os.path.splitext(file_path)[1].lower()

    @staticmethod
    def is_image_file(file_path: str) -> bool:
        """判断是否为图片文件"""
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.ico'}
        return FileUtils.get_file_extension(file_path) in image_exts

    @staticmethod
    def is_audio_file(file_path: str) -> bool:
        """判断是否为音频文件"""
        audio_exts = {'.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a'}
        return FileUtils.get_file_extension(file_path) in audio_exts

    @staticmethod
    def is_video_file(file_path: str) -> bool:
        """判断是否为视频文件"""
        video_exts = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
        return FileUtils.get_file_extension(file_path) in video_exts

    @staticmethod
    def copy_file(source: str, destination: str) -> bool:
        """复制文件"""
        try:
            import shutil
            shutil.copy2(source, destination)
            return True
        except:
            return False

    @staticmethod
    def move_file(source: str, destination: str) -> bool:
        """移动文件"""
        try:
            import shutil
            shutil.move(source, destination)
            return True
        except:
            return False

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except:
            return False

    @staticmethod
    def create_directory(dir_path: str) -> bool:
        """创建目录"""
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except:
            return False

    @staticmethod
    def list_files(dir_path: str, pattern: str = "*") -> List[str]:
        """列出目录下的文件"""
        try:
            import glob
            return glob.glob(os.path.join(dir_path, pattern))
        except:
            return []


# ==========================================
# 日期时间工具
# ==========================================
class DateTimeUtils:
    """日期时间工具"""

    @staticmethod
    def get_current_date() -> str:
        """获取当前日期"""
        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def get_current_time() -> str:
        """获取当前时间"""
        return datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def get_current_datetime() -> str:
        """获取当前日期时间"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_today_weekday() -> str:
        """获取今天是星期几"""
        weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        return weekdays[datetime.now().weekday()]

    @staticmethod
    def get_month_start(date_str: str = None) -> str:
        """获取月份开始日期"""
        if date_str:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            dt = datetime.now()
        return dt.replace(day=1).strftime("%Y-%m-%d")

    @staticmethod
    def get_month_end(date_str: str = None) -> str:
        """获取月份结束日期"""
        if date_str:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            dt = datetime.now()
        next_month = dt.replace(day=28) + timedelta(days=4)
        return (next_month - timedelta(days=next_month.day)).strftime("%Y-%m-%d")

    @staticmethod
    def add_days(date_str: str, days: int) -> str:
        """日期加减天数"""
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        new_dt = dt + timedelta(days=days)
        return new_dt.strftime("%Y-%m-%d")

    @staticmethod
    def add_months(date_str: str, months: int) -> str:
        """日期加减月数"""
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        month = dt.month - 1 + months
        year = dt.year + month // 12
        month = month % 12 + 1
        day = min(dt.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return datetime(year, month, day).strftime("%Y-%m-%d")

    @staticmethod
    def get_days_between(start_date: str, end_date: str) -> int:
        """获取两个日期之间的天数"""
        dt1 = datetime.strptime(start_date, '%Y-%m-%d')
        dt2 = datetime.strptime(end_date, '%Y-%m-%d')
        return abs((dt2 - dt1).days)

    @staticmethod
    def is_weekend(date_str: str) -> bool:
        """判断是否为周末"""
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.weekday() >= 5

    @staticmethod
    def is_same_day(date1: str, date2: str) -> bool:
        """判断是否为同一天"""
        return date1.split(' ')[0] == date2.split(' ')[0]

    @staticmethod
    def get_timestamp() -> int:
        """获取时间戳"""
        return int(time.time())

    @staticmethod
    def from_timestamp(timestamp: int) -> str:
        """从时间戳获取日期时间"""
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


# ==========================================
# 字符串工具
# ==========================================
class StringUtils:
    """字符串工具"""

    @staticmethod
    def truncate(text: str, length: int, suffix: str = "...") -> str:
        """截断字符串"""
        if len(text) <= length:
            return text
        return text[:length - len(suffix)] + suffix

    @staticmethod
    def capitalize(text: str) -> str:
        """首字母大写"""
        return text.capitalize()

    @staticmethod
    def remove_special_chars(text: str) -> str:
        """移除特殊字符"""
        return re.sub(r'[^\w\s]', '', text)

    @staticmethod
    def remove_whitespace(text: str) -> str:
        """移除空白字符"""
        return re.sub(r'\s+', '', text)

    @staticmethod
    def pad_left(text: str, length: int, char: str = " ") -> str:
        """左填充"""
        return text.rjust(length, char)

    @staticmethod
    def pad_right(text: str, length: int, char: str = " ") -> str:
        """右填充"""
        return text.ljust(length, char)

    @staticmethod
    def contains(text: str, keyword: str, case_sensitive: bool = True) -> bool:
        """判断是否包含关键词"""
        if not case_sensitive:
            text = text.lower()
            keyword = keyword.lower()
        return keyword in text

    @staticmethod
    def starts_with(text: str, prefix: str) -> bool:
        """判断是否以指定字符串开头"""
        return text.startswith(prefix)

    @staticmethod
    def ends_with(text: str, suffix: str) -> bool:
        """判断是否以指定字符串结尾"""
        return text.endswith(suffix)

    @staticmethod
    def to_pinyin(text: str) -> str:
        """转拼音（简单实现）"""
        # 简化实现，实际需要拼音库
        return text

    @staticmethod
    def mask_phone(phone: str) -> str:
        """手机号脱敏"""
        if len(phone) == 11:
            return phone[:3] + '****' + phone[7:]
        return phone

    @staticmethod
    def mask_email(email: str) -> str:
        """邮箱脱敏"""
        if '@' in email:
            name, domain = email.split('@')
            if len(name) > 2:
                return name[0] + '*' * (len(name) - 2) + name[-1] + '@' + domain
            return name + '@' + domain
        return email


# ==========================================
# 列表工具
# ==========================================
class ListUtils:
    """列表工具"""

    @staticmethod
    def chunk(lst: List, size: int) -> List[List]:
        """将列表分块"""
        return [lst[i:i + size] for i in range(0, len(lst), size)]

    @staticmethod
    def deduplicate(lst: List) -> List:
        """去重"""
        seen = set()
        result = []
        for item in lst:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    @staticmethod
    def flatten(nested_list: List) -> List:
        """展平嵌套列表"""
        result = []
        for item in nested_list:
            if isinstance(item, list):
                result.extend(ListUtils.flatten(item))
            else:
                result.append(item)
        return result

    @staticmethod
    def group_by(lst: List, key: str) -> Dict:
        """按键分组"""
        result = defaultdict(list)
        for item in lst:
            if isinstance(item, dict):
                result[item.get(key, 'other')].append(item)
        return dict(result)

    @staticmethod
    def sort_by(lst: List, key: str, reverse: bool = False) -> List:
        """按键排序"""
        return sorted(lst, key=lambda x: x.get(key, '') if isinstance(x, dict) else getattr(x, key, ''), reverse=reverse)

    @staticmethod
    def filter_by(lst: List, key: str, value) -> List:
        """按键值过滤"""
        return [item for item in lst if (isinstance(item, dict) and item.get(key) == value) or (hasattr(item, key) and getattr(item, key) == value)]

    @staticmethod
    def find(lst: List, predicate) -> Optional:
        """查找满足条件的第一个元素"""
        for item in lst:
            if predicate(item):
                return item
        return None

    @staticmethod
    def intersection(list1: List, list2: List) -> List:
        """获取两个列表的交集"""
        return list(set(list1) & set(list2))

    @staticmethod
    def union(list1: List, list2: List) -> List:
        """获取两个列表的并集"""
        return list(set(list1) | set(list2))

    @staticmethod
    def difference(list1: List, list2: List) -> List:
        """获取两个列表的差集"""
        return list(set(list1) - set(list2))


# ==========================================
# 数学工具
# ==========================================
class MathUtils:
    """数学工具"""

    @staticmethod
    def average(numbers: List[float]) -> float:
        """计算平均值"""
        if not numbers:
            return 0.0
        return sum(numbers) / len(numbers)

    @staticmethod
    def median(numbers: List[float]) -> float:
        """计算中位数"""
        if not numbers:
            return 0.0
        sorted_numbers = sorted(numbers)
        n = len(sorted_numbers)
        if n % 2 == 0:
            return (sorted_numbers[n // 2 - 1] + sorted_numbers[n // 2]) / 2
        else:
            return sorted_numbers[n // 2]

    @staticmethod
    def mode(numbers: List) -> List:
        """计算众数"""
        if not numbers:
            return []
        counter = Counter(numbers)
        max_count = max(counter.values())
        return [num for num, count in counter.items() if count == max_count]

    @staticmethod
    def standard_deviation(numbers: List[float]) -> float:
        """计算标准差"""
        if not numbers:
            return 0.0
        avg = MathUtils.average(numbers)
        variance = sum((x - avg) ** 2 for x in numbers) / len(numbers)
        return variance ** 0.5

    @staticmethod
    def variance(numbers: List[float]) -> float:
        """计算方差"""
        if not numbers:
            return 0.0
        avg = MathUtils.average(numbers)
        return sum((x - avg) ** 2 for x in numbers) / len(numbers)

    @staticmethod
    def percentile(numbers: List[float], percent: float) -> float:
        """计算百分位数"""
        if not numbers:
            return 0.0
        sorted_numbers = sorted(numbers)
        index = (len(sorted_numbers) - 1) * percent / 100
        floor_index = int(index)
        ceil_index = min(floor_index + 1, len(sorted_numbers) - 1)
        weight = index - floor_index
        return sorted_numbers[floor_index] * (1 - weight) + sorted_numbers[ceil_index] * weight

    @staticmethod
    def normalize(numbers: List[float]) -> List[float]:
        """归一化"""
        if not numbers:
            return []
        min_val = min(numbers)
        max_val = max(numbers)
        if max_val == min_val:
            return [0.5] * len(numbers)
        return [(x - min_val) / (max_val - min_val) for x in numbers]

    @staticmethod
    def clamp(value: float, min_value: float, max_value: float) -> float:
        """限制值在范围内"""
        return max(min_value, min(max_value, value))

    @staticmethod
    def round_half_up(value: float, decimals: int = 0) -> float:
        """四舍五入"""
        multiplier = 10 ** decimals
        return int(value * multiplier + 0.5) / multiplier if decimals > 0 else int(value + 0.5)


# ==========================================
# 图表生成工具
# ==========================================
class ChartGenerator:
    """图表生成工具"""

    def __init__(self):
        self.charts_dir = os.path.join(EXPORT_DIR, "charts")
        os.makedirs(self.charts_dir, exist_ok=True)

    def generate_pie_chart(self, data: Dict[str, int], title: str = "", filename: str = None) -> Optional[str]:
        """生成饼图"""
        if not MATPLOTLIB_AVAILABLE:
            return None

        try:
            fig, ax = plt.subplots(figsize=(8, 8))

            labels = list(data.keys())
            sizes = list(data.values())
            colors = plt.cm.Set3(range(len(labels)))

            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)

            if title:
                ax.set_title(title, fontsize=16, fontweight='bold')

            plt.tight_layout()

            if not filename:
                filename = f"pie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            filepath = os.path.join(self.charts_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()

            return filepath
        except Exception as e:
            print(f"[错误] 饼图生成失败: {e}")
            return None

    def generate_bar_chart(self, data: Dict[str, int], title: str = "", filename: str = None) -> Optional[str]:
        """生成柱状图"""
        if not MATPLOTLIB_AVAILABLE:
            return None

        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            labels = list(data.keys())
            values = list(data.values())

            ax.bar(labels, values, color='skyblue', edgecolor='navy')

            ax.set_xlabel('')
            ax.set_ylabel('数量')
            if title:
                ax.set_title(title, fontsize=16, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)

            plt.tight_layout()

            if not filename:
                filename = f"bar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            filepath = os.path.join(self.charts_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()

            return filepath
        except Exception as e:
            print(f"[错误] 柱状图生成失败: {e}")
            return None

    def generate_line_chart(self, data: Dict[str, List], title: str = "", filename: str = None) -> Optional[str]:
        """生成折线图"""
        if not MATPLOTLIB_AVAILABLE:
            return None

        try:
            fig, ax = plt.subplots(figsize=(12, 6))

            for label, values in data.items():
                ax.plot(range(len(values)), values, marker='o', label=label, linewidth=2)

            ax.set_xlabel('时间')
            ax.set_ylabel('值')
            if title:
                ax.set_title(title, fontsize=16, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)

            plt.tight_layout()

            if not filename:
                filename = f"line_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            filepath = os.path.join(self.charts_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()

            return filepath
        except Exception as e:
            print(f"[错误] 折线图生成失败: {e}")
            return None

    def generate_histogram(self, data: List[float], bins: int = 10, title: str = "", filename: str = None) -> Optional[str]:
        """生成直方图"""
        if not MATPLOTLIB_AVAILABLE:
            return None

        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            ax.hist(data, bins=bins, color='skyblue', edgecolor='navy', alpha=0.7)

            ax.set_xlabel('值')
            ax.set_ylabel('频数')
            if title:
                ax.set_title(title, fontsize=16, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)

            plt.tight_layout()

            if not filename:
                filename = f"hist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            filepath = os.path.join(self.charts_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()

            return filepath
        except Exception as e:
            print(f"[错误] 直方图生成失败: {e}")
            return None

    def generate_scatter_plot(self, x_data: List[float], y_data: List[float], title: str = "", filename: str = None) -> Optional[str]:
        """生成散点图"""
        if not MATPLOTLIB_AVAILABLE:
            return None

        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            ax.scatter(x_data, y_data, c='blue', alpha=0.6, edgecolors='navy')

            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            if title:
                ax.set_title(title, fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)

            plt.tight_layout()

            if not filename:
                filename = f"scatter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            filepath = os.path.join(self.charts_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()

            return filepath
        except Exception as e:
            print(f"[错误] 散点图生成失败: {e}")
            return None


# ==========================================
# PDF生成工具
# ==========================================
class PDFGenerator:
    """PDF生成工具"""

    def __init__(self):
        self.pdfs_dir = os.path.join(EXPORT_DIR, "pdfs")
        os.makedirs(self.pdfs_dir, exist_ok=True)

    def generate_attendance_report(self, data: Dict, filename: str = None) -> Optional[str]:
        """生成考勤报表PDF"""
        try:
            from fpdf import FPDF

            pdf = FPDF()
            pdf.add_page()

            # 标题
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Attendance Report', ln=True, align='C')
            pdf.ln(10)

            # 班级信息
            pdf.set_font('Arial', '', 12)
            class_info = data.get('class', {})
            pdf.cell(0, 8, f"Class: {class_info.get('name', 'N/A')}", ln=True)
            pdf.cell(0, 8, f"Grade: {class_info.get('grade', 'N/A')}", ln=True)
            pdf.cell(0, 8, f"Period: {data.get('period', {}).get('start', '')} - {data.get('period', {}).get('end', '')}", ln=True)
            pdf.ln(10)

            # 统计
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Statistics', ln=True)
            pdf.set_font('Arial', '', 12)

            attendance = data.get('attendance', {})
            pdf.cell(0, 8, f"Total: {attendance.get('total', 0)}", ln=True)
            pdf.cell(0, 8, f"Present: {attendance.get('present', 0)} ({attendance.get('present_rate', 0)}%)", ln=True)
            pdf.cell(0, 8, f"Absent: {attendance.get('absent', 0)} ({attendance.get('absent_rate', 0)}%)", ln=True)
            pdf.cell(0, 8, f"Late: {attendance.get('late', 0)} ({attendance.get('late_rate', 0)}%)", ln=True)
            pdf.ln(10)

            if not filename:
                filename = f"attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            filepath = os.path.join(self.pdfs_dir, filename)
            pdf.output(filepath)

            return filepath
        except ImportError:
            print("[错误] fpdf库未安装，无法生成PDF")
            return None
        except Exception as e:
            print(f"[错误] PDF生成失败: {e}")
            return None

    def generate_student_report(self, student: Student, attendance_history: List, draw_history: List, filename: str = None) -> Optional[str]:
        """生成学生报告PDF"""
        try:
            from fpdf import FPDF

            pdf = FPDF()
            pdf.add_page()

            # 标题
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, f"Student Report: {student.name}", ln=True, align='C')
            pdf.ln(10)

            # 学生信息
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Student Information', ln=True)
            pdf.set_font('Arial', '', 12)

            pdf.cell(0, 8, f"Number: {student.number}", ln=True)
            pdf.cell(0, 8, f"Name: {student.name}", ln=True)
            pdf.cell(0, 8, f"Gender: {student.gender}", ln=True)
            pdf.cell(0, 8, f"Phone: {student.phone}", ln=True)
            pdf.cell(0, 8, f"Email: {student.email}", ln=True)
            pdf.ln(10)

            # 统计
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Statistics', ln=True)
            pdf.set_font('Arial', '', 12)

            pdf.cell(0, 8, f"Points: {student.points}", ln=True)
            pdf.cell(0, 8, f"Stars: {student.stars}", ln=True)
            pdf.cell(0, 8, f"Draw Count: {student.draw_count}", ln=True)
            pdf.cell(0, 8, f"Attendance Count: {student.attendance_count}", ln=True)
            pdf.cell(0, 8, f"Absent Count: {student.absent_count}", ln=True)

            if not filename:
                filename = f"student_{student.number}_{datetime.now().strftime('%Y%m%d')}.pdf"

            filepath = os.path.join(self.pdfs_dir, filename)
            pdf.output(filepath)

            return filepath
        except ImportError:
            print("[错误] fpdf库未安装，无法生成PDF")
            return None
        except Exception as e:
            print(f"[错误] PDF生成失败: {e}")
            return None


# ==========================================
# Excel导出工具
# ==========================================
class ExcelExporter:
    """Excel导出工具"""

    def __init__(self):
        self.excel_dir = os.path.join(EXPORT_DIR, "excel")
        os.makedirs(self.excel_dir, exist_ok=True)

    def export_attendance_report(self, records: List[AttendanceRecord], stats: Dict, filename: str = None) -> Optional[str]:
        """导出考勤报表到Excel"""
        try:
            import openpyxl
            from openpyxl.styles import Font, Alignment, PatternFill

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Attendance Report"

            # 标题
            ws['A1'] = "Attendance Report"
            ws['A1'].font = Font(size=16, bold=True)
            ws.merge_cells('A1:F1')

            # 统计
            ws['A3'] = "Statistics"
            ws['A3'].font = Font(size=12, bold=True)

            stats_data = [
                ["Total", stats.get('total', 0)],
                ["Present", stats.get('present', 0), f"{stats.get('present_rate', 0)}%"],
                ["Absent", stats.get('absent', 0), f"{stats.get('absent_rate', 0)}%"],
                ["Late", stats.get('late', 0), f"{stats.get('late_rate', 0)}%"],
                ["Leave", stats.get('leave', 0), f"{stats.get('leave_rate', 0)}%"],
            ]

            for i, row_data in enumerate(stats_data, start=4):
                for j, value in enumerate(row_data):
                    ws.cell(row=i, column=j + 1, value=value)

            # 表头
            ws['A10'] = "Student ID"
            ws['B10'] = "Name"
            ws['C10'] = "Date"
            ws['D10'] = "Status"
            ws['E10'] = "Check In Time"
            ws['F10'] = "Note"

            for col in range(1, 7):
                ws.cell(row=10, column=col).font = Font(bold=True)
                ws.cell(row=10, column=col).fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")

            # 数据
            status_names = {
                AttendanceStatus.PRESENT.value: 'Present',
                AttendanceStatus.ABSENT.value: 'Absent',
                AttendanceStatus.LATE.value: 'Late',
                AttendanceStatus.LEAVE.value: 'Leave'
            }

            for i, record in enumerate(records, start=11):
                ws.cell(row=i, column=1, value=record.student_id)
                ws.cell(row=i, column=2, value=record.student_name)
                ws.cell(row=i, column=3, value=record.date)
                ws.cell(row=i, column=4, value=status_names.get(record.status, 'Unknown'))
                ws.cell(row=i, column=5, value=record.check_in_time)
                ws.cell(row=i, column=6, value=record.note)

            if not filename:
                filename = f"attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            filepath = os.path.join(self.excel_dir, filename)
            wb.save(filepath)

            return filepath
        except ImportError:
            print("[错误] openpyxl库未安装，无法生成Excel")
            return None
        except Exception as e:
            print(f"[错误] Excel生成失败: {e}")
            return None

    def export_students_report(self, students: List[Student], filename: str = None) -> Optional[str]:
        """导出学生报表到Excel"""
        try:
            import openpyxl
            from openpyxl.styles import Font, Alignment, PatternFill

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Students Report"

            # 表头
            headers = ['Number', 'Name', 'Gender', 'Phone', 'Email', 'Points', 'Stars', 'Attendance', 'Absent', 'Draw Count']
            for i, header in enumerate(headers, start=1):
                ws.cell(row=1, column=i, value=header)
                ws.cell(row=1, column=i).font = Font(bold=True)
                ws.cell(row=1, column=i).fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")

            # 数据
            for i, student in enumerate(students, start=2):
                ws.cell(row=i, column=1, value=student.number)
                ws.cell(row=i, column=2, value=student.name)
                ws.cell(row=i, column=3, value=student.gender)
                ws.cell(row=i, column=4, value=student.phone)
                ws.cell(row=i, column=5, value=student.email)
                ws.cell(row=i, column=6, value=student.points)
                ws.cell(row=i, column=7, value=student.stars)
                ws.cell(row=i, column=8, value=student.attendance_count)
                ws.cell(row=i, column=9, value=student.absent_count)
                ws.cell(row=i, column=10, value=student.draw_count)

            if not filename:
                filename = f"students_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            filepath = os.path.join(self.excel_dir, filename)
            wb.save(filepath)

            return filepath
        except ImportError:
            print("[错误] openpyxl库未安装，无法生成Excel")
            return None
        except Exception as e:
            print(f"[错误] Excel生成失败: {e}")
            return None


# ==========================================
# 网络工具
# ==========================================
class NetworkUtils:
    """网络工具"""

    @staticmethod
    def check_internet() -> bool:
        """检查网络连接"""
        try:
            urllib.request.urlopen('https://www.google.com', timeout=3)
            return True
        except:
            return False

    @staticmethod
    def download_file(url: str, save_path: str, callback: Callable = None) -> bool:
        """下载文件"""
        try:
            def reporthook(block_num, block_size, total_size):
                if callback:
                    downloaded = block_num * block_size
                    if total_size > 0:
                        progress = min(100, downloaded * 100 // total_size)
                        callback(progress)

            urllib.request.urlretrieve(url, save_path, reporthook)
            return True
        except Exception as e:
            print(f"[错误] 文件下载失败: {e}")
            return False

    @staticmethod
    def get_json(url: str, headers: Dict = None) -> Optional[Dict]:
        """获取JSON数据"""
        try:
            request = urllib.request.Request(url)
            if headers:
                for key, value in headers.items():
                    request.add_header(key, value)

            with urllib.request.urlopen(request, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"[错误] JSON获取失败: {e}")
            return None

    @staticmethod
    def post_json(url: str, data: Dict, headers: Dict = None) -> Optional[Dict]:
        """发送JSON数据"""
        try:
            request = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            if headers:
                for key, value in headers.items():
                    request.add_header(key, value)

            with urllib.request.urlopen(request, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"[错误] JSON发送失败: {e}")
            return None

    @staticmethod
    def get_ip_address() -> str:
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    @staticmethod
    def get_public_ip() -> str:
        """获取公网IP地址"""
        try:
            response = urllib.request.urlopen('https://api.ipify.org', timeout=5)
            return response.read().decode('utf-8')
        except:
            return "Unknown"


# ==========================================
# 系统信息工具
# ==========================================
class SystemInfo:
    """系统信息"""

    @staticmethod
    def get_platform() -> str:
        """获取平台信息"""
        return sys.platform

    @staticmethod
    def get_python_version() -> str:
        """获取Python版本"""
        return sys.version

    @staticmethod
    def get_memory_info() -> Dict:
        """获取内存信息"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            }
        except:
            return {}

    @staticmethod
    def get_cpu_info() -> Dict:
        """获取CPU信息"""
        try:
            import psutil
            return {
                'count': psutil.cpu_count(),
                'percent': psutil.cpu_percent(interval=1)
            }
        except:
            return {}

    @staticmethod
    def get_disk_info() -> Dict:
        """获取磁盘信息"""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            return {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }
        except:
            return {}

    @staticmethod
    def get_boot_time() -> str:
        """获取系统启动时间"""
        try:
            import psutil
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            return boot_time.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return ""


# ==========================================
# 快捷方式管理器
# ==========================================
class ShortcutManager:
    """快捷方式管理器"""

    def __init__(self):
        self.shortcuts_file = os.path.join(DATA_DIR, "shortcuts.json")
        self.shortcuts = self._load_shortcuts()

    def _load_shortcuts(self) -> Dict:
        """加载快捷方式"""
        if os.path.exists(self.shortcuts_file):
            try:
                with open(self.shortcuts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return self._get_default_shortcuts()

    def _get_default_shortcuts(self) -> Dict:
        """获取默认快捷方式"""
        return {
            'start_stop': 'space',
            'reset': 'r',
            'settings': 's',
            'history': 'h',
            'students': 'f',
            'classes': 'c',
            'attendance': 'a',
            'statistics': 't',
            'help': '?',
            'exit': 'escape'
        }

    def save_shortcuts(self):
        """保存快捷方式"""
        try:
            with open(self.shortcuts_file, 'w', encoding='utf-8') as f:
                json.dump(self.shortcuts, f, ensure_ascii=False, indent=2)
        except:
            pass

    def get_shortcut(self, action: str) -> str:
        """获取快捷键"""
        return self.shortcuts.get(action, '')

    def set_shortcut(self, action: str, key: str):
        """设置快捷键"""
        self.shortcuts[action] = key
        self.save_shortcuts()


# ==========================================
# 缓存管理器
# ==========================================
class CacheManager:
    """缓存管理器"""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache = {}
        self.access_times = {}

    def get(self, key: str, default=None):
        """获取缓存"""
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return default

    def set(self, key: str, value):
        """设置缓存"""
        if len(self.cache) >= self.max_size:
            self._evict_oldest()

        self.cache[key] = value
        self.access_times[key] = time.time()

    def _evict_oldest(self):
        """清除最旧的缓存"""
        if not self.access_times:
            return

        oldest_key = min(self.access_times, key=self.access_times.get)
        del self.cache[oldest_key]
        del self.access_times[oldest_key]

    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_times.clear()

    def remove(self, key: str):
        """移除缓存"""
        if key in self.cache:
            del self.cache[key]
            del self.access_times[key]

    def size(self) -> int:
        """获取缓存大小"""
        return len(self.cache)


# ==========================================
# 事件系统
# ==========================================
class EventManager:
    """事件管理器"""

    def __init__(self):
        self.listeners = defaultdict(list)

    def on(self, event_name: str, callback: Callable):
        """注册事件监听器"""
        self.listeners[event_name].append(callback)

    def off(self, event_name: str, callback: Callable):
        """移除事件监听器"""
        if event_name in self.listeners:
            self.listeners[event_name].remove(callback)

    def emit(self, event_name: str, *args, **kwargs):
        """触发事件"""
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"[错误] 事件处理失败: {e}")


# ==========================================
# 命令行接口
# ==========================================
class CLI:
    """命令行接口"""

    def __init__(self):
        self.commands = {
            'help': self._cmd_help,
            'version': self._cmd_version,
            'info': self._cmd_info,
            'list': self._cmd_list,
            'export': self._cmd_export,
            'import': self._cmd_import,
            'backup': self._cmd_backup,
            'restore': self._cmd_restore,
            'clear': self._cmd_clear,
            'exit': self._cmd_exit,
        }

    def run(self):
        """运行CLI"""
        print(f"{APP_NAME} CLI V{VERSION}")
        print("Type 'help' for available commands.\n")

        while True:
            try:
                command = input("> ").strip()

                if not command:
                    continue

                parts = command.split()
                cmd = parts[0].lower()
                args = parts[1:]

                if cmd in self.commands:
                    result = self.commands[cmd](args)
                    if result:
                        print(result)
                else:
                    print(f"Unknown command: {cmd}. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\nUse 'exit' to quit.")
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")

    def _cmd_help(self, args):
        """帮助命令"""
        return """
Available commands:
  help          Show this help message
  version       Show version information
  info          Show system information
  list <type>   List data (students/classes/attendance)
  export <type> Export data to file
  import <type>  Import data from file
  backup        Create a backup
  restore       Restore from backup
  clear         Clear screen
  exit          Exit the application
        """

    def _cmd_version(self, args):
        """版本命令"""
        return f"{APP_NAME} V{VERSION}"

    def _cmd_info(self, args):
        """系统信息命令"""
        return f"""
Platform: {SystemInfo.get_platform()}
Python: {SystemInfo.get_python_version()}
        """

    def _cmd_list(self, args):
        """列出数据命令"""
        if not args:
            return "Please specify data type: students, classes, attendance"

        data_type = args[0].lower()
        return f"Listing {data_type}..."

    def _cmd_export(self, args):
        """导出命令"""
        if not args:
            return "Please specify data type to export"

        return f"Exporting {args[0]}..."

    def _cmd_import(self, args):
        """导入命令"""
        if not args:
            return "Please specify file path to import"

        return f"Importing from {args[0]}..."

    def _cmd_backup(self, args):
        """备份命令"""
        return "Creating backup..."

    def _cmd_restore(self, args):
        """恢复命令"""
        return "Restoring from backup..."

    def _cmd_clear(self, args):
        """清屏命令"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def _cmd_exit(self, args):
        """退出命令"""
        print("Goodbye!")
        exit(0)


# ==========================================
# 扩展功能模块（用于插件开发示例）
# ==========================================

# 示例插件代码 - 保存为 plugins/example_plugin.py 使用
EXAMPLE_PLUGIN_CODE = '''
"""
示例插件 - SmartPicker Pro
将文件保存到 plugins/example_plugin.py 即可自动加载
"""

class Plugin:
    """插件基类"""

    def __init__(self):
        self.name = "Example Plugin"
        self.version = "1.0.0"
        self.author = "Developer"
        self.description = "这是一个示例插件"

    def on_load(self):
        """插件加载时调用"""
        print(f"[插件] {self.name} 已加载")

    def on_unload(self):
        """插件卸载时调用"""
        print(f"[插件] {self.name} 已卸载")

    def on_event(self, event_name: str, *args, **kwargs):
        """处理事件"""
        print(f"[插件] 收到事件: {event_name}")

    def get_menu(self):
        """获取菜单项"""
        return [
            {"label": "插件示例", "command": self.example_command}
        ]

    def example_command(self):
        """示例命令"""
        print("这是插件的示例命令!")
'''

# 导出所有工具类和函数
__all__ = [
    'DatabaseManager', 'StudentManager', 'ClassManager', 'AttendanceManager',
    'DrawRecordManager', 'RewardManager', 'BackupManager', 'ImportExportManager',
    'StatisticsAnalyzer', 'SoundManager', 'AnimationEngine', 'ThemeManager',
    'I18nManager', 'Validator', 'CryptoUtils', 'FileUtils', 'DateTimeUtils',
    'StringUtils', 'ListUtils', 'MathUtils', 'ChartGenerator', 'PDFGenerator',
    'ExcelExporter', 'NetworkUtils', 'SystemInfo', 'ShortcutManager', 'CacheManager',
    'EventManager', 'CLI', 'ScheduledAttendanceManager', 'GroupManager',
    'SeatManager', 'NotificationManager', 'LogManager', 'PluginManager',
    'Student', 'ClassInfo', 'AttendanceRecord', 'DrawRecord', 'SeatInfo',
    'DrawMode', 'AttendanceStatus', 'StudentState', 'RewardType', 'PunishmentType',
    'generate_unique_id', 'safe_after_call'
]



# ==========================================
# 高级UI组件
# ==========================================

# ==========================================
# 高级对话框
# ==========================================
class AdvancedDialogs:
    """高级对话框"""

    @staticmethod
    def show_info(title: str, message: str, parent=None):
        """显示信息对话框"""
        messagebox.showinfo(title, message, parent=parent)

    @staticmethod
    def show_warning(title: str, message: str, parent=None):
        """显示警告对话框"""
        messagebox.showwarning(title, message, parent=parent)

    @staticmethod
    def show_error(title: str, message: str, parent=None):
        """显示错误对话框"""
        messagebox.showerror(title, message, parent=parent)

    @staticmethod
    def ask_yes_no(title: str, message: str, parent=None) -> bool:
        """询问是否"""
        return messagebox.askyesno(title, message, parent=parent)

    @staticmethod
    def ask_ok_cancel(title: str, message: str, parent=None) -> bool:
        """询问确定"""
        return messagebox.askokcancel(title, message, parent=parent)

    @staticmethod
    def ask_retry_cancel(title: str, message: str, parent=None) -> bool:
        """询问重试"""
        return messagebox.askretrycancel(title, message, parent=parent)

    @staticmethod
    def ask_yes_no_cancel(title: str, message: str, parent=None) -> Optional[str]:
        """询问是否取消"""
        return messagebox.askyesnocancel(title, message, parent=parent)

    @staticmethod
    def input_string(title: str, prompt: str, initial_value: str = "", parent=None) -> Optional[str]:
        """输入字符串"""
        return simpledialog.askstring(title, prompt, initialvalue=initial_value, parent=parent)

    @staticmethod
    def input_integer(title: str, prompt: str, initial_value: int = 0, min_value: int = None, max_value: int = None, parent=None) -> Optional[int]:
        """输入整数"""
        return simpledialog.askinteger(title, prompt, initialvalue=initial_value, minvalue=min_value, maxvalue=max_value, parent=parent)

    @staticmethod
    def input_float(title: str, prompt: str, initial_value: float = 0.0, min_value: float = None, max_value: float = None, parent=None) -> Optional[float]:
        """输入浮点数"""
        return simpledialog.askfloat(title, prompt, initialvalue=initial_value, minvalue=min_value, maxvalue=max_value, parent=parent)

    @staticmethod
    def select_file(title: str = "选择文件", initial_dir: str = None, file_types: List[Tuple[str, str]] = None, parent=None) -> Optional[str]:
        """选择文件"""
        if file_types is None:
            file_types = [("所有文件", "*.*")]
        return filedialog.askopenfilename(title=title, initialdir=initial_dir, filetypes=file_types, parent=parent)

    @staticmethod
    def select_files(title: str = "选择文件", initial_dir: str = None, file_types: List[Tuple[str, str]] = None, parent=None) -> Optional[List[str]]:
        """选择多个文件"""
        if file_types is None:
            file_types = [("所有文件", "*.*")]
        return filedialog.askopenfilenames(title=title, initialdir=initial_dir, filetypes=file_types, parent=parent)

    @staticmethod
    def select_directory(title: str = "选择目录", initial_dir: str = None, parent=None) -> Optional[str]:
        """选择目录"""
        return filedialog.askdirectory(title=title, initialdir=initial_dir, parent=parent)

    @staticmethod
    def save_file(title: str = "保存文件", initial_dir: str = None, default_extension: str = None, file_types: List[Tuple[str, str]] = None, parent=None) -> Optional[str]:
        """保存文件"""
        if file_types is None:
            file_types = [("所有文件", "*.*")]
        return filedialog.asksaveasfilename(title=title, initialdir=initial_dir, defaultextension=default_extension, filetypes=file_types, parent=parent)

    @staticmethod
    def select_color(title: str = "选择颜色", initial_color: str = "#000000", parent=None) -> Optional[str]:
        """选择颜色"""
        try:
            from tkinter.colorchooser import askcolor
            color = askcolor(initialcolor=initial_color, title=title, parent=parent)
            return color[1] if color else None
        except:
            return initial_color

    @staticmethod
    def show_custom_dialog(title: str, width: int = 400, height: int = 300, parent=None):
        """显示自定义对话框"""
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        dialog.resizable(False, False)

        if parent:
            dialog.transient(parent)
            dialog.grab_set()

        return dialog


# ==========================================
# 表格组件
# ==========================================
class TableWidget:
    """表格组件"""

    def __init__(self, parent, columns: List[str], headings: List[str] = None, widths: List[int] = None):
        self.parent = parent
        self.columns = columns
        self.headings = headings or columns
        self.widths = widths or [100] * len(columns)

        self.frame = tk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # 表头
        self.header_frame = tk.Frame(self.frame)
        self.header_frame.pack(fill=tk.X)

        self.header_labels = []
        for i, (heading, width) in enumerate(zip(self.headings, self.widths)):
            label = tk.Label(
                self.header_frame, text=heading,
                font=("Microsoft YaHei", 10, "bold"),
                bg="#e0e0e0", pady=5,
                width=width // 8, cursor="hand2"
            )
            label.pack(side=tk.LEFT, padx=1)
            label.bind("<Button-1>", lambda e, col=i: self._on_header_click(col))
            self.header_labels.append(label)

        # 数据区域
        self.canvas = tk.Canvas(self.frame, bg="white")
        self.scrollbar_y = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar_x = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.inner_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.rows = []
        self.data = []
        self.sort_column = None
        self.sort_reverse = False

    def _on_canvas_configure(self, event):
        """画布配置"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_header_click(self, column: int):
        """表头点击排序"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
        self.sort_column = column
        self._refresh()

    def set_data(self, data: List[List]):
        """设置数据"""
        self.data = data
        self._refresh()

    def add_row(self, row_data: List, tags: tuple = ()):
        """添加行"""
        self.data.append(row_data)
        self._refresh()

    def insert_row(self, index: int, row_data: List, tags: tuple = ()):
        """插入行"""
        self.data.insert(index, row_data)
        self._refresh()

    def delete_row(self, index: int):
        """删除行"""
        if 0 <= index < len(self.data):
            self.data.pop(index)
            self._refresh()

    def clear(self):
        """清空数据"""
        self.data = []
        self._refresh()

    def _refresh(self):
        """刷新表格"""
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        if self.sort_column is not None:
            self.data = sorted(self.data, key=lambda x: x[self.sort_column], reverse=self.sort_reverse)

        for i, row_data in enumerate(self.data):
            bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
            row_frame = tk.Frame(self.inner_frame, bg=bg)
            row_frame.pack(fill=tk.X, pady=0.5)

            for j, value in enumerate(row_data):
                label = tk.Label(
                    row_frame, text=str(value),
                    font=("Microsoft YaHei", 9),
                    bg=bg, pady=3,
                    width=self.widths[j] // 8
                )
                label.pack(side=tk.LEFT, padx=1)

        self.inner_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def get_selected_row(self) -> Optional[int]:
        """获取选中行"""
        pass  # 可扩展

    def get_cell_value(self, row: int, col: int):
        """获取单元格值"""
        if 0 <= row < len(self.data) and 0 <= col < len(self.columns):
            return self.data[row][col]
        return None

    def set_cell_value(self, row: int, col: int, value):
        """设置单元格值"""
        if 0 <= row < len(self.data) and 0 <= col < len(self.columns):
            self.data[row][col] = value
            self._refresh()


# ==========================================
# 卡片组件
# ==========================================
class CardWidget:
    """卡片组件"""

    def __init__(self, parent, title: str = "", content: str = "", icon: str = "", **kwargs):
        self.parent = parent
        self.frame = tk.Frame(parent, bg="white", bd=1, relief=tk.SOLID, **kwargs)
        self.frame.pack_propagate(False)

        if icon:
            icon_label = tk.Label(self.frame, text=icon, font=("Microsoft YaHei", 30), bg="white")
            icon_label.pack(pady=(10, 5))

        if title:
            title_label = tk.Label(
                self.frame, text=title,
                font=("Microsoft YaHei", 14, "bold"),
                bg="white"
            )
            title_label.pack()

        if content:
            content_label = tk.Label(
                self.frame, text=content,
                font=("Microsoft YaHei", 10),
                bg="white", fg="gray"
            )
            content_label.pack(pady=(5, 10))

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        """网格布局"""
        self.frame.grid(**kwargs)

    def configure(self, **kwargs):
        """配置"""
        self.frame.configure(**kwargs)


# ==========================================
# 标签页组件
# ==========================================
class TabWidget:
    """标签页组件"""

    def __init__(self, parent):
        self.parent = parent
        self.notebook = tk.ttk.Notebook(parent)
        self.tabs = {}
        self.current_tab = None

    def add_tab(self, name: str, title: str) -> tk.Frame:
        """添加标签页"""
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        self.tabs[name] = frame
        return frame

    def get_tab(self, name: str) -> Optional[tk.Frame]:
        """获取标签页"""
        return self.tabs.get(name)

    def remove_tab(self, name: str):
        """移除标签页"""
        if name in self.tabs:
            index = list(self.tabs.keys()).index(name)
            self.notebook.forget(index)
            del self.tabs[name]

    def select_tab(self, name: str):
        """选择标签页"""
        if name in self.tabs:
            index = list(self.tabs.keys()).index(name)
            self.notebook.select(index)
            self.current_tab = name

    def pack(self, **kwargs):
        """打包"""
        self.notebook.pack(**kwargs)


# ==========================================
# 进度条组件
# ==========================================
class ProgressWidget:
    """进度条组件"""

    def __init__(self, parent, width: int = 300, height: int = 20):
        self.parent = parent
        self.width = width
        self.height = height

        self.frame = tk.Frame(parent, bg="white", bd=1, relief=tk.SOLID)
        self.canvas = tk.Canvas(self.frame, width=width, height=height, bg="white", highlightthickness=0)
        self.canvas.pack()

        self.progress_rect = self.canvas.create_rectangle(0, 0, 0, height, fill="#4caf50", outline="")
        self.text_id = self.canvas.create_text(width // 2, height // 2, text="0%", fill="black", font=("Microsoft YaHei", 9))

        self.value = 0

    def set_value(self, value: int):
        """设置值"""
        self.value = max(0, min(100, value))
        bar_width = int(self.width * self.value / 100)
        self.canvas.coords(self.progress_rect, 0, 0, bar_width, self.height)
        self.canvas.itemconfig(self.text_id, text=f"{self.value}%")
        self.frame.update_idletasks()

    def get_value(self) -> int:
        """获取值"""
        return self.value

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)


# ==========================================
# 搜索框组件
# ==========================================
class SearchBox:
    """搜索框组件"""

    def __init__(self, parent, placeholder: str = "搜索...", on_search: Callable = None, on_clear: Callable = None):
        self.parent = parent
        self.on_search = on_search
        self.on_clear = on_clear

        self.frame = tk.Frame(parent, bg="white", bd=1, relief=tk.SOLID)

        self.search_icon = tk.Label(
            self.frame, text="🔍",
            font=("Microsoft YaHei", 10),
            bg="white"
        )
        self.search_icon.pack(side=tk.LEFT, padx=5)

        self.entry = tk.Entry(
            self.frame, font=("Microsoft YaHei", 10),
            relief=tk.FLAT, bg="white",
            width=30
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.insert(0, placeholder)
        self.entry.config(fg="gray")

        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<KeyRelease>", self._on_key_release)

        self.clear_btn = tk.Label(
            self.frame, text="✕",
            font=("Microsoft YaHei", 8),
            bg="white", cursor="hand2"
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=5)
        self.clear_btn.bind("<Button-1>", self._on_clear_click)
        self.clear_btn.pack_forget()

    def _on_focus_in(self, event):
        """获得焦点"""
        if self.entry.get() == self._get_placeholder():
            self.entry.delete(0, tk.END)
            self.entry.config(fg="black")
        self.clear_btn.pack(side=tk.RIGHT, padx=5)

    def _on_focus_out(self, event):
        """失去焦点"""
        if not self.entry.get():
            self.entry.insert(0, self._get_placeholder())
            self.entry.config(fg="gray")
            self.clear_btn.pack_forget()

    def _on_key_release(self, event):
        """按键释放"""
        if self.on_search and self.entry.get() != self._get_placeholder():
            self.on_search(self.entry.get())

    def _on_clear_click(self, event):
        """清除点击"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self._get_placeholder())
        self.entry.config(fg="gray")
        self.clear_btn.pack_forget()
        if self.on_clear:
            self.on_clear()

    def _get_placeholder(self) -> str:
        """获取占位符"""
        return "搜索..."

    def get_value(self) -> str:
        """获取值"""
        value = self.entry.get()
        return value if value != self._get_placeholder() else ""

    def set_value(self, value: str):
        """设置值"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
        self.entry.config(fg="black")
        self.clear_btn.pack(side=tk.RIGHT, padx=5)

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)


# ==========================================
# 分页组件
# ==========================================
class PaginationWidget:
    """分页组件"""

    def __init__(self, parent, total: int, per_page: int = 20, on_page_change: Callable = None):
        self.parent = parent
        self.total = total
        self.per_page = per_page
        self.current_page = 1
        self.on_page_change = on_page_change

        self.total_pages = max(1, (total + per_page - 1) // per_page)

        self.frame = tk.Frame(parent, bg="white")

        self.prev_btn = tk.Button(
            self.frame, text="◀",
            font=("Microsoft YaHei", 10),
            bg="white", relief=tk.FLAT,
            cursor="hand2", command=self._prev_page
        )
        self.prev_btn.pack(side=tk.LEFT)

        self.page_label = tk.Label(
            self.frame, text=f"1 / {self.total_pages}",
            font=("Microsoft YaHei", 10),
            bg="white", padx=10
        )
        self.page_label.pack(side=tk.LEFT)

        self.next_btn = tk.Button(
            self.frame, text="▶",
            font=("Microsoft YaHei", 10),
            bg="white", relief=tk.FLAT,
            cursor="hand2", command=self._next_page
        )
        self.next_btn.pack(side=tk.LEFT)

        self.info_label = tk.Label(
            self.frame, text=f"共 {total} 条",
            font=("Microsoft YaHei", 9),
            bg="white", fg="gray"
        )
        self.info_label.pack(side=tk.LEFT, padx=20)

        self._update_buttons()

    def _prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self._update()
            if self.on_page_change:
                self.on_page_change(self.current_page)

    def _next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._update()
            if self.on_page_change:
                self.on_page_change(self.current_page)

    def _update(self):
        """更新"""
        self.page_label.config(text=f"{self.current_page} / {self.total_pages}")
        self._update_buttons()

    def _update_buttons(self):
        """更新按钮状态"""
        self.prev_btn.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_page < self.total_pages else tk.DISABLED)

    def set_total(self, total: int):
        """设置总数"""
        self.total = total
        self.total_pages = max(1, (total + per_page - 1) // per_page)
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        self._update()

    def get_offset(self) -> int:
        """获取偏移量"""
        return (self.current_page - 1) * self.per_page

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)


# ==========================================
# 评分组件
# ==========================================
class RatingWidget:
    """评分组件"""

    def __init__(self, parent, max_rating: int = 5, on_change: Callable = None):
        self.parent = parent
        self.max_rating = max_rating
        self.on_change = on_change
        self.rating = 0

        self.frame = tk.Frame(parent, bg="white")

        self.stars = []
        for i in range(max_rating):
            star = tk.Label(
                self.frame, text="☆",
                font=("Microsoft YaHei", 20),
                bg="white", cursor="hand2"
            )
            star.pack(side=tk.LEFT)
            star.bind("<Button-1>", lambda e, idx=i: self._set_rating(idx + 1))
            star.bind("<Enter>", lambda e, idx=i: self._preview_rating(idx + 1))
            star.bind("<Leave>", lambda e: self._update_stars())
            self.stars.append(star)

    def _set_rating(self, rating: int):
        """设置评分"""
        self.rating = rating
        self._update_stars()
        if self.on_change:
            self.on_change(rating)

    def _preview_rating(self, rating: int):
        """预览评分"""
        for i, star in enumerate(self.stars):
            if i < rating:
                star.config(text="★")
            else:
                star.config(text="☆")

    def _update_stars(self):
        """更新星星显示"""
        for i, star in enumerate(self.stars):
            if i < self.rating:
                star.config(text="★", fg="#ffc107")
            else:
                star.config(text="☆", fg="#bdbdbd")

    def get_rating(self) -> int:
        """获取评分"""
        return self.rating

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)


# ==========================================
# 标签输入组件
# ==========================================
class TagInputWidget:
    """标签输入组件"""

    def __init__(self, parent, placeholder: str = "输入标签...", on_change: Callable = None):
        self.parent = parent
        self.placeholder = placeholder
        self.on_change = on_change
        self.tags = []

        self.frame = tk.Frame(parent, bg="white", bd=1, relief=tk.SOLID)

        self.canvas = tk.Canvas(self.frame, height=60, bg="white", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.inner_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="w")

        self.entry = tk.Entry(
            self.inner_frame, font=("Microsoft YaHei", 10),
            relief=tk.FLAT, bg="white",
            width=20
        )
        self.entry.pack(side=tk.LEFT)
        self.entry.insert(0, placeholder)
        self.entry.config(fg="gray")
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<KeyRelease>", self._on_key_release)

        self.canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def _on_focus_in(self, event):
        """获得焦点"""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg="black")

    def _on_focus_out(self, event):
        """失去焦点"""
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg="gray")

    def _on_key_release(self, event):
        """按键释放"""
        if event.keysym == "Return":
            tag = self.entry.get()
            if tag and tag != self.placeholder:
                self.add_tag(tag)
                self.entry.delete(0, tk.END)

    def add_tag(self, tag: str):
        """添加标签"""
        if tag not in self.tags:
            self.tags.append(tag)
            self._refresh_tags()
            if self.on_change:
                self.on_change(self.tags)

    def remove_tag(self, tag: str):
        """移除标签"""
        if tag in self.tags:
            self.tags.remove(tag)
            self._refresh_tags()
            if self.on_change:
                self.on_change(self.tags)

    def _refresh_tags(self):
        """刷新标签显示"""
        for widget in self.inner_frame.winfo_children()[:-1]:
            widget.destroy()

        x = 5
        for tag in self.tags:
            tag_frame = tk.Frame(self.inner_frame, bg="#e3f2fd", bd=1, relief=tk.SOLID)
            tag_label = tk.Label(
                tag_frame, text=tag,
                font=("Microsoft YaHei", 9),
                bg="#e3f2fd", padx=8, pady=2
            )
            tag_label.pack(side=tk.LEFT)

            close_btn = tk.Label(
                tag_frame, text="✕",
                font=("Microsoft YaHei", 8),
                bg="#e3f2fd", cursor="hand2"
            )
            close_btn.pack(side=tk.LEFT, padx=2)
            close_btn.bind("<Button-1>", lambda e, t=tag: self.remove_tag(t))

            tag_frame.pack(side=tk.LEFT, padx=3, pady=5)

        self.entry.lift()

    def get_tags(self) -> List[str]:
        """获取标签"""
        return self.tags

    def set_tags(self, tags: List[str]):
        """设置标签"""
        self.tags = tags
        self._refresh_tags()

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)


# ==========================================
# 富文本编辑器
# ==========================================
class RichTextEditor:
    """富文本编辑器"""

    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent)

        # 工具栏
        self.toolbar = tk.Frame(self.frame, bg="#f5f5f5")
        self.toolbar.pack(fill=tk.X)

        self.bold_btn = tk.Button(
            self.toolbar, text="B",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT, cursor="hand2",
            command=lambda: self._format("bold")
        )
        self.bold_btn.pack(side=tk.LEFT, padx=2)

        self.italic_btn = tk.Button(
            self.toolbar, text="I",
            font=("Arial", 10, "italic"),
            relief=tk.FLAT, cursor="hand2",
            command=lambda: self._format("italic")
        )
        self.italic_btn.pack(side=tk.LEFT, padx=2)

        self.underline_btn = tk.Button(
            self.toolbar, text="U",
            font=("Arial", 10),
            relief=tk.FLAT, cursor="hand2",
            command=lambda: self._format("underline")
        )
        self.underline_btn.pack(side=tk.LEFT, padx=2)

        # 文本框
        self.text = tk.Text(
            self.frame, font=("Microsoft YaHei", 10),
            wrap=tk.WORD, padx=10, pady=10,
            undo=True
        )
        self.text.pack(fill=tk.BOTH, expand=True)

        # 滚动条
        scrollbar = tk.Scrollbar(self.text, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=scrollbar.set)

    def _format(self, tag: str):
        """格式化"""
        try:
            self.text.tag_config(tag, font=("Microsoft YaHei", 10, tag))
            current_tags = self.text.tag_names("sel.first")
            if tag in current_tags:
                self.text.tag_remove(tag, "sel.first", "sel.last")
            else:
                self.text.tag_add(tag, "sel.first", "sel.last")
        except:
            pass

    def get_content(self) -> str:
        """获取内容"""
        return self.text.get("1.0", tk.END)

    def set_content(self, content: str):
        """设置内容"""
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)


# ==========================================
# 日历组件
# ==========================================
class CalendarWidget:
    """日历组件"""

    def __init__(self, parent, on_select: Callable = None):
        self.parent = parent
        self.on_select = on_select
        self.current_date = datetime.now()
        self.selected_date = None

        self.frame = tk.Frame(parent, bg="white")

        # 标题栏
        self.title_frame = tk.Frame(self.frame, bg="white")
        self.title_frame.pack(fill=tk.X, pady=5)

        self.prev_btn = tk.Button(
            self.title_frame, text="◀",
            font=("Microsoft YaHei", 10),
            bg="white", relief=tk.FLAT,
            cursor="hand2", command=self._prev_month
        )
        self.prev_btn.pack(side=tk.LEFT, padx=10)

        self.month_label = tk.Label(
            self.title_frame,
            font=("Microsoft YaHei", 12, "bold"),
            bg="white"
        )
        self.month_label.pack(side=tk.LEFT, expand=True)

        self.next_btn = tk.Button(
            self.title_frame, text="▶",
            font=("Microsoft YaHei", 10),
            bg="white", relief=tk.FLAT,
            cursor="hand2", command=self._next_month
        )
        self.next_btn.pack(side=tk.RIGHT, padx=10)

        # 星期标题
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        weekday_frame = tk.Frame(self.frame, bg="white")
        weekday_frame.pack(fill=tk.X)

        for day in weekdays:
            label = tk.Label(
                weekday_frame, text=day,
                font=("Microsoft YaHei", 9),
                bg="white", fg="gray",
                width=4, pady=5
            )
            label.pack(side=tk.LEFT)

        # 日期网格
        self.days_frame = tk.Frame(self.frame, bg="white")
        self.days_frame.pack(fill=tk.BOTH, expand=True)

        self._render_calendar()

    def _prev_month(self):
        """上一个月"""
        year = self.current_date.year
        month = self.current_date.month - 1
        if month < 1:
            month = 12
            year -= 1
        self.current_date = datetime(year, month, 1)
        self._render_calendar()

    def _next_month(self):
        """下一个月"""
        year = self.current_date.year
        month = self.current_date.month + 1
        if month > 12:
            month = 1
            year += 1
        self.current_date = datetime(year, month, 1)
        self._render_calendar()

    def _render_calendar(self):
        """渲染日历"""
        self.month_label.config(text=self.current_date.strftime("%Y年%m月"))

        for widget in self.days_frame.winfo_children():
            widget.destroy()

        year = self.current_date.year
        month = self.current_date.month

        first_day = datetime(year, month, 1)
        last_day = (datetime(year, month + 1, 1) - timedelta(days=1)) if month < 12 else datetime(year + 1, 1, 1) - timedelta(days=1)

        start_weekday = first_day.weekday()

        day = 1
        for week in range(6):
            week_frame = tk.Frame(self.days_frame, bg="white")
            week_frame.pack(fill=tk.X)

            for weekday in range(7):
                cell_frame = tk.Frame(week_frame, bg="white", width=50, height=40)

                if week == 0 and weekday < start_weekday:
                    cell_frame.pack(side=tk.LEFT, padx=1, pady=1)
                elif day <= last_day.day:
                    date = datetime(year, month, day)
                    label = tk.Label(
                        cell_frame, text=str(day),
                        font=("Microsoft YaHei", 10),
                        bg="white", cursor="hand2",
                        width=4
                    )
                    label.pack(pady=5)

                    if date.date() == datetime.now().date():
                        label.config(fg="#1976d2", font=("Microsoft YaHei", 10, "bold"))

                    label.bind("<Button-1>", lambda e, d=date: self._select_date(d))

                    cell_frame.pack(side=tk.LEFT, padx=1, pady=1)
                    day += 1
                else:
                    cell_frame.pack(side=tk.LEFT, padx=1, pady=1)

    def _select_date(self, date: datetime):
        """选择日期"""
        self.selected_date = date
        if self.on_select:
            self.on_select(date.strftime("%Y-%m-%d"))
        self._render_calendar()

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)


# ==========================================
# 时间选择器
# ==========================================
class TimePickerWidget:
    """时间选择器"""

    def __init__(self, parent, on_change: Callable = None):
        self.parent = parent
        self.on_change = on_change

        self.frame = tk.Frame(parent, bg="white")

        self.hour_var = tk.StringVar(value="00")
        self.minute_var = tk.StringVar(value="00")
        self.second_var = tk.StringVar(value="00")

        hours = [f"{i:02d}" for i in range(24)]
        minutes = [f"{i:02d}" for i in range(60)]
        seconds = [f"{i:02d}" for i in range(60)]

        self.hour_combo = tk.ttk.Combobox(
            self.frame, textvariable=self.hour_var,
            values=hours, width=5,
            state="readonly"
        )
        self.hour_combo.pack(side=tk.LEFT)
        self.hour_combo.bind("<<ComboboxSelected>>", self._on_change)

        tk.Label(self.frame, text=":", font=("Microsoft YaHei", 12), bg="white").pack(side=tk.LEFT)

        self.minute_combo = tk.ttk.Combobox(
            self.frame, textvariable=self.minute_var,
            values=minutes, width=5,
            state="readonly"
        )
        self.minute_combo.pack(side=tk.LEFT)
        self.minute_combo.bind("<<ComboboxSelected>>", self._on_change)

        tk.Label(self.frame, text=":", font=("Microsoft YaHei", 12), bg="white").pack(side=tk.LEFT)

        self.second_combo = tk.ttk.Combobox(
            self.frame, textvariable=self.second_var,
            values=seconds, width=5,
            state="readonly"
        )
        self.second_combo.pack(side=tk.LEFT)
        self.second_combo.bind("<<ComboboxSelected>>", self._on_change)

    def _on_change(self, event=None):
        """值改变"""
        if self.on_change:
            self.on_change(self.get_time())

    def get_time(self) -> str:
        """获取时间"""
        return f"{self.hour_var.get()}:{self.minute_var.get()}:{self.second_var.get()}"

    def set_time(self, time_str: str):
        """设置时间"""
        parts = time_str.split(":")
        if len(parts) == 3:
            self.hour_var.set(parts[0])
            self.minute_var.set(parts[1])
            self.second_var.set(parts[2])

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)


# ==========================================
# 头像上传组件
# ==========================================
class AvatarUploadWidget:
    """头像上传组件"""

    def __init__(self, parent, size: int = 100, on_change: Callable = None):
        self.parent = parent
        self.size = size
        self.on_change = on_change
        self.image_path = None

        self.frame = tk.Frame(parent, bg="white", width=size, height=size)
        self.frame.pack_propagate(False)

        self.canvas = tk.Canvas(
            self.frame, width=size, height=size,
            bg="#f0f0f0", highlightthickness=0,
            cursor="hand2"
        )
        self.canvas.pack()

        self.placeholder_id = self.canvas.create_text(
            size // 2, size // 2,
            text="📷",
            font=("Microsoft YaHei", int(size // 4))
        )

        self.canvas.bind("<Button-1>", self._on_click)

    def _on_click(self, event):
        """点击"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.gif;*.bmp")]
        )

        if file_path:
            self.set_image(file_path)
            if self.on_change:
                self.on_change(file_path)

    def set_image(self, image_path: str):
        """设置图片"""
        self.image_path = image_path

        try:
            if PIL_AVAILABLE:
                img = Image.open(image_path)
                img = img.resize((self.size, self.size), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                self.canvas.delete(self.placeholder_id)
                self.canvas.create_image(self.size // 2, self.size // 2, image=photo)
                self.canvas.image = photo
        except:
            pass

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)


# ==========================================
# 轮播图组件
# ==========================================
class CarouselWidget:
    """轮播图组件"""

    def __init__(self, parent, width: int = 600, height: int = 300):
        self.parent = parent
        self.width = width
        self.height = height
        self.images = []
        self.current_index = 0

        self.frame = tk.Frame(parent, width=width, height=height)
        self.frame.pack_propagate(False)

        self.canvas = tk.Canvas(
            self.frame, width=width, height=height,
            bg="#f0f0f0", highlightthickness=0
        )
        self.canvas.pack()

        self.prev_btn = tk.Button(
            self.canvas, text="◀",
            font=("Microsoft YaHei", 16),
            bg="rgba(0,0,0,0.3)", fg="white",
            relief=tk.FLAT, cursor="hand2",
            command=self._prev
        )
        self.canvas.create_window(20, height // 2, window=self.prev_btn)

        self.next_btn = tk.Button(
            self.canvas, text="▶",
            font=("Microsoft YaHei", 16),
            bg="rgba(0,0,0,0.3)", fg="white",
            relief=tk.FLAT, cursor="hand2",
            command=self._next
        )
        self.canvas.create_window(width - 20, height // 2, window=self.next_btn)

        self.indicator_frame = tk.Frame(self.canvas, bg="rgba(0,0,0,0.3)")
        self.indicator_canvas = tk.Canvas(self.indicator_frame, width=width, height=30, bg="transparent", highlightthickness=0)
        self.indicator_canvas.pack()
        self.indicators = []
        self.canvas.create_window(width // 2, height - 15, window=self.indicator_frame)

    def add_image(self, image_path: str, title: str = ""):
        """添加图片"""
        self.images.append({"path": image_path, "title": title})
        self._update_indicators()
        if len(self.images) == 1:
            self._show_image(0)

    def _prev(self):
        """上一张"""
        if self.images:
            self.current_index = (self.current_index - 1 + len(self.images)) % len(self.images)
            self._show_image(self.current_index)

    def _next(self):
        """下一张"""
        if self.images:
            self.current_index = (self.current_index + 1) % len(self.images)
            self._show_image(self.current_index)

    def _show_image(self, index: int):
        """显示图片"""
        if PIL_AVAILABLE and index < len(self.images):
            try:
                img = Image.open(self.images[index]["path"])
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                self.canvas.delete("all")
                self.canvas.create_image(self.width // 2, self.height // 2, image=photo)
                self.canvas.image = photo

                self._update_indicators()
            except:
                pass

    def _update_indicators(self):
        """更新指示器"""
        self.indicator_canvas.delete("all")
        self.indicators = []

        for i in range(len(self.images)):
            color = "#4caf50" if i == self.current_index else "white"
            x = (self.width // 2) + (i - len(self.images) // 2) * 20
            self.indicators.append(
                self.indicator_canvas.create_oval(x - 5, 10, x + 5, 20, fill=color, outline="")
            )

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)


# ==========================================
# 步骤指示器
# ==========================================
class StepIndicatorWidget:
    """步骤指示器"""

    def __init__(self, parent, steps: List[str]):
        self.parent = parent
        self.steps = steps
        self.current_step = 0

        self.frame = tk.Frame(parent, bg="white")

        self.step_frames = []
        self.step_labels = []
        self.step_lines = []

        for i, step in enumerate(steps):
            # 步骤圆圈
            step_frame = tk.Frame(self.frame, bg="white")

            circle = tk.Canvas(step_frame, width=30, height=30, bg="white", highlightthickness=0)
            if i <= self.current_step:
                circle.create_oval(2, 2, 28, 28, fill="#4caf50", outline="")
                circle.create_text(15, 15, text=str(i + 1), fill="white", font=("Microsoft YaHei", 10, "bold"))
            else:
                circle.create_oval(2, 2, 28, 28, fill="#e0e0e0", outline="")
                circle.create_text(15, 15, text=str(i + 1), fill="gray", font=("Microsoft YaHei", 10, "bold"))
            circle.pack()

            # 步骤名称
            label = tk.Label(
                step_frame, text=step,
                font=("Microsoft YaHei", 9),
                bg="white", fg="gray" if i > self.current_step else "black"
            )
            label.pack()

            step_frame.pack(side=tk.LEFT)

            if i < len(steps) - 1:
                line = tk.Frame(self.frame, bg="#e0e0e0", width=50, height=2)
                line.pack(side=tk.LEFT, pady=10, padx=5)
                self.step_lines.append(line)

            self.step_frames.append(step_frame)
            self.step_labels.append(label)

    def set_step(self, step: int):
        """设置当前步骤"""
        self.current_step = step
        self._refresh()

    def next_step(self):
        """下一步"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._refresh()

    def prev_step(self):
        """上一步"""
        if self.current_step > 0:
            self.current_step -= 1
            self._refresh()

    def _refresh(self):
        """刷新"""
        for i in range(len(self.steps)):
            if i <= self.current_step:
                self.step_labels[i].config(fg="black")
                if i < len(self.steps) - 1:
                    self.step_lines[i].config(bg="#4caf50")
            else:
                self.step_labels[i].config(fg="gray")
                if i < len(self.steps) - 1:
                    self.step_lines[i].config(bg="#e0e0e0")

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)


# ==========================================
# 折叠面板
# ==========================================
class AccordionWidget:
    """折叠面板"""

    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent, bg="white")
        self.items = []

    def add_item(self, title: str, content: str = ""):
        """添加项目"""
        item_frame = tk.Frame(self.frame, bg="white", bd=1, relief=tk.SOLID)

        header = tk.Frame(item_frame, bg="#f5f5f5", cursor="hand2")
        header.pack(fill=tk.X)

        arrow = tk.Label(header, text="▶", font=("Microsoft YaHei", 8), bg="#f5f5f5")
        arrow.pack(side=tk.LEFT, padx=5)

        title_label = tk.Label(
            header, text=title,
            font=("Microsoft YaHei", 10, "bold"),
            bg="#f5f5f5"
        )
        title_label.pack(side=tk.LEFT, pady=5)

        content_frame = tk.Frame(item_frame, bg="white")
        content_label = tk.Label(
            content_frame, text=content,
            font=("Microsoft YaHei", 9),
            bg="white", anchor="w", justify="left"
        )
        content_label.pack(padx=10, pady=5, fill=tk.X)

        is_expanded = [False]

        def toggle(e):
            if is_expanded[0]:
                content_frame.pack_forget()
                arrow.config(text="▶")
                is_expanded[0] = False
            else:
                content_frame.pack(fill=tk.X, pady=(0, 5))
                arrow.config(text="▼")
                is_expanded[0] = True

        header.bind("<Button-1>", toggle)
        title_label.bind("<Button-1>", toggle)
        arrow.bind("<Button-1>", toggle)

        item_frame.pack(fill=tk.X, pady=2)
        self.items.append(item_frame)

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)


# ==========================================
# 通知提示
# ==========================================
class ToastNotification:
    """通知提示"""

    def __init__(self, parent):
        self.parent = parent
        self.toasts = []

    def show(self, message: str, duration: int = 3000, toast_type: str = "info"):
        """显示通知"""
        colors = {
            "info": "#2196f3",
            "success": "#4caf50",
            "warning": "#ff9800",
            "error": "#f44336"
        }

        toast = tk.Toplevel(self.parent)
        toast.overrideredirect(True)

        bg_color = colors.get(toast_type, colors["info"])
        frame = tk.Frame(toast, bg=bg_color, padx=20, pady=10)
        frame.pack()

        label = tk.Label(
            frame, text=message,
            font=("Microsoft YaHei", 10),
            bg=bg_color, fg="white"
        )
        label.pack()

        # 获取父窗口位置
        try:
            x = self.parent.winfo_x() + self.parent.winfo_width() // 2 - 100
            y = self.parent.winfo_y() + 50
            toast.geometry(f"+{x}+{y}")
        except:
            toast.geometry("200x50")

        toast.after(duration, toast.destroy)


# ==========================================
# 拖拽排序列表
# ==========================================
class DragSortListbox:
    """拖拽排序列表"""

    def __init__(self, parent, items: List[str] = None):
        self.parent = parent
        self.items = items or []
        self.on_change = None

        self.frame = tk.Frame(parent, bg="white")

        self.canvas = tk.Canvas(self.frame, bg="white", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.inner_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.item_widgets = []
        self._render()

    def _render(self):
        """渲染"""
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        self.item_widgets = []

        for i, item in enumerate(self.items):
            item_frame = tk.Frame(
                self.inner_frame, bg="white", bd=1, relief=tk.SOLID,
                cursor="hand2"
            )
            item_frame.pack(fill=tk.X, pady=1)

            handle = tk.Label(
                item_frame, text="☰",
                font=("Microsoft YaHei", 10),
                bg="#e0e0e0", width=3
            )
            handle.pack(side=tk.LEFT)

            label = tk.Label(
                item_frame, text=item,
                font=("Microsoft YaHei", 10),
                bg="white", anchor="w"
            )
            label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

            item_frame.bind("<Button-1>", lambda e, idx=i: self._on_drag_start(idx))
            item_frame.bind("<B1-Motion>", self._on_drag_motion)
            item_frame.bind("<ButtonRelease-1>", self._on_drag_end)

            self.item_widgets.append(item_frame)

    def _on_drag_start(self, index: int):
        """开始拖拽"""
        self.drag_index = index

    def _on_drag_motion(self, event):
        """拖拽中"""
        pass  # 简化实现

    def _on_drag_end(self, event):
        """结束拖拽"""
        pass  # 简化实现

    def set_items(self, items: List[str]):
        """设置项目"""
        self.items = items
        self._render()

    def get_items(self) -> List[str]:
        """获取项目"""
        return self.items

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)


# ==========================================
# 倒计时组件
# ==========================================
class CountdownWidget:
    """倒计时组件"""

    def __init__(self, parent, seconds: int, on_finish: Callable = None):
        self.parent = parent
        self.seconds = seconds
        self.on_finish = on_finish
        self.remaining = seconds
        self.running = False

        self.frame = tk.Frame(parent, bg="white")

        self.label = tk.Label(
            self.frame,
            text=self._format_time(self.seconds),
            font=("Microsoft YaHei", 48, "bold"),
            bg="white", fg="#f44336"
        )
        self.label.pack()

    def _format_time(self, seconds: int) -> str:
        """格式化时间"""
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def start(self):
        """开始"""
        self.running = True
        self._tick()

    def pause(self):
        """暂停"""
        self.running = False

    def resume(self):
        """继续"""
        if not self.running:
            self.running = True
            self._tick()

    def reset(self):
        """重置"""
        self.running = False
        self.remaining = self.seconds
        self.label.config(text=self._format_time(self.remaining))

    def _tick(self):
        """计时"""
        if self.running and self.remaining > 0:
            self.remaining -= 1
            self.label.config(text=self._format_time(self.remaining))
            self.parent.after(1000, self._tick)
        elif self.remaining == 0:
            if self.on_finish:
                self.on_finish()

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)


# ==========================================
# 徽章组件
# ==========================================
class BadgeWidget:
    """徽章组件"""

    def __init__(self, parent, text: str, badge_type: str = "info"):
        self.parent = parent
        self.text = text
        self.badge_type = badge_type

        colors = {
            "info": "#2196f3",
            "success": "#4caf50",
            "warning": "#ff9800",
            "error": "#f44336",
            "primary": "#1976d2"
        }

        self.frame = tk.Label(
            self.parent, text=text,
            font=("Microsoft YaHei", 9),
            bg=colors.get(badge_type, colors["info"]),
            fg="white", padx=8, pady=2
        )

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)


# ==========================================
# 分割线
# ==========================================
class SeparatorWidget:
    """分割线"""

    def __init__(self, parent, orient: str = "horizontal", color: str = "#e0e0e0"):
        self.parent = parent

        if orient == "horizontal":
            self.frame = tk.Frame(parent, bg=color, height=1)
            self.frame.pack(fill=tk.X, pady=10)
        else:
            self.frame = tk.Frame(parent, bg=color, width=1)
            self.frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)


# ==========================================
# 空间占位
# ==========================================
class SpacerWidget:
    """空间占位"""

    def __init__(self, parent, width: int = 0, height: int = 0):
        self.parent = parent
        self.width = width
        self.height = height

        self.frame = tk.Frame(parent, width=width, height=height, bg="white")
        self.frame.pack_propagate(False)

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        """网格布局"""
        self.frame.grid(**kwargs)


# ==========================================
# 页面加载动画
# ==========================================
class LoadingWidget:
    """页面加载动画"""

    def __init__(self, parent, message: str = "加载中..."):
        self.parent = parent
        self.message = message

        self.frame = tk.Frame(parent, bg="rgba(255,255,255,0.9)")

        self.label = tk.Label(
            self.frame,
            text=message,
            font=("Microsoft YaHei", 12),
            bg="white", padx=20, pady=10
        )
        self.label.pack()

        self.loading_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.current_index = 0

    def start(self):
        """开始动画"""
        self._animate()

    def _animate(self):
        """动画"""
        if self.frame.winfo_viewable():
            self.label.config(text=f"{self.loading_chars[self.current_index]} {self.message}")
            self.current_index = (self.current_index + 1) % len(self.loading_chars)
            self.parent.after(100, self._animate)

    def stop(self):
        """停止动画"""
        self.frame.pack_forget()

    def pack(self, **kwargs):
        """打包"""
        self.frame.pack(**kwargs)



# ==========================================
# 第五部分 - 补充功能与配置
# ==========================================

# ==========================================
# 数据模型扩展
# ==========================================

@dataclass
class GradeInfo:
    """年级信息"""
    id: str = ""
    name: str = ""
    level: int = 0
    student_count: int = 0
    class_count: int = 0
    description: str = ""
    created_at: str = ""

@dataclass
class SubjectInfo:
    """科目信息"""
    id: str = ""
    name: str = ""
    code: str = ""
    teacher: str = ""
    credit: float = 0.0
    description: str = ""

@dataclass
class ScheduleInfo:
    """课程安排"""
    id: str = ""
    class_id: str = ""
    subject_id: str = ""
    weekday: int = 0
    start_time: str = ""
    end_time: str = ""
    room: str = ""

@dataclass
class MessageInfo:
    """消息信息"""
    id: str = ""
    sender_id: str = ""
    receiver_id: str = ""
    title: str = ""
    content: str = ""
    type: int = 0  # 0-系统消息 1-点名通知 2-考勤提醒 3-其他
    is_read: bool = False
    created_at: str = ""

@dataclass
class AchievementInfo:
    """成就信息"""
    id: str = ""
    name: str = ""
    description: str = ""
    icon: str = ""
    requirement: str = ""
    points: int = 0
    rarity: int = 1  # 1-普通 2-稀有 3-传说
    unlocked_at: str = ""

# ==========================================
# 枚举扩展
# ==========================================

class MessageType(Enum):
    """消息类型"""
    SYSTEM = auto()
    ATTENDANCE_NOTICE = auto()
    ATTENDANCE_REMINDER = auto()
    OTHER = auto()

class AchievementType(Enum):
    """成就类型"""
    ATTENDANCE = auto()  # 考勤成就
    DRAW = auto()        # 点名成就
    POINTS = auto()      # 积分成就
    SOCIAL = auto()      # 社交成就

class PermissionLevel(Enum):
    """权限等级"""
    ADMIN = 0
    TEACHER = 1
    STUDENT = 2
    GUEST = 3

# ==========================================
# 数据库扩展操作
# ==========================================

class ExtendedDatabaseManager(DatabaseManager):
    """扩展数据库管理器"""

    def get_student_stats(self, student_id: str) -> Dict:
        """获取学生统计数据"""
        stats = {}

        # 考勤统计
        attendance_rows = self.fetchall(
            'SELECT status, COUNT(*) as count FROM attendance_records WHERE student_id = ? GROUP BY status',
            (student_id,)
        )
        for row in attendance_rows:
            status_name = AttendanceStatus(row['status']).name
            stats[status_name] = row['count']

        # 点名统计
        draw_rows = self.fetchall(
            'SELECT COUNT(*) as total FROM draw_records WHERE winners LIKE ?',
            (f'%{student_id}%',)
        )
        stats['total_draws'] = draw_rows[0]['total'] if draw_rows else 0

        # 奖励统计
        reward_rows = self.fetchall(
            'SELECT COUNT(*) as count, SUM(points) as points FROM rewards_history WHERE student_id = ?',
            (student_id,)
        )
        stats['rewards_count'] = reward_rows[0]['count'] if reward_rows else 0
        stats['rewards_points'] = reward_rows[0]['points'] if reward_rows else 0

        # 惩罚统计
        punish_rows = self.fetchall(
            'SELECT COUNT(*) as count, SUM(points) as points FROM punishments_history WHERE student_id = ?',
            (student_id,)
        )
        stats['punishments_count'] = punish_rows[0]['count'] if punish_rows else 0
        stats['punishments_points'] = punish_rows[0]['points'] if punish_rows else 0

        return stats

    def get_class_attendance_rate(self, class_id: str, days: int = 30) -> float:
        """获取班级出勤率"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        total_rows = self.fetchall(
            'SELECT COUNT(*) as total FROM attendance_records WHERE class_id = ? AND date BETWEEN ? AND ?',
            (class_id, start_date, end_date)
        )
        total = total_rows[0]['total'] if total_rows else 0

        present_rows = self.fetchall(
            'SELECT COUNT(*) as count FROM attendance_records WHERE class_id = ? AND date BETWEEN ? AND ? AND status = ?',
            (class_id, start_date, end_date, AttendanceStatus.PRESENT.value)
        )
        present = present_rows[0]['count'] if present_rows else 0

        if total > 0:
            return round(present / total * 100, 2)
        return 0.0

    def search_students_advanced(self, keyword: str, class_id: str = None,
                                min_points: int = None, max_points: int = None,
                                min_attendance: float = None) -> List[Student]:
        """高级搜索学生"""
        conditions = []
        params = []

        if keyword:
            conditions.append("(name LIKE ? OR number LIKE ? OR phone LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

        if class_id:
            conditions.append("s.id IN (SELECT student_id FROM class_students WHERE class_id = ?)")
            params.append(class_id)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        sql = f'''
            SELECT DISTINCT s.* FROM students s
            LEFT JOIN class_students cs ON s.id = cs.student_id
            WHERE {where_clause}
            ORDER BY s.name
        '''

        rows = self.fetchall(sql, tuple(params))
        return [StudentManager(self)._row_to_student(row) for row in rows]

    def get_popular_students(self, limit: int = 10) -> List[Dict]:
        """获取热门学生（被点名最多的）"""
        rows = self.fetchall('''
            SELECT student_id, COUNT(*) as draw_count
            FROM (
                SELECT json_extract(value, '$.id') as student_id
                FROM draw_records, json_each(winners)
            )
            GROUP BY student_id
            ORDER BY draw_count DESC
            LIMIT ?
        ''', (limit,))

        results = []
        for row in rows:
            student = self.fetchone('SELECT * FROM students WHERE id = ?', (row['student_id'],))
            if student:
                results.append({
                    'student': dict(student),
                    'draw_count': row['draw_count']
                })

        return results

    def get_inactive_students(self, days: int = 30) -> List[Student]:
        """获取长期未被点名的学生"""
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        rows = self.fetchall('''
            SELECT * FROM students
            WHERE last_draw_time IS NULL OR last_draw_time < ?
            ORDER BY last_draw_time
        ''', (cutoff_date,))

        return [StudentManager(self)._row_to_student(row) for row in rows]

# ==========================================
# 报表生成扩展
# ==========================================

class ReportGenerator:
    """报表生成器"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.chart_generator = ChartGenerator()
        self.pdf_generator = PDFGenerator()
        self.excel_exporter = ExcelExporter()

    def generate_daily_attendance_report(self, class_id: str, date: str) -> Dict:
        """生成每日考勤报表"""
        records = self.db.fetchall(
            'SELECT * FROM attendance_records WHERE class_id = ? AND date = ? ORDER BY student_name',
            (class_id, date)
        )

        stats = {
            'total': len(records),
            'present': 0,
            'absent': 0,
            'late': 0,
            'leave': 0
        }

        present_list = []
        absent_list = []
        late_list = []
        leave_list = []

        for row in records:
            status = row['status']
            student_info = {
                'name': row['student_name'],
                'time': row['check_in_time'],
                'note': row['note']
            }

            if status == AttendanceStatus.PRESENT.value:
                stats['present'] += 1
                present_list.append(student_info)
            elif status == AttendanceStatus.ABSENT.value:
                stats['absent'] += 1
                absent_list.append(student_info)
            elif status == AttendanceStatus.LATE.value:
                stats['late'] += 1
                late_list.append(student_info)
            elif status == AttendanceStatus.LEAVE.value:
                stats['leave'] += 1
                leave_list.append(student_info)

        return {
            'date': date,
            'stats': stats,
            'present': present_list,
            'absent': absent_list,
            'late': late_list,
            'leave': leave_list
        }

    def generate_weekly_report(self, class_id: str) -> Dict:
        """生成周报"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        daily_reports = []
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            report = self.generate_daily_attendance_report(class_id, date_str)
            daily_reports.append(report)
            current_date += timedelta(days=1)

        # 计算周统计
        total_present = sum(r['stats']['present'] for r in daily_reports)
        total_absent = sum(r['stats']['absent'] for r in daily_reports)
        total_late = sum(r['stats']['late'] for r in daily_reports)
        total_leave = sum(r['stats']['leave'] for r in daily_reports)
        total = total_present + total_absent + total_late + total_leave

        return {
            'start_date': start_date.strftime("%Y-%m-%d"),
            'end_date': end_date.strftime("%Y-%m-%d"),
            'daily_reports': daily_reports,
            'weekly_stats': {
                'total': total,
                'present': total_present,
                'absent': total_absent,
                'late': total_late,
                'leave': total_leave,
                'attendance_rate': round(total_present / total * 100, 2) if total > 0 else 0
            }
        }

    def generate_monthly_report(self, class_id: str, year: int, month: int) -> Dict:
        """生成月报"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)

        # 获取班级信息
        class_info = self.db.fetchone('SELECT * FROM classes WHERE id = ?', (class_id,))

        # 获取学生名单
        student_ids = self.db.fetchall(
            'SELECT student_id FROM class_students WHERE class_id = ?',
            (class_id,)
        )
        total_students = len(student_ids)

        # 获取该月考勤记录
        records = self.db.fetchall(
            'SELECT * FROM attendance_records WHERE class_id = ? AND date BETWEEN ? AND ?',
            (class_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        )

        # 统计
        stats = defaultdict(lambda: {'present': 0, 'absent': 0, 'late': 0, 'leave': 0})
        student_stats = defaultdict(lambda: {'present': 0, 'absent': 0, 'late': 0, 'leave': 0})

        for record in records:
            date = record['date']
            student_id = record['student_id']
            status = record['status']

            if status == AttendanceStatus.PRESENT.value:
                stats[date]['present'] += 1
                student_stats[student_id]['present'] += 1
            elif status == AttendanceStatus.ABSENT.value:
                stats[date]['absent'] += 1
                student_stats[student_id]['absent'] += 1
            elif status == AttendanceStatus.LATE.value:
                stats[date]['late'] += 1
                student_stats[student_id]['late'] += 1
            elif status == AttendanceStatus.LEAVE.value:
                stats[date]['leave'] += 1
                student_stats[student_id]['leave'] += 1

        return {
            'year': year,
            'month': month,
            'class': dict(class_info) if class_info else {},
            'total_students': total_students,
            'working_days': len(stats),
            'daily_stats': dict(stats),
            'student_stats': dict(student_stats)
        }

    def generate_student_report(self, student_id: str) -> Dict:
        """生成学生个人报告"""
        student = self.db.fetchone('SELECT * FROM students WHERE id = ?', (student_id,))
        if not student:
            return {}

        # 考勤记录
        attendance_records = self.db.fetchall(
            'SELECT * FROM attendance_records WHERE student_id = ? ORDER BY date DESC LIMIT 100',
            (student_id,)
        )

        # 点名记录
        draw_records = self.db.fetchall(
            'SELECT * FROM draw_records ORDER BY created_at DESC LIMIT 50',
        )

        # 奖励记录
        reward_records = self.db.fetchall(
            'SELECT * FROM rewards_history WHERE student_id = ? ORDER BY created_at DESC',
            (student_id,)
        )

        # 惩罚记录
        punish_records = self.db.fetchall(
            'SELECT * FROM punishments_history WHERE student_id = ? ORDER BY created_at DESC',
            (student_id,)
        )

        # 统计
        attendance_stats = defaultdict(int)
        for record in attendance_records:
            attendance_stats[record['status']] += 1

        return {
            'student': dict(student),
            'attendance': {
                'records': [dict(r) for r in attendance_records],
                'stats': dict(attendance_stats)
            },
            'draw_records': [dict(r) for r in draw_records],
            'rewards': [dict(r) for r in reward_records],
            'punishments': [dict(r) for r in punish_records]
        }

    def export_report_to_pdf(self, report: Dict, filename: str) -> Optional[str]:
        """导出报表为PDF"""
        return self.pdf_generator.generate_attendance_report(report, filename)

    def export_report_to_excel(self, report: Dict, filename: str) -> Optional[str]:
        """导出报表为Excel"""
        return self.excel_exporter.export_attendance_report(
            [AttendanceRecord(**r) for r in report.get('attendance', {}).get('records', [])],
            report.get('stats', {}),
            filename
        )

    def generate_attendance_chart(self, class_id: str, days: int = 30) -> Optional[str]:
        """生成考勤图表"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        rows = self.db.fetchall('''
            SELECT date,
                   SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) as present,
                   SUM(CASE WHEN status = 2 THEN 1 ELSE 0 END) as absent,
                   SUM(CASE WHEN status = 3 THEN 1 ELSE 0 END) as late,
                   SUM(CASE WHEN status = 4 THEN 1 ELSE 0 END) as leave
            FROM attendance_records
            WHERE class_id = ? AND date BETWEEN ? AND ?
            GROUP BY date
            ORDER BY date
        ''', (class_id, start_date, end_date))

        dates = []
        present = []
        absent = []
        late = []
        leave = []

        for row in rows:
            dates.append(row['date'])
            present.append(row['present'])
            absent.append(row['absent'])
            late.append(row['late'])
            leave.append(row['leave'])

        data = {
            'dates': dates,
            '出勤': present,
            '缺勤': absent,
            '迟到': late,
            '请假': leave
        }

        return self.chart_generator.generate_line_chart(data, title="近30天考勤趋势")

# ==========================================
# 数据同步管理器
# ==========================================

class SyncManager:
    """数据同步管理器"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.sync_server = None
        self.last_sync_time = None

    def sync_to_cloud(self, server_url: str, api_key: str) -> bool:
        """同步到云端"""
        try:
            # 准备数据
            data = {
                'students': [s.to_dict() for s in StudentManager(self.db).get_all_students()],
                'classes': [c.to_dict() for c in ClassManager(self.db).get_all_classes()],
                'timestamp': datetime.now().isoformat()
            }

            # 发送到服务器
            response = NetworkUtils.post_json(
                f"{server_url}/api/sync",
                data=data,
                headers={'Authorization': f'Bearer {api_key}'}
            )

            if response:
                self.last_sync_time = datetime.now()
                return True

            return False
        except Exception as e:
            print(f"[错误] 云端同步失败: {e}")
            return False

    def sync_from_cloud(self, server_url: str, api_key: str) -> bool:
        """从云端同步"""
        try:
            response = NetworkUtils.get_json(
                f"{server_url}/api/sync",
                headers={'Authorization': f'Bearer {api_key}'}
            )

            if response and 'data' in response:
                data = response['data']

                # 导入学生
                for student_dict in data.get('students', []):
                    student = Student(**student_dict)
                    StudentManager(self.db).add_student(student)

                # 导入班级
                for class_dict in data.get('classes', []):
                    class_info = ClassInfo(**class_dict)
                    ClassManager(self.db).add_class(class_info)

                self.last_sync_time = datetime.now()
                return True

            return False
        except Exception as e:
            print(f"[错误] 云端同步失败: {e}")
            return False

    def create_sync_package(self) -> str:
        """创建同步包"""
        data = {
            'version': VERSION,
            'created_at': datetime.now().isoformat(),
            'students': [s.to_dict() for s in StudentManager(self.db).get_all_students()],
            'classes': [c.to_dict() for c in ClassManager(self.db).get_all_classes()],
            'settings': ConfigManager().config
        }

        package_path = os.path.join(BACKUP_DIR, f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

        with open(package_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return package_path

    def import_sync_package(self, package_path: str) -> bool:
        """导入同步包"""
        try:
            with open(package_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 导入学生
            for student_dict in data.get('students', []):
                student = Student(**student_dict)
                StudentManager(self.db).add_student(student)

            # 导入班级
            for class_dict in data.get('classes', []):
                class_info = ClassInfo(**class_dict)
                ClassManager(self.db).add_class(class_info)

            # 更新设置
            if 'settings' in data:
                ConfigManager().config.update(data['settings'])
                ConfigManager().save_config()

            return True
        except Exception as e:
            print(f"[错误] 导入同步包失败: {e}")
            return False

# ==========================================
# 权限管理器
# ==========================================

class PermissionManager:
    """权限管理器"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self._create_table()

    def _create_table(self):
        """创建权限表"""
        sql = """
        CREATE TABLE IF NOT EXISTS permissions (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            user_type TEXT,
            permissions TEXT,
            created_at TEXT
        )
        """
        self.db.execute(sql)
        self.db.commit()

    def check_permission(self, user_id: str, permission: str) -> bool:
        """检查权限"""
        row = self.db.fetchone(
            'SELECT permissions FROM permissions WHERE user_id = ?',
            (user_id,)
        )

        if row and row['permissions']:
            permissions = json.loads(row['permissions'])
            return permission in permissions

        return False

    def grant_permission(self, user_id: str, permissions: List[str]):
        """授予权限"""
        data = {
            'id': generate_unique_id(),
            'user_id': user_id,
            'permissions': json.dumps(permissions),
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.db.insert('permissions', data)

    def revoke_permission(self, user_id: str, permission: str):
        """撤销权限"""
        row = self.db.fetchone(
            'SELECT permissions FROM permissions WHERE user_id = ?',
            (user_id,)
        )

        if row and row['permissions']:
            permissions = json.loads(row['permissions'])
            if permission in permissions:
                permissions.remove(permission)
                self.db.update(
                    'permissions',
                    {'permissions': json.dumps(permissions)},
                    'user_id = ?',
                    (user_id,)
                )

# ==========================================
# 成就系统
# ==========================================

class AchievementSystem:
    """成就系统"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.achievements = self._load_achievements()

    def _load_achievements(self) -> List[Dict]:
        """加载成就列表"""
        default_achievements = [
            {
                'id': 'first_draw',
                'name': '初次点名',
                'description': '完成第一次点名',
                'icon': '🎯',
                'requirement': 'draw_count >= 1',
                'points': 10
            },
            {
                'id': 'draw_10',
                'name': '点名达人',
                'description': '点名次数达到10次',
                'icon': '🏆',
                'requirement': 'draw_count >= 10',
                'points': 50
            },
            {
                'id': 'draw_100',
                'name': '点名狂人',
                'description': '点名次数达到100次',
                'icon': '💫',
                'requirement': 'draw_count >= 100',
                'points': 200
            },
            {
                'id': 'perfect_attendance',
                'name': '全勤之星',
                'description': '连续一周全勤',
                'icon': '⭐',
                'requirement': 'attendance_rate >= 100',
                'points': 100
            },
            {
                'id': 'class_manager',
                'name': '班级管理者',
                'description': '管理3个以上班级',
                'icon': '👔',
                'requirement': 'class_count >= 3',
                'points': 150
            }
        ]

        return default_achievements

    def check_achievements(self, student_id: str) -> List[Dict]:
        """检查成就"""
        student = self.db.fetchone('SELECT * FROM students WHERE id = ?', (student_id,))
        if not student:
            return []

        unlocked = []

        for achievement in self.achievements:
            # 检查是否已解锁
            existing = self.db.fetchone(
                'SELECT * FROM achievements WHERE student_id = ? AND achievement_id = ?',
                (student_id, achievement['id'])
            )

            if existing:
                continue

            # 检查是否满足条件
            if self._check_requirement(student, achievement['requirement']):
                # 解锁成就
                self._unlock_achievement(student_id, achievement)
                unlocked.append(achievement)

        return unlocked

    def _check_requirement(self, student: Dict, requirement: str) -> bool:
        """检查条件"""
        # 简化实现
        try:
            student_dict = dict(student)
            return eval(requirement, {"__builtins__": {}}, student_dict)
        except:
            return False

    def _unlock_achievement(self, student_id: str, achievement: Dict):
        """解锁成就"""
        data = {
            'id': generate_unique_id(),
            'student_id': student_id,
            'achievement_id': achievement['id'],
            'unlocked_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.db.insert('achievements', data)

        # 奖励积分
        self.db.update(
            'students',
            {'points': f'points + {achievement["points"]}'},
            'id = ?',
            (student_id,)
        )

    def get_student_achievements(self, student_id: str) -> List[Dict]:
        """获取学生成就"""
        rows = self.db.fetchall(
            '''
            SELECT a.*, ach.name, ach.description, ach.icon, ach.points
            FROM achievements a
            JOIN achievement_list ach ON a.achievement_id = ach.id
            WHERE a.student_id = ?
            ORDER BY a.unlocked_at DESC
            ''',
            (student_id,)
        )
        return [dict(row) for row in rows]

# ==========================================
# 提醒系统
# ==========================================

class ReminderManager:
    """提醒管理器"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self._create_table()
        self.reminders = []
        self.running = False

    def _create_table(self):
        """创建提醒表"""
        sql = """
        CREATE TABLE IF NOT EXISTS reminders (
            id TEXT PRIMARY KEY,
            title TEXT,
            content TEXT,
            remind_time TEXT,
            repeat_type TEXT,
            status INTEGER DEFAULT 0,
            created_at TEXT
        )
        """
        self.db.execute(sql)
        self.db.commit()

    def add_reminder(self, title: str, content: str, remind_time: str, repeat_type: str = "once") -> str:
        """添加提醒"""
        reminder_id = generate_unique_id()
        data = {
            'id': reminder_id,
            'title': title,
            'content': content,
            'remind_time': remind_time,
            'repeat_type': repeat_type,
            'status': 0,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.db.insert('reminders', data)
        return reminder_id

    def get_reminders(self, pending: bool = True) -> List[Dict]:
        """获取提醒列表"""
        if pending:
            return [dict(row) for row in self.db.fetchall(
                'SELECT * FROM reminders WHERE status = 0 ORDER BY remind_time'
            )]
        else:
            return [dict(row) for row in self.db.fetchall(
                'SELECT * FROM reminders ORDER BY remind_time'
            )]

    def start_reminder_service(self, on_remind: Callable = None):
        """启动提醒服务"""
        self.running = True
        self._check_reminders(on_remind)

    def stop_reminder_service(self):
        """停止提醒服务"""
        self.running = False

    def _check_reminders(self, on_remind: Callable = None):
        """检查提醒"""
        if not self.running:
            return

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        reminders = self.db.fetchall(
            'SELECT * FROM reminders WHERE status = 0 AND remind_time <= ?',
            (current_time,)
        )

        for reminder in reminders:
            if on_remind:
                on_remind(dict(reminder))

            # 更新状态
            self.db.update('reminders', {'status': 1}, 'id = ?', (reminder['id'],))

        # 每分钟检查一次
        threading.Timer(60, lambda: self._check_reminders(on_remind)).start()

# ==========================================
# 模板系统
# ==========================================

class TemplateManager:
    """模板管理器"""

    def __init__(self):
        self.templates_dir = os.path.join(BASE_DIR, "templates")
        os.makedirs(self.templates_dir, exist_ok=True)
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict:
        """加载模板"""
        templates = {
            'attendance_report': self._get_attendance_report_template(),
            'student_report': self._get_student_report_template(),
            'class_summary': self._get_class_summary_template(),
            'draw_result': self._get_draw_result_template(),
            'notification': self._get_notification_template()
        }

        return templates

    def _get_attendance_report_template(self) -> str:
        """考勤报表模板"""
        return """
【考勤报表】

班级：{class_name}
日期：{date}
年级：{grade}

━━━━━━━━━━━━━━━━━━━━
统计信息
━━━━━━━━━━━━━━━━━━━━
应到人数：{total}
实到人数：{present}
出勤率：{rate}%

出勤：{present}人
缺勤：{absent}人
迟到：{late}人
请假：{leave}人

━━━━━━━━━━━━━━━━━━━━
详细记录
━━━━━━━━━━━━━━━━━━━━
{records}

生成时间：{generated_at}
        """

    def _get_student_report_template(self) -> str:
        """学生报告模板"""
        return """
【学生报告】

姓名：{name}
学号：{number}
班级：{class_name}

━━━━━━━━━━━━━━━━━━━━
基本信息
━━━━━━━━━━━━━━━━━━━━
性别：{gender}
电话：{phone}
邮箱：{email}

━━━━━━━━━━━━━━━━━━━━
统计数据
━━━━━━━━━━━━━━━━━━━━
积分：{points}
星星：{stars}
出勤率：{attendance_rate}%
点名次数：{draw_count}

━━━━━━━━━━━━━━━━━━━━
最近奖励
━━━━━━━━━━━━━━━━━━━━
{rewards}

━━━━━━━━━━━━━━━━━━━━
最近惩罚
━━━━━━━━━━━━━━━━━━━━
{punishments}

生成时间：{generated_at}
        """

    def _get_class_summary_template(self) -> str:
        """班级汇总模板"""
        return """
【班级汇总】

班级：{class_name}
年级：{grade}
人数：{student_count}

━━━━━━━━━━━━━━━━━━━━
本周考勤
━━━━━━━━━━━━━━━━━━━━
出勤率：{attendance_rate}%
最佳出勤日：{best_day}
需要关注：{attention_needed}

━━━━━━━━━━━━━━━━━━━━
点名统计
━━━━━━━━━━━━━━━━━━━━
本周点名次数：{draw_count}
被点名最多：{most_drawn}
近期未点名：{not_drawn}
        """

    def _get_draw_result_template(self) -> str:
        """点名结果模板"""
        return """
【点名结果】

班级：{class_name}
时间：{time}
模式：{mode}

━━━━━━━━━━━━━━━━━━━━
本次点名
━━━━━━━━━━━━━━━━━━━━
抽取人数：{count}

恭喜以下同学：
{winners}

━━━━━━━━━━━━━━━━━━━━
历史统计
━━━━━━━━━━━━━━━━━━━━
总点名次数：{total_draws}
您的点名次数：{your_draws}
        """

    def _get_notification_template(self) -> str:
        """通知模板"""
        return """
【{title}】

{content}

发送时间：{sent_at}
        """

    def render(self, template_name: str, **kwargs) -> str:
        """渲染模板"""
        template = self.templates.get(template_name, "")
        try:
            return template.format(**kwargs)
        except:
            return template

    def save_template(self, name: str, content: str):
        """保存模板"""
        filepath = os.path.join(self.templates_dir, f"{name}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def load_template(self, name: str) -> str:
        """加载模板"""
        filepath = os.path.join(self.templates_dir, f"{name}.txt")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

# ==========================================
# 快捷操作
# ==========================================

class QuickActionManager:
    """快捷操作管理器"""

    def __init__(self):
        self.actions_file = os.path.join(DATA_DIR, "quick_actions.json")
        self.actions = self._load_actions()

    def _load_actions(self) -> Dict:
        """加载快捷操作"""
        if os.path.exists(self.actions_file):
            try:
                with open(self.actions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass

        return {
            'draw': {'name': '快速点名', 'icon': '🎯', 'shortcut': 'F5'},
            'attendance': {'name': '一键考勤', 'icon': '✅', 'shortcut': 'F6'},
            'export': {'name': '导出数据', 'icon': '📤', 'shortcut': 'F7'},
            'backup': {'name': '创建备份', 'icon': '💾', 'shortcut': 'F8'},
            'settings': {'name': '系统设置', 'icon': '⚙️', 'shortcut': 'F9'}
        }

    def save_actions(self):
        """保存快捷操作"""
        with open(self.actions_file, 'w', encoding='utf-8') as f:
            json.dump(self.actions, f, ensure_ascii=False, indent=2)

    def get_action(self, key: str) -> Optional[Dict]:
        """获取操作"""
        return self.actions.get(key)

    def add_action(self, key: str, name: str, icon: str = "", shortcut: str = ""):
        """添加操作"""
        self.actions[key] = {'name': name, 'icon': icon, 'shortcut': shortcut}
        self.save_actions()

    def remove_action(self, key: str):
        """移除操作"""
        if key in self.actions:
            del self.actions[key]
            self.save_actions()

# ==========================================
# 版本检查器
# ==========================================

class VersionChecker:
    """版本检查器"""

    def __init__(self):
        self.github_api = "https://api.github.com/repos/YuYuCong/SmartPicker/releases/latest"

    def check_update(self) -> Tuple[bool, Dict]:
        """检查更新"""
        try:
            response = NetworkUtils.get_json(self.github_api)
            if response:
                latest_version = response.get('tag_name', '').lstrip('v')
                if self._compare_versions(latest_version, VERSION) > 0:
                    return True, {
                        'version': latest_version,
                        'name': response.get('name', ''),
                        'body': response.get('body', ''),
                        'html_url': response.get('html_url', ''),
                        'published_at': response.get('published_at', '')
                    }
        except:
            pass

        return False, {}

    def _compare_versions(self, v1: str, v2: str) -> int:
        """比较版本"""
        def parse(v):
            return [int(x) for x in v.split('.')[:3]]

        p1, p2 = parse(v1), parse(v2)
        for i in range(max(len(p1), len(p2))):
            n1, n2 = p1[i] if i < len(p1) else 0, p2[i] if i < len(p2) else 0
            if n1 > n2:
                return 1
            if n1 < n2:
                return -1
        return 0

# ==========================================
# 帮助文档生成器
# ==========================================

class HelpDocumentGenerator:
    """帮助文档生成器"""

    def __init__(self):
        self.doc_dir = os.path.join(BASE_DIR, "docs")
        os.makedirs(self.doc_dir, exist_ok=True)

    def generate_help_document(self) -> str:
        """生成帮助文档"""
        content = f"""
# {APP_NAME} 帮助文档

版本：{VERSION}
作者：{AUTHOR}

## 功能介绍

{APP_NAME} 是一款功能强大的课堂点名系统，主要功能包括：

### 1. 随机点名
- 支持多种抽取模式（普通、加权、随机、分组等）
- 实时滚动动画效果
- 语音播报功能
- 自定义抽取人数

### 2. 学生管理
- 添加、编辑、删除学生信息
- 批量导入/导出学生
- 学生档案管理
- 积分和星星系统

### 3. 班级管理
- 多班级支持
- 班级学生分配
- 座位管理
- 课程安排

### 4. 考勤系统
- 快速考勤
- 出勤统计
- 考勤报表
- 导出功能

### 5. 数据统计
- 出勤率分析
- 点名历史
- 学生排名
- 图表展示

## 使用指南

### 快捷键
- 空格键：开始/停止点名
- R 键：重置
- ESC 键：退出程序

### 数据导入
支持以下格式导入学生数据：
- CSV 文件
- Excel 文件 (.xlsx, .xls)
- JSON 文件
- 纯文本文件（每行一个姓名）

### 数据备份
程序支持自动备份和手动备份，确保数据安全。

## 常见问题

### Q: 如何添加学生？
A: 点击左侧菜单"学生管理"，然后点击"添加"按钮。

### Q: 如何切换班级？
A: 在点名页面，点击班级下拉框选择班级。

### Q: 如何重置学生权重？
A: 点击"重置权重"按钮即可将所有学生权重恢复为默认值。

### Q: 如何更改界面主题？
A: 进入"设置"页面，选择喜欢的主题即可。

## 联系方式

如有问题或建议，请联系作者：{AUTHOR}

---
文档更新时间：{datetime.now().strftime('%Y-%m-%d')}
        """

        filepath = os.path.join(self.doc_dir, "help.md")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

# ==========================================
# 最终导出
# ==========================================

__all__ = [
    # 核心管理器
    'DatabaseManager', 'StudentManager', 'ClassManager', 'AttendanceManager',
    'DrawRecordManager', 'RewardManager', 'BackupManager', 'ImportExportManager',
    'StatisticsAnalyzer', 'ReportGenerator', 'SyncManager', 'PermissionManager',
    'AchievementSystem', 'ReminderManager', 'TemplateManager', 'QuickActionManager',
    'VersionChecker', 'HelpDocumentGenerator',

    # UI组件
    'AdvancedDialogs', 'TableWidget', 'CardWidget', 'TabWidget', 'ProgressWidget',
    'SearchBox', 'PaginationWidget', 'RatingWidget', 'TagInputWidget', 'RichTextEditor',
    'CalendarWidget', 'TimePickerWidget', 'AvatarUploadWidget', 'CarouselWidget',
    'StepIndicatorWidget', 'AccordionWidget', 'ToastNotification', 'DragSortListbox',
    'CountdownWidget', 'BadgeWidget', 'SeparatorWidget', 'SpacerWidget', 'LoadingWidget',

    # 工具类
    'ChartGenerator', 'PDFGenerator', 'ExcelExporter', 'NetworkUtils',
    'SystemInfo', 'FileUtils', 'DateTimeUtils', 'StringUtils', 'ListUtils',
    'MathUtils', 'Validator', 'CryptoUtils', 'CacheManager', 'EventManager',

    # 数据模型
    'Student', 'ClassInfo', 'AttendanceRecord', 'DrawRecord', 'SeatInfo',
    'GradeInfo', 'SubjectInfo', 'ScheduleInfo', 'MessageInfo', 'AchievementInfo',

    # 枚举
    'DrawMode', 'AttendanceStatus', 'StudentState', 'RewardType', 'PunishmentType',
    'MessageType', 'AchievementType', 'PermissionLevel',

    # 辅助函数
    'generate_unique_id', 'safe_after_call', 'AdvancedDatabaseManager',

    # 常量
    'VERSION', 'APP_NAME', 'AUTHOR', 'BASE_DIR', 'DATA_DIR', 'THEMES', 'LANGUAGE_PACKS'
]


# ==========================================
# 成绩管理系统
# ==========================================

class GradeManager:
    """成绩管理系统"""
    
    def __init__(self):
        self.grades = {}  # student_id -> {subject_id -> score}
        self.grade_config = {
            'excellent_threshold': 90,
            'good_threshold': 80,
            'pass_threshold': 60,
        }
    
    def record_score(self, student_id: str, subject_id: str, score: float) -> bool:
        """记录成绩"""
        if student_id not in self.grades:
            self.grades[student_id] = {}
        self.grades[student_id][subject_id] = score
        return True
    
    def get_score(self, student_id: str, subject_id: str) -> float:
        """获取成绩"""
        return self.grades.get(student_id, {}).get(subject_id, 0.0)
    
    def get_average(self, student_id: str) -> float:
        """获取平均分"""
        if student_id not in self.grades or not self.grades[student_id]:
            return 0.0
        scores = list(self.grades[student_id].values())
        return sum(scores) / len(scores)
    
    def get_ranking(self, student_id: str) -> int:
        """获取排名"""
        averages = [(sid, self.get_average(sid)) for sid in self.grades]
        averages.sort(key=lambda x: x[1], reverse=True)
        for i, (sid, _) in enumerate(averages):
            if sid == student_id:
                return i + 1
        return len(averages)
    
    def get_grade_level(self, score: float) -> str:
        """获取等级"""
        if score >= self.grade_config['excellent_threshold']:
            return "优秀"
        elif score >= self.grade_config['good_threshold']:
            return "良好"
        elif score >= self.grade_config['pass_threshold']:
            return "及格"
        else:
            return "不及格"
    
    def export_report(self, student_id: str) -> str:
        """导出成绩报告"""
        if student_id not in self.grades:
            return ""
        report = f"成绩报告 - {student_id}\n"
        report += "=" * 40 + "\n"
        for subject, score in self.grades[student_id].items():
            level = self.get_grade_level(score)
            report += f"{subject}: {score:.1f} ({level})\n"
        report += f"平均分: {self.get_average(student_id):.1f}\n"
        report += f"排名: {self.get_ranking(student_id)}\n"
        return report


# ==========================================
# 考勤管理系统
# ==========================================

class AttendanceStatus(Enum):
    """考勤状态"""
    PRESENT = "present"      # 正常出勤
    ABSENT = "absent"        # 缺勤
    LATE = "late"            # 迟到
    LEAVE_EARLY = "leave_early"  # 早退
    SICK_LEAVE = "sick_leave"    # 病假
    PERSONAL_LEAVE = "personal_leave"  # 事假
    OFFICIAL_LEAVE = "official_leave"  # 公假

@dataclass
class AttendanceRecord:
    """考勤记录"""
    student_id: str
    date: str
    status: AttendanceStatus
    check_in_time: str = ""
    check_out_time: str = ""
    remark: str = ""
    recorded_by: str = ""


class AttendanceManager:
    """考勤管理器"""
    
    def __init__(self):
        self.records: List[AttendanceRecord] = []
        self.auto_late_threshold = "09:00"
        self.auto_leave_early_threshold = "16:30"
    
    def check_in(self, student_id: str, date: str, time: str) -> bool:
        """签到"""
        if time > self.auto_late_threshold:
            status = AttendanceStatus.LATE
        else:
            status = AttendanceStatus.PRESENT
        
        record = AttendanceRecord(
            student_id=student_id,
            date=date,
            status=status,
            check_in_time=time
        )
        self.records.append(record)
        return True
    
    def check_out(self, student_id: str, date: str, time: str) -> bool:
        """签退"""
        for record in self.records:
            if record.student_id == student_id and record.date == date:
                record.check_out_time = time
                if time < self.auto_leave_early_threshold:
                    record.status = AttendanceStatus.LEAVE_EARLY
                return True
        return False
    
    def apply_leave(self, student_id: str, date: str, leave_type: str, reason: str) -> bool:
        """请假申请"""
        if leave_type == "sick":
            status = AttendanceStatus.SICK_LEAVE
        elif leave_type == "personal":
            status = AttendanceStatus.PERSONAL_LEAVE
        else:
            status = AttendanceStatus.OFFICIAL_LEAVE
        
        record = AttendanceRecord(
            student_id=student_id,
            date=date,
            status=status,
            remark=reason
        )
        self.records.append(record)
        return True
    
    def get_attendance_rate(self, student_id: str) -> float:
        """获取出勤率"""
        student_records = [r for r in self.records if r.student_id == student_id]
        if not student_records:
            return 100.0
        present_count = sum(1 for r in student_records 
                           if r.status == AttendanceStatus.PRESENT)
        return (present_count / len(student_records)) * 100
    
    def get_monthly_report(self, date: str) -> Dict:
        """月度考勤报告"""
        month_records = [r for r in self.records if r.date.startswith(date[:7])]
        stats = {
            'total': len(month_records),
            'present': sum(1 for r in month_records if r.status == AttendanceStatus.PRESENT),
            'absent': sum(1 for r in month_records if r.status == AttendanceStatus.ABSENT),
            'late': sum(1 for r in month_records if r.status == AttendanceStatus.LATE),
            'leave_early': sum(1 for r in month_records if r.status == AttendanceStatus.LEAVE_EARLY),
            'sick_leave': sum(1 for r in month_records if r.status == AttendanceStatus.SICK_LEAVE),
            'personal_leave': sum(1 for r in month_records if r.status == AttendanceStatus.PERSONAL_LEAVE),
        }
        stats['attendance_rate'] = (stats['present'] / stats['total'] * 100) if stats['total'] > 0 else 100
        return stats


# ==========================================
# 作业管理系统
# ==========================================

class HomeworkStatus(Enum):
    """作业状态"""
    NOT_SUBMITTED = "not_submitted"
    SUBMITTED = "submitted"
    LATE = "late"
    GRADED = "graded"

@dataclass
class Homework:
    """作业"""
    id: str
    title: str
    subject: str
    description: str
    deadline: str
    created_by: str
    created_at: str
    max_score: float = 100.0
    attachment: str = ""

@dataclass
class HomeworkSubmission:
    """作业提交"""
    homework_id: str
    student_id: str
    content: str
    attachment: str = ""
    submitted_at: str = ""
    status: HomeworkStatus = HomeworkStatus.SUBMITTED
    score: float = 0.0
    feedback: str = ""


class HomeworkManager:
    """作业管理器"""
    
    def __init__(self):
        self.homeworks: Dict[str, Homework] = {}
        self.submissions: Dict[str, List[HomeworkSubmission]] = {}  # homework_id -> submissions
        self.next_id = 1
    
    def create_homework(self, title: str, subject: str, description: str, 
                       deadline: str, created_by: str) -> str:
        """创建作业"""
        homework_id = f"HW{self.next_id:04d}"
        self.next_id += 1
        
        homework = Homework(
            id=homework_id,
            title=title,
            subject=subject,
            description=description,
            deadline=deadline,
            created_by=created_by,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.homeworks[homework_id] = homework
        self.submissions[homework_id] = []
        return homework_id
    
    def submit_homework(self, homework_id: str, student_id: str, 
                       content: str, attachment: str = "") -> bool:
        """提交作业"""
        if homework_id not in self.homeworks:
            return False
        
        submission = HomeworkSubmission(
            homework_id=homework_id,
            student_id=student_id,
            content=content,
            attachment=attachment,
            submitted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # 检查是否迟到
        homework = self.homeworks[homework_id]
        if submission.submitted_at > homework.deadline:
            submission.status = HomeworkStatus.LATE
        
        self.submissions[homework_id].append(submission)
        return True
    
    def grade_homework(self, homework_id: str, student_id: str, 
                      score: float, feedback: str) -> bool:
        """批改作业"""
        if homework_id not in self.submissions:
            return False
        
        for submission in self.submissions[homework_id]:
            if submission.student_id == student_id:
                submission.score = score
                submission.feedback = feedback
                submission.status = HomeworkStatus.GRADED
                return True
        return False
    
    def get_homework_stats(self, homework_id: str) -> Dict:
        """获取作业统计"""
        if homework_id not in self.submissions:
            return {}
        
        submissions = self.submissions[homework_id]
        scores = [s.score for s in submissions if s.status == HomeworkStatus.GRADED]
        
        return {
            'total_submissions': len(submissions),
            'graded_count': len(scores),
            'average_score': sum(scores) / len(scores) if scores else 0,
            'max_score': max(scores) if scores else 0,
            'min_score': min(scores) if scores else 0,
        }


# ==========================================
# 通知公告系统
# ==========================================

class NoticeType(Enum):
    """通知类型"""
    SYSTEM = "system"
    HOMEWORK = "homework"
    EXAM = "exam"
    ACTIVITY = "activity"
    ANNOUNCEMENT = "announcement"

@dataclass
class Notice:
    """通知公告"""
    id: str
    title: str
    content: str
    notice_type: NoticeType
    priority: int  # 1-5, 5最高
    target_audience: List[str]  # 年级/班级/个人
    attachment: List[str] = field(default_factory=list)
    created_by: str = ""
    created_at: str = ""
    valid_from: str = ""
    valid_until: str = ""
    view_count: int = 0
    is_pinned: bool = False


class NoticeBoard:
    """公告板"""
    
    def __init__(self):
        self.notices: Dict[str, Notice] = {}
        self.next_id = 1
        self.subscribers: Dict[str, List[str]] = {}  # user_id -> notice_types
    
    def publish_notice(self, title: str, content: str, notice_type: NoticeType,
                      priority: int, target_audience: List[str],
                      created_by: str, valid_from: str = "", valid_until: str = "") -> str:
        """发布通知"""
        notice_id = f"N{self.next_id:05d}"
        self.next_id += 1
        
        notice = Notice(
            id=notice_id,
            title=title,
            content=content,
            notice_type=notice_type,
            priority=priority,
            target_audience=target_audience,
            created_by=created_by,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            valid_from=valid_from or datetime.now().strftime("%Y-%m-%d"),
            valid_until=valid_until
        )
        self.notices[notice_id] = notice
        return notice_id
    
    def pin_notice(self, notice_id: str) -> bool:
        """置顶通知"""
        if notice_id in self.notices:
            self.notices[notice_id].is_pinned = True
            return True
        return False
    
    def get_active_notices(self, audience: str) -> List[Notice]:
        """获取有效通知"""
        now = datetime.now().strftime("%Y-%m-%d")
        active = []
        
        for notice in self.notices.values():
            # 检查有效期
            if notice.valid_until and notice.valid_until < now:
                continue
            # 检查受众
            if audience not in notice.target_audience and "all" not in notice.target_audience:
                continue
            active.append(notice)
        
        # 按置顶和优先级排序
        active.sort(key=lambda x: (not x.is_pinned, -x.priority, -x.view_count))
        return active
    
    def subscribe(self, user_id: str, notice_types: List[str]) -> bool:
        """订阅通知"""
        self.subscribers[user_id] = notice_types
        return True
    
    def get_unread_count(self, user_id: str) -> int:
        """获取未读数量"""
        if user_id not in self.subscribers:
            return 0
        
        subscribed_types = self.subscribers[user_id]
        count = 0
        for notice in self.notices.values():
            if notice.notice_type.value in subscribed_types:
                count += 1
        return count


# ==========================================
# 考试安排系统
# ==========================================

@dataclass
class Exam:
    """考试信息"""
    id: str
    name: str
    subject: str
    exam_date: str
    start_time: str
    end_time: str
    location: str
    duration_minutes: int
    total_score: float
    passing_score: float
    exam_type: str  #期中/期末/月考
    notes: str = ""

@dataclass
class ExamSeat:
    """考场座位"""
    exam_id: str
    room: str
    row: int
    col: int
    student_id: str = ""


class ExamScheduler:
    """考试安排器"""
    
    def __init__(self):
        self.exams: Dict[str, Exam] = {}
        self.seats: Dict[str, List[ExamSeat]] = {}  # exam_id -> seats
        self.next_id = 1
    
    def create_exam(self, name: str, subject: str, exam_date: str,
                   start_time: str, end_time: str, location: str,
                   duration: int, total_score: float, passing_score: float,
                   exam_type: str) -> str:
        """创建考试"""
        exam_id = f"E{self.next_id:04d}"
        self.next_id += 1
        
        exam = Exam(
            id=exam_id,
            name=name,
            subject=subject,
            exam_date=exam_date,
            start_time=start_time,
            end_time=end_time,
            location=location,
            duration_minutes=duration,
            total_score=total_score,
            passing_score=passing_score,
            exam_type=exam_type
        )
        self.exams[exam_id] = exam
        self.seats[exam_id] = []
        return exam_id
    
    def arrange_seats(self, exam_id: str, room_layout: Tuple[int, int],
                     student_ids: List[str]) -> bool:
        """安排座位"""
        if exam_id not in self.exams:
            return False
        
        rows, cols = room_layout
        seat_idx = 0
        
        for row in range(rows):
            for col in range(cols):
                if seat_idx >= len(student_ids):
                    break
                seat = ExamSeat(
                    exam_id=exam_id,
                    room=self.exams[exam_id].location,
                    row=row,
                    col=col,
                    student_id=student_ids[seat_idx]
                )
                self.seats[exam_id].append(seat)
                seat_idx += 1
        
        return True
    
    def get_seat_number(self, exam_id: str, student_id: str) -> Optional[ExamSeat]:
        """获取座位号"""
        if exam_id not in self.seats:
            return None
        
        for seat in self.seats[exam_id]:
            if seat.student_id == student_id:
                return seat
        return None
    
    def get_exam_schedule(self, start_date: str, end_date: str) -> List[Exam]:
        """获取考试日程"""
        exams = []
        for exam in self.exams.values():
            if start_date <= exam.exam_date <= end_date:
                exams.append(exam)
        return sorted(exams, key=lambda x: (x.exam_date, x.start_time))


# ==========================================
# 请假审批系统
# ==========================================

class LeaveType(Enum):
    """请假类型"""
    SICK = "sick"
    PERSONAL = "personal"
    FAMILY = "family"
    OFFICIAL = "official"
    OTHER = "other"

class LeaveStatus(Enum):
    """请假状态"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

@dataclass
class LeaveRequest:
    """请假申请"""
    id: str
    student_id: str
    leave_type: LeaveType
    start_date: str
    end_date: str
    reason: str
    status: LeaveStatus
    approver_id: str = ""
    approved_at: str = ""
    reject_reason: str = ""
    attachment: str = ""


class LeaveApprovalSystem:
    """请假审批系统"""
    
    def __init__(self):
        self.requests: Dict[str, LeaveRequest] = {}
        self.approvers: Dict[str, List[str]] = {}  # approver_id -> authorized_types
        self.next_id = 1
        self.auto_approve_config = {
            'max_days': 3,
            'allowed_types': [LeaveType.SICK]
        }
    
    def submit_request(self, student_id: str, leave_type: LeaveType,
                      start_date: str, end_date: str, reason: str,
                      attachment: str = "") -> str:
        """提交请假申请"""
        request_id = f"L{self.next_id:06d}"
        self.next_id += 1
        
        # 计算天数
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1
        
        # 自动审批
        status = LeaveStatus.PENDING
        if leave_type in self.auto_approve_config['allowed_types'] and \
           days <= self.auto_approve_config['max_days']:
            status = LeaveStatus.APPROVED
        
        request = LeaveRequest(
            id=request_id,
            student_id=student_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status=status,
            attachment=attachment
        )
        self.requests[request_id] = request
        return request_id
    
    def approve_request(self, request_id: str, approver_id: str) -> bool:
        """审批通过"""
        if request_id not in self.requests:
            return False
        
        self.requests[request_id].status = LeaveStatus.APPROVED
        self.requests[request_id].approver_id = approver_id
        self.requests[request_id].approved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True
    
    def reject_request(self, request_id: str, approver_id: str, reason: str) -> bool:
        """审批拒绝"""
        if request_id not in self.requests:
            return False
        
        self.requests[request_id].status = LeaveStatus.REJECTED
        self.requests[request_id].approver_id = approver_id
        self.requests[request_id].reject_reason = reason
        return True
    
    def get_pending_requests(self, approver_id: str) -> List[LeaveRequest]:
        """获取待审批请求"""
        return [r for r in self.requests.values() 
                if r.status == LeaveStatus.PENDING]
    
    def cancel_request(self, request_id: str) -> bool:
        """取消申请"""
        if request_id in self.requests:
            self.requests[request_id].status = LeaveStatus.CANCELLED
            return True
        return False


# ==========================================
# 数据备份与恢复系统
# ==========================================

class DataBackupManager:
    """数据备份管理器"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = backup_dir
        self.backups: List[Dict] = []
        self.max_backups = 10
        self.compression_enabled = True
        self.encryption_enabled = False
    
    def create_backup(self, data: Dict, backup_name: str = "") -> str:
        """创建备份"""
        import json
        import hashlib
        
        if not backup_name:
            backup_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        backup_path = f"{self.backup_dir}/{backup_name}.json"
        
        backup_info = {
            'name': backup_name,
            'path': backup_path,
            'created_at': datetime.now().isoformat(),
            'size': len(json.dumps(data)),
            'checksum': hashlib.md5(json.dumps(data).encode()).hexdigest()
        }
        
        # 保存备份文件
        os.makedirs(self.backup_dir, exist_ok=True)
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.backups.append(backup_info)
        
        # 清理旧备份
        if len(self.backups) > self.max_backups:
            oldest = self.backups.pop(0)
            try:
                os.remove(oldest['path'])
            except:
                pass
        
        return backup_name
    
    def restore_backup(self, backup_name: str) -> Optional[Dict]:
        """恢复备份"""
        import json
        
        backup_path = f"{self.backup_dir}/{backup_name}.json"
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def list_backups(self) -> List[Dict]:
        """列出所有备份"""
        return sorted(self.backups, key=lambda x: x['created_at'], reverse=True)
    
    def delete_backup(self, backup_name: str) -> bool:
        """删除备份"""
        backup_path = f"{self.backup_dir}/{backup_name}.json"
        try:
            os.remove(backup_path)
            self.backups = [b for b in self.backups if b['name'] != backup_name]
            return True
        except:
            return False
    
    def verify_backup(self, backup_name: str) -> bool:
        """验证备份完整性"""
        import json
        import hashlib
        
        backup_path = f"{self.backup_dir}/{backup_name}.json"
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 验证校验和
            for backup in self.backups:
                if backup['name'] == backup_name:
                    current_checksum = hashlib.md5(json.dumps(data).encode()).hexdigest()
                    return current_checksum == backup['checksum']
        except:
            return False
        return False


# ==========================================
# 数据统计分析模块
# ==========================================

class StatisticsAnalyzer:
    """统计分析器"""
    
    def __init__(self):
        self.data_cache: Dict = {}
        self.calculation_history: List[Dict] = []
    
    def calculate_attendance_stats(self, attendance_manager: AttendanceManager,
                                   class_id: str = "") -> Dict:
        """计算考勤统计"""
        records = attendance_manager.records
        if class_id:
            records = [r for r in records if r.class_id == class_id]
        
        total = len(records)
        if total == 0:
            return {}
        
        stats = {
            'total_records': total,
            'present_rate': sum(1 for r in records 
                               if r.status == AttendanceStatus.PRESENT) / total * 100,
            'absent_rate': sum(1 for r in records 
                              if r.status == AttendanceStatus.ABSENT) / total * 100,
            'late_rate': sum(1 for r in records 
                            if r.status == AttendanceStatus.LATE) / total * 100,
        }
        return stats
    
    def calculate_grade_distribution(self, grade_manager: GradeManager,
                                     subject: str = "") -> Dict:
        """计算成绩分布"""
        distributions = {
            'excellent': 0,  # 90+
            'good': 0,       # 80-89
            'pass': 0,       # 60-79
            'fail': 0,       # <60
        }
        
        for student_scores in grade_manager.grades.values():
            for subj, score in student_scores.items():
                if subject and subj != subject:
                    continue
                
                if score >= 90:
                    distributions['excellent'] += 1
                elif score >= 80:
                    distributions['good'] += 1
                elif score >= 60:
                    distributions['pass'] += 1
                else:
                    distributions['fail'] += 1
        
        total = sum(distributions.values())
        if total > 0:
            for key in distributions:
                distributions[key] = distributions[key] / total * 100
        
        return distributions
    
    def generate_trend_data(self, data_points: List[float], 
                           period: str = "daily") -> List[Dict]:
        """生成趋势数据"""
        trends = []
        for i, value in enumerate(data_points):
            trend = {
                'index': i,
                'value': value,
                'change': 0,
                'change_rate': 0
            }
            
            if i > 0:
                trend['change'] = value - data_points[i-1]
                trend['change_rate'] = (trend['change'] / data_points[i-1] * 100) if data_points[i-1] != 0 else 0
            
            trends.append(trend)
        
        return trends
    
    def export_statistics_report(self, stats: Dict, title: str) -> str:
        """导出统计报告"""
        report = f"{'='*50}\n"
        report += f"{title}\n"
        report += f"{'='*50}\n"
        report += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for key, value in stats.items():
            if isinstance(value, float):
                report += f"{key}: {value:.2f}\n"
            else:
                report += f"{key}: {value}\n"
        
        return report


# ==========================================
# 权限管理系统
# ==========================================

class Permission(Enum):
    """权限枚举"""
    VIEW_STUDENTS = "view_students"
    EDIT_STUDENTS = "edit_students"
    DELETE_STUDENTS = "delete_students"
    VIEW_GRADES = "view_grades"
    EDIT_GRADES = "edit_grades"
    VIEW_ATTENDANCE = "view_attendance"
    EDIT_ATTENDANCE = "edit_attendance"
    MANAGE_HOMEWORK = "manage_homework"
    PUBLISH_NOTICE = "publish_notice"
    MANAGE_EXAM = "manage_exam"
    APPROVE_LEAVE = "approve_leave"
    ADMIN_ACCESS = "admin_access"

class Role(Enum):
    """角色枚举"""
    STUDENT = "student"
    TEACHER = "teacher"
    CLASS_TEACHER = "class_teacher"
    DEPARTMENT_HEAD = "department_head"
    ADMIN = "admin"

@dataclass
class User:
    """用户"""
    id: str
    username: str
    role: Role
    class_id: str = ""
    department: str = ""
    permissions: List[Permission] = field(default_factory=list)

class PermissionManager:
    """权限管理器"""
    
    # 角色默认权限映射
    ROLE_PERMISSIONS = {
        Role.STUDENT: [
            Permission.VIEW_STUDENTS,
            Permission.VIEW_GRADES,
            Permission.VIEW_ATTENDANCE,
        ],
        Role.TEACHER: [
            Permission.VIEW_STUDENTS,
            Permission.EDIT_STUDENTS,
            Permission.VIEW_GRADES,
            Permission.EDIT_GRADES,
            Permission.VIEW_ATTENDANCE,
            Permission.EDIT_ATTENDANCE,
            Permission.MANAGE_HOMEWORK,
        ],
        Role.CLASS_TEACHER: [
            Permission.VIEW_STUDENTS,
            Permission.EDIT_STUDENTS,
            Permission.VIEW_GRADES,
            Permission.EDIT_GRADES,
            Permission.VIEW_ATTENDANCE,
            Permission.EDIT_ATTENDANCE,
            Permission.MANAGE_HOMEWORK,
            Permission.PUBLISH_NOTICE,
            Permission.APPROVE_LEAVE,
        ],
        Role.DEPARTMENT_HEAD: [
            Permission.VIEW_STUDENTS,
            Permission.VIEW_GRADES,
            Permission.EDIT_GRADES,
            Permission.VIEW_ATTENDANCE,
            Permission.MANAGE_EXAM,
            Permission.PUBLISH_NOTICE,
        ],
        Role.ADMIN: [p for p in Permission],
    }
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.session_tokens: Dict[str, str] = {}  # token -> user_id
    
    def create_user(self, user_id: str, username: str, role: Role,
                   class_id: str = "", department: str = "") -> User:
        """创建用户"""
        permissions = self.ROLE_PERMISSIONS.get(role, [])
        user = User(
            id=user_id,
            username=username,
            role=role,
            class_id=class_id,
            department=department,
            permissions=permissions
        )
        self.users[user_id] = user
        return user
    
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """检查权限"""
        if user_id not in self.users:
            return False
        return permission in self.users[user_id].permissions
    
    def grant_permission(self, user_id: str, permission: Permission) -> bool:
        """授予权限"""
        if user_id not in self.users:
            return False
        if permission not in self.users[user_id].permissions:
            self.users[user_id].permissions.append(permission)
        return True
    
    def revoke_permission(self, user_id: str, permission: Permission) -> bool:
        """撤销权限"""
        if user_id not in self.users:
            return False
        if permission in self.users[user_id].permissions:
            self.users[user_id].permissions.remove(permission)
        return True
    
    def login(self, user_id: str) -> str:
        """登录"""
        import hashlib
        import secrets
        
        if user_id not in self.users:
            return ""
        
        token = secrets.token_hex(32)
        self.session_tokens[token] = user_id
        return token
    
    def logout(self, token: str) -> bool:
        """登出"""
        if token in self.session_tokens:
            del self.session_tokens[token]
            return True
        return False
    
    def get_current_user(self, token: str) -> Optional[User]:
        """获取当前用户"""
        user_id = self.session_tokens.get(token)
        if user_id:
            return self.users.get(user_id)
        return None


# ==========================================
# SmartPicker Pro V5.0 全功能整合
# ==========================================

class SmartPickerProV5:
    """SmartPicker Pro V5.0 - 终极版课堂点名系统"""
    
    def __init__(self):
        # 核心组件
        self.picker = StudentPicker()
        self.weight_manager = WeightManager()
        self.blacklist_manager = BlacklistManager()
        self.record_manager = RecordManager()
        
        # 扩展组件
        self.grade_manager = GradeManager()
        self.attendance_manager = AttendanceManager()
        self.homework_manager = HomeworkManager()
        self.notice_board = NoticeBoard()
        self.exam_scheduler = ExamScheduler()
        self.leave_system = LeaveApprovalSystem()
        self.backup_manager = DataBackupManager()
        self.stats_analyzer = StatisticsAnalyzer()
        self.permission_manager = PermissionManager()
        
        # 配置
        self.config = {
            'version': '5.0',
            'build_date': '2026-06-13',
            'features': [
                '智能点名', '权重系统', '黑名单加密', '成绩管理',
                '考勤管理', '作业管理', '通知公告', '考试安排',
                '请假审批', '数据备份', '统计分析', '权限管理'
            ]
        }
        
        self._init_default_data()
    
    def _init_default_data(self):
        """初始化默认数据"""
        # 创建管理员账户
        self.permission_manager.create_user(
            user_id='admin001',
            username='管理员',
            role=Role.ADMIN
        )
        
        # 创建教师账户
        self.permission_manager.create_user(
            user_id='teacher001',
            username='教师',
            role=Role.TEACHER
        )
        
        # 初始化默认配置
        self.config['max_history_days'] = 365
        self.config['auto_backup_enabled'] = True
        self.config['backup_interval_hours'] = 24
    
    def pick_student(self) -> str:
        """执行点名"""
        student = self.picker.pick()
        if student:
            # 记录点名
            self.record_manager.add_record(
                student_id=student.id,
                student_name=student.name,
                class_name=student.class_name
            )
            # 更新权重
            self.weight_manager.update_weight(student.id)
        return student.name if student else ""
    
    def get_full_report(self) -> str:
        """获取完整报告"""
        report = "=" * 60 + "\n"
        report += "SmartPicker Pro V5.0 系统报告\n"
        report += "=" * 60 + "\n\n"
        
        report += f"版本: {self.config['version']}\n"
        report += f"构建日期: {self.config['build_date']}\n\n"
        
        report += "功能模块:\n"
        for feature in self.config['features']:
            report += f"  ✓ {feature}\n"
        
        report += f"\n学生总数: {len(self.picker.students)}\n"
        report += f"历史记录: {len(self.record_manager.records)} 条\n"
        report += f"黑名单人数: {len(self.blacklist_manager.blacklist)}\n"
        
        return report
    
    def export_all_data(self) -> Dict:
        """导出所有数据"""
        return {
            'students': [vars(s) for s in self.picker.students],
            'records': [vars(r) for r in self.record_manager.records],
            'blacklist': [vars(b) for b in self.blacklist_manager.blacklist],
            'config': self.config,
            'exported_at': datetime.now().isoformat()
        }
    
    def import_data(self, data: Dict) -> bool:
        """导入数据"""
        try:
            # 恢复学生数据
            self.picker.students = [Student(**s) for s in data.get('students', [])]
            
            # 恢复记录
            self.record_manager.records = [PickRecord(**r) for r in data.get('records', [])]
            
            # 恢复黑名单
            self.blacklist_manager.blacklist = [BlacklistEntry(**b) for b in data.get('blacklist', [])]
            
            return True
        except Exception as e:
            print(f"导入失败: {e}")
            return False
    
    def backup_data(self, backup_name: str = "") -> str:
        """备份数据"""
        data = self.export_all_data()
        return self.backup_manager.create_backup(data, backup_name)
    
    def restore_data(self, backup_name: str) -> bool:
        """恢复数据"""
        data = self.backup_manager.restore_backup(backup_name)
        if data:
            return self.import_data(data)
        return False
    
    def run(self):
        """运行主程序"""
        print(self.get_full_report())
        print("\n系统已准备就绪！")


# ==========================================
# 程序入口
# ==========================================

if __name__ == "__main__":
    app = SmartPickerProV5()
    app.run()
