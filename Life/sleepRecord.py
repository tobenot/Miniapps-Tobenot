# 需要安装以下依赖:
# pip install PyQt6 pandas matplotlib seaborn

# 色板
# <palette>
#   <color name="Space cadet" hex="22223b" r="34" g="34" b="59" />
#   <color name="Ultra Violet" hex="4a4e69" r="74" g="78" b="105" />
#   <color name="Rose quartz" hex="9a8c98" r="154" g="140" b="152" />
#   <color name="Pale Dogwood" hex="c9ada7" r="201" g="173" b="167" />
#   <color name="Isabelline" hex="f2e9e4" r="242" g="233" b="228" />
# </palette>

import sys
import json
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QDateEdit, 
                            QTimeEdit, QCalendarWidget, QTableWidget, 
                            QTableWidgetItem, QMessageBox, QSpinBox, QLineEdit)  # 添加QSpinBox和QLineEdit
from PyQt6.QtCore import Qt, QDate, QTime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

class TimeInputWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setWrapping(True)
        self.hour_spin.setFixedWidth(60)
        
        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setWrapping(True)
        self.minute_spin.setFixedWidth(60)
        
        colon_label = QLabel(":")
        
        layout.addWidget(self.hour_spin)
        layout.addWidget(colon_label)
        layout.addWidget(self.minute_spin)
        
        # 设置样式
        self.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 2px solid #9a8c98;
                border-radius: 5px;
                background: white;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                margin: 0 5px;
            }
        """)
    
    def setTime(self, hour, minute):
        self.hour_spin.setValue(hour)
        self.minute_spin.setValue(minute)
    
    def time(self):
        return QTime(self.hour_spin.value(), self.minute_spin.value())

# 添加新的 DateInputWidget 类
class DateInputWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        current_date = QDate.currentDate()
        
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(current_date.year())
        self.year_spin.setFixedWidth(80)
        
        self.month_spin = QSpinBox()
        self.month_spin.setRange(1, 12)
        self.month_spin.setValue(current_date.month())
        self.month_spin.setFixedWidth(60)
        
        self.day_spin = QSpinBox()
        self.day_spin.setRange(1, 31)
        self.day_spin.setValue(current_date.day())
        self.day_spin.setFixedWidth(60)
        
        separator1 = QLabel("-")
        separator2 = QLabel("-")
        
        layout.addWidget(self.year_spin)
        layout.addWidget(separator1)
        layout.addWidget(self.month_spin)
        layout.addWidget(separator2)
        layout.addWidget(self.day_spin)
        
        # 设置样式
        self.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 2px solid #9a8c98;
                border-radius: 5px;
                background: white;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                margin: 0 5px;
            }
        """)
        
        # 添加月份变化时更新天数的逻辑
        self.month_spin.valueChanged.connect(self.update_days)
        self.year_spin.valueChanged.connect(self.update_days)
    
    def update_days(self):
        year = self.year_spin.value()
        month = self.month_spin.value()
        current_day = self.day_spin.value()
        
        # 获取该月的天数
        days_in_month = QDate(year, month, 1).daysInMonth()
        
        # 更新日期范围
        self.day_spin.setRange(1, days_in_month)
        
        # 如果当前日期超过了新的最大天数,则设置为最大天数
        if current_day > days_in_month:
            self.day_spin.setValue(days_in_month)
    
    def date(self):
        return QDate(self.year_spin.value(), 
                    self.month_spin.value(), 
                    self.day_spin.value())
    
    def setDate(self, date):
        self.year_spin.setValue(date.year())
        self.month_spin.setValue(date.month())
        self.day_spin.setValue(date.day())

class SleepTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("睡眠记录助手 😴")
        self.setGeometry(100, 100, 900, 650)
        
        # 获取脚本所在目录
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 更新应用全局样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f2e9e4;  /* Isabelline */
            }
            QWidget {
                font-family: 'Microsoft YaHei', '微软雅黑', Arial;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4a4e69;  /* Ultra Violet */
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                min-width: 120px;
                font-family: 'Microsoft YaHei', '微软雅黑', Arial;
            }
            QPushButton:hover {
                background-color: #22223b;  /* Space cadet */
            }
            QLabel {
                color: #22223b;  /* Space cadet */
                font-weight: bold;
            }
            QDateEdit, QTimeEdit {
                padding: 5px;
                border: 2px solid #9a8c98;  /* Rose quartz */
                border-radius: 5px;
                background: white;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #f2e9e4;  /* Isabelline */
                border: 1px solid #c9ada7;  /* Pale Dogwood */
                border-radius: 5px;
                gridline-color: #c9ada7;  /* Pale Dogwood */
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #4a4e69;  /* Ultra Violet */
                color: white;
                padding: 8px;
                border: none;
            }
        """)
        
        # 数据文件路径
        self.data_file = os.path.join(self.script_dir, "sleep_data.json")
        self.load_data()
        
        # 调整后的每日成就系统
        self.daily_achievements = {
            "超级早睡": {"description": "0:00前睡觉", "emoji": "🌌"},
            "早睡": {"description": "1:00前睡觉", "emoji": "😴"},
            "超级早起": {"description": "7:00前起床", "emoji": "🌟"},
            "早起": {"description": "8:00前起床", "emoji": "🌅"},
            "充足睡眠": {"description": "睡眠时间超过7小时", "emoji": "✨"},
            "作息规律": {"description": "与前一天睡眠时间相差不超过60分钟", "emoji": "🎯"},
            "超长睡眠": {"description": "睡眠时间超过9小时", "emoji": "🛌"},
            "周末不赖床": {"description": "周末9:00前起床", "emoji": "💪"},
            "作息达人": {"description": "连续7天保持相似作息", "emoji": "👑"},
            "早睡周": {"description": "连续7天1:00前睡觉", "emoji": "🏆"},
            "早起周": {"description": "连续7天8:00前起床", "emoji": "🎖️"},
            "早睡三连": {"description": "连续3天1:00前睡觉", "emoji": "🌠"},
            "早起三连": {"description": "连续3天8:00前起床", "emoji": "🌇"},
            "规律三连": {"description": "连续3天保持相似作息", "emoji": "📅"},
            "充足睡眠三连": {"description": "连续3天睡眠超过7小时", "emoji": "💫"}
        }
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加标题
        title_label = QLabel("记录今日睡眠 💤")
        title_label.setStyleSheet("""
            font-size: 24px;
            color: #2c3e50;
            margin-bottom: 10px;
            padding: 10px;
        """)
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 输入区域容器
        input_container = QWidget()
        input_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #c9ada7;  /* Pale Dogwood */
                border-radius: 10px;
                padding: 15px;
            }
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setSpacing(20)
        
        # 日期选择
        date_widget = QWidget()
        date_layout = QVBoxLayout(date_widget)
        date_label = QLabel("日期:")
        self.date_edit = DateInputWidget()  # 使用新的 DateInputWidget
        self.date_edit.setDate(QDate.currentDate())
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        input_layout.addWidget(date_widget)
        
        # 睡眠时间
        sleep_widget = QWidget()
        sleep_layout = QVBoxLayout(sleep_widget)
        sleep_label = QLabel("睡眠时间:")
        self.sleep_time = TimeInputWidget()
        self.sleep_time.setTime(23, 0)  # 设置默认时间
        sleep_layout.addWidget(sleep_label)
        sleep_layout.addWidget(self.sleep_time)
        input_layout.addWidget(sleep_widget)
        
        # 起床时间
        wake_widget = QWidget()
        wake_layout = QVBoxLayout(wake_widget)
        wake_label = QLabel("起床时间:")
        self.wake_time = TimeInputWidget()
        self.wake_time.setTime(7, 0)  # 设置默认时间
        wake_layout.addWidget(wake_label)
        wake_layout.addWidget(self.wake_time)
        input_layout.addWidget(wake_widget)
        # 添加按钮
        add_btn = QPushButton("添加记录 ✍️")
        add_btn.clicked.connect(self.add_record)
        add_btn.setStyleSheet("color: #22223b;")  # 设置按钮文字颜色为Space cadet
        input_layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        # 备注输入
        note_widget = QWidget()
        note_layout = QVBoxLayout(note_widget)
        note_label = QLabel("备注:")
        self.note_edit = QLineEdit()  # 添加这个类导入
        self.note_edit.setPlaceholderText("添加今日睡眠备注...")  # 设置占位符文本
        self.note_edit.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 2px solid #9a8c98;
                border-radius: 5px;
                background: white;
                min-width: 200px;
            }
        """)
        note_layout.addWidget(note_label)
        note_layout.addWidget(self.note_edit)
        input_layout.addWidget(note_widget)
        
        layout.addWidget(input_container)
        
        # 表格样式优化
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # 改为6列
        self.table.setHorizontalHeaderLabels(["日期", "睡眠时间", "起床时间", "睡眠时长", "获得成就", "备注"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
        
        # 功能按钮区域
        btn_container = QWidget()
        btn_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #c9ada7;  /* Pale Dogwood */
                border-radius: 10px;
                padding: 10px;
            }
        """)
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setSpacing(15)
        
        generate_report_btn = QPushButton("生成报告 📊")
        generate_report_btn.clicked.connect(self.generate_report)
        generate_report_btn.setStyleSheet("color: #22223b;")  # 设置按钮文字颜色为Space cadet
        btn_layout.addWidget(generate_report_btn)
        
        view_achievements_btn = QPushButton("查看成就 🏆")
        view_achievements_btn.clicked.connect(self.view_achievements)
        view_achievements_btn.setStyleSheet("color: #22223b;")  # 设置按钮文字颜色为Space cadet
        btn_layout.addWidget(view_achievements_btn)
        
        layout.addWidget(btn_container)
        
        self.update_table()
        
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.sleep_data = json.load(f)
        else:
            self.sleep_data = []
            
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.sleep_data, f, ensure_ascii=False, indent=2)
            
    def add_record(self):
        date = self.date_edit.date().toPyDate().strftime("%Y-%m-%d")
        sleep_time = self.sleep_time.time().toString("HH:mm")
        wake_time = self.wake_time.time().toString("HH:mm")
        
        # 计算睡眠时长
        sleep_dt = datetime.strptime(f"{date} {sleep_time}", "%Y-%m-%d %H:%M")
        wake_dt = datetime.strptime(f"{date} {wake_time}", "%Y-%m-%d %H:%M")
        if wake_dt < sleep_dt:
            wake_dt += timedelta(days=1)
        duration = wake_dt - sleep_dt
        
        # 检查当天获得的成就
        achieved = self.check_daily_achievements(sleep_time, wake_time, duration)
        
        record = {
            "date": date,
            "sleep_time": sleep_time,
            "wake_time": wake_time,
            "duration": str(duration),
            "achievements": achieved,
            "note": self.note_edit.text()  # 添加备注
        }
        
        self.sleep_data.append(record)
        self.save_data()
        self.update_table()
        
        # 显示当天获得的成就
        self.show_daily_achievements(achieved)
        
    def check_daily_achievements(self, sleep_time, wake_time, duration):
        achieved = []
        sleep_dt = datetime.strptime(sleep_time, "%H:%M")
        wake_dt = datetime.strptime(wake_time, "%H:%M")
        date = self.date_edit.date().toPyDate()
        
        # 基础成就检查
        if sleep_dt.time() < datetime.strptime("00:00", "%H:%M").time():
            achieved.append(("超级早睡", self.daily_achievements["超级早睡"]["emoji"]))
        elif sleep_dt.time() < datetime.strptime("01:00", "%H:%M").time():
            achieved.append(("早睡", self.daily_achievements["早睡"]["emoji"]))
        
        if wake_dt.time() < datetime.strptime("07:00", "%H:%M").time():
            achieved.append(("超级早起", self.daily_achievements["超级早起"]["emoji"]))
        elif wake_dt.time() < datetime.strptime("08:00", "%H:%M").time():
            achieved.append(("早起", self.daily_achievements["早起"]["emoji"]))
        
        if duration.total_seconds() / 3600 >= 7:
            achieved.append(("充足睡眠", self.daily_achievements["充足睡眠"]["emoji"]))
        
        if duration.total_seconds() / 3600 >= 9:
            achieved.append(("超长睡眠", self.daily_achievements["超长睡眠"]["emoji"]))
        
        if (datetime.strptime("22:00", "%H:%M").time() <= sleep_dt.time() <= 
            datetime.strptime("23:00", "%H:%M").time()):
            achieved.append(("黄金睡眠", self.daily_achievements["黄金睡眠"]["emoji"]))
        
        # 周末不赖床检查
        if date.weekday() >= 5:  # 周六和周日
            if wake_dt.time() < datetime.strptime("09:00", "%H:%M").time():
                achieved.append(("周末不赖床", self.daily_achievements["周末不赖床"]["emoji"]))
        
        # 连续性成就检查
        if len(self.sleep_data) > 0:
            # 作息规律检查
            prev_sleep = datetime.strptime(self.sleep_data[-1]["sleep_time"], "%H:%M")
            time_diff = abs((sleep_dt - prev_sleep).total_seconds() / 60)
            if time_diff <= 60:  # 改为60分钟
                achieved.append(("作息规律", self.daily_achievements["作息规律"]["emoji"]))
            
            # 连续7天成就检查
            if len(self.sleep_data) >= 6:  # 加上今天刚好7天
                # 检查连续早睡
                early_sleep_streak = all(
                    datetime.strptime(record["sleep_time"], "%H:%M").time() < 
                    datetime.strptime("01:00", "%H:%M").time()
                    for record in self.sleep_data[-6:]
                ) and sleep_dt.time() < datetime.strptime("01:00", "%H:%M").time()
                
                if early_sleep_streak:
                    achieved.append(("早睡周", self.daily_achievements["早睡周"]["emoji"]))
                
                # 检查连续早起
                early_wake_streak = all(
                    datetime.strptime(record["wake_time"], "%H:%M").time() < 
                    datetime.strptime("07:00", "%H:%M").time()
                    for record in self.sleep_data[-6:]
                ) and wake_dt.time() < datetime.strptime("07:00", "%H:%M").time()
                
                if early_wake_streak:
                    achieved.append(("早起周", self.daily_achievements["早起周"]["emoji"]))
                
                # 检查连续作息规律
                regular_schedule = True
                for i in range(len(self.sleep_data)-6, len(self.sleep_data)):
                    curr_sleep = datetime.strptime(self.sleep_data[i]["sleep_time"], "%H:%M")
                    next_sleep = datetime.strptime(self.sleep_data[i+1]["sleep_time"], "%H:%M")
                    if abs((curr_sleep - next_sleep).total_seconds() / 60) > 60:
                        regular_schedule = False
                        break
                
                if regular_schedule and time_diff <= 60:
                    achieved.append(("作息达人", self.daily_achievements["作息达人"]["emoji"]))
            
            # 添加三天连续成就检查
            if len(self.sleep_data) >= 2:  # 加上今天刚好3天
                # 检查连续三天早睡
                early_sleep_streak = all(
                    datetime.strptime(record["sleep_time"], "%H:%M").time() < 
                    datetime.strptime("01:00", "%H:%M").time()
                    for record in self.sleep_data[-2:]
                ) and sleep_dt.time() < datetime.strptime("01:00", "%H:%M").time()
                
                if early_sleep_streak:
                    achieved.append(("早睡三连", self.daily_achievements["早睡三连"]["emoji"]))
                
                # 检查连续三天早起
                early_wake_streak = all(
                    datetime.strptime(record["wake_time"], "%H:%M").time() < 
                    datetime.strptime("08:00", "%H:%M").time()
                    for record in self.sleep_data[-2:]
                ) and wake_dt.time() < datetime.strptime("08:00", "%H:%M").time()
                
                if early_wake_streak:
                    achieved.append(("早起三连", self.daily_achievements["早起三连"]["emoji"]))
                
                # 检查连续三天规律作息
                regular_schedule = True
                for i in range(len(self.sleep_data)-2, len(self.sleep_data)):
                    curr_sleep = datetime.strptime(self.sleep_data[i]["sleep_time"], "%H:%M")
                    next_sleep = datetime.strptime(self.sleep_data[i+1]["sleep_time"], "%H:%M")
                    if abs((curr_sleep - next_sleep).total_seconds() / 60) > 60:
                        regular_schedule = False
                        break
                
                if regular_schedule and time_diff <= 60:
                    achieved.append(("规律三连", self.daily_achievements["规律三连"]["emoji"]))
                
                # 检查连续三天充足睡眠
                sufficient_sleep_streak = all(
                    timedelta(hours=7) <= pd.to_timedelta(record["duration"])
                    for record in self.sleep_data[-2:]
                ) and duration >= timedelta(hours=7)
                
                if sufficient_sleep_streak:
                    achieved.append(("充足睡眠三连", self.daily_achievements["充足睡眠三连"]["emoji"]))

        return achieved
        
    def show_daily_achievements(self, achieved):
        if not achieved:
            message = "今天没有获得成就，继续加油！ 💪"
        else:
            message = "🎉 今获得的成就：\n\n"
            for achievement, emoji in achieved:
                message += f"{emoji} {achievement}\n"
        
        QMessageBox.information(self, "今日成就", message)
        
    def update_table(self):
        self.table.setRowCount(len(self.sleep_data))
        self.table.setColumnCount(6)  # 改为6列
        self.table.setHorizontalHeaderLabels(["日期", "睡眠时间", "起床时间", "睡眠时长", "获得成就", "备注"])
        
        for i, record in enumerate(self.sleep_data):
            self.table.setItem(i, 0, QTableWidgetItem(record["date"]))
            self.table.setItem(i, 1, QTableWidgetItem(record["sleep_time"]))
            self.table.setItem(i, 2, QTableWidgetItem(record["wake_time"]))
            self.table.setItem(i, 3, QTableWidgetItem(str(record["duration"])))
            
            # 显示成就图标
            achievements_text = " ".join(emoji for _, emoji in record["achievements"])
            self.table.setItem(i, 4, QTableWidgetItem(achievements_text))
            
            # 显示备注
            note = record.get("note", "")  # 使用get方法避免旧数据没有note字段的情况
            self.table.setItem(i, 5, QTableWidgetItem(note))

    def view_achievements(self):
        # 统计已获得的成就
        achieved_counts = {}
        for record in self.sleep_data:
            for achievement_name, emoji in record["achievements"]:
                achieved_counts[achievement_name] = achieved_counts.get(achievement_name, 0) + 1
        
        message = "🏆 成就系统 🏆\n\n"
        for name, achievement in self.daily_achievements.items():
            count = achieved_counts.get(name, 0)
            status = f"✅ (x{count})" if count > 0 else "❌"
            message += f"{achievement['emoji']} {name}: {achievement['description']} {status}\n"
        
        QMessageBox.information(self, "成就系统", message)
        
    def generate_report(self):
        if not self.sleep_data:
            QMessageBox.warning(self, "警告", "没有可用的睡眠数据！")
            return
            
        df = pd.DataFrame(self.sleep_data)
        df['date'] = pd.to_datetime(df['date'])
        df['duration'] = pd.to_timedelta(df['duration'])
        df['duration_hours'] = df['duration'].dt.total_seconds() / 3600
        
        # 生成图表
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df, x='date', y='duration_hours')
        plt.title('睡眠时长趋势')
        plt.xlabel('日期')
        plt.ylabel('睡眠时长（小时）')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.script_dir, 'sleep_trend.png'))
        
        # 创建睡眠时间分布热力图
        plt.figure(figsize=(12, 6))

        # 将睡眠时间转换为小时和分钟
        def time_to_float(time_str):
            hour, minute = map(int, time_str.split(':'))
            # 如果是凌晨时间（0-6点），加24小时以便于展示
            if hour < 6:
                hour += 24
            return hour + minute/60

        # 准备热力图数据
        df['sleep_hour'] = df['sleep_time'].apply(time_to_float)
        df['wake_hour'] = df['wake_time'].apply(time_to_float)
        df['weekday'] = df['date'].dt.strftime('%A')  # 获取星期几

        # 创建星期几的有序列表
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        sleep_matrix = np.zeros((7, 24))  # 7天 x 24小时

        # 统计每个时间段的睡眠频率
        for _, row in df.iterrows():
            day_idx = weekdays.index(row['weekday'])
            sleep_hour = int(row['sleep_hour'])
            wake_hour = int(row['wake_hour'])
            
            # 处理跨天的情况
            if wake_hour > 24:
                wake_hour = wake_hour % 24
            
            # 标记睡眠时间
            if sleep_hour >= 24:
                sleep_hour = sleep_hour % 24
            sleep_matrix[day_idx, sleep_hour] += 1

        # 绘制热力图
        plt.figure(figsize=(15, 8))
        sns.heatmap(sleep_matrix, 
                    xticklabels=range(24),
                    yticklabels=weekdays,
                    cmap='YlOrRd',
                    cbar_kws={'label': '睡眠频率'})

        plt.title('睡眠时间分布热力图')
        plt.xlabel('小时')
        plt.ylabel('星期')
        plt.tight_layout()
        plt.savefig(os.path.join(self.script_dir, 'sleep_heatmap.png'))

        # 生成更详细的Markdown报告
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"""---
title: 睡眠记录报告
date: {current_time}
tags:
    - 睡眠记录
    - 健康管理
categories: 生活记录
---

# 睡眠记录报告 😴

## 统计概要 📊

| 指标 | 数值 |
|------|------|
| 记录天数 | {len(df)} 天 |
| 平均睡眠时长 | {df['duration_hours'].mean():.2f} 小时 |
| 最长睡眠 | {df['duration_hours'].max():.2f} 小时 |
| 最短睡眠 | {df['duration_hours'].min():.2f} 小时 |

## 成就统计 🏆

| 成就 | 获得次数 |
|------|----------|
"""
        # 统计各类成就获得次数
        achievement_counts = {}
        for record in self.sleep_data:
            for name, emoji in record["achievements"]:
                key = f"{emoji} {name}"
                achievement_counts[key] = achievement_counts.get(key, 0) + 1
        
        for achievement, count in achievement_counts.items():
            report += f"| {achievement} | {count} |\n"
        
        report += "\n## 详细睡眠记录 📝\n\n"
        report += "| 日期 | 睡眠时间 | 起床时间 | 睡眠时长 | 成就 | 备注 |\n"
        report += "|------|----------|----------|----------|----------|----------|\n"
        
        # 按日期排序
        df_sorted = df.sort_values('date', ascending=False)
        for i, record in df_sorted.iterrows():
            idx = df_sorted.index.get_loc(i)
            achievements_text = " ".join(emoji for _, emoji in self.sleep_data[idx]["achievements"])
            note = self.sleep_data[idx].get("note", "")  # 获取备注
            report += f"| {record['date'].strftime('%Y-%m-%d')} "
            report += f"| {self.sleep_data[idx]['sleep_time']} "
            report += f"| {self.sleep_data[idx]['wake_time']} "
            report += f"| {record['duration_hours']:.2f}小时 "
            report += f"| {achievements_text} "
            report += f"| {note} |\n"
            
        report_path = os.path.join(self.script_dir, 'sleep_report.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
            
        QMessageBox.information(self, "成功", f"报告已生成！ 📊\n请查看 {report_path} 文件")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SleepTracker()
    window.show()
    sys.exit(app.exec())
