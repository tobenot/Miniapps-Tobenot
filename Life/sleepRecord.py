# 需要安装以下依赖:
# pip install PyQt6 pandas matplotlib seaborn

import sys
import json
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QDateEdit, 
                            QTimeEdit, QCalendarWidget, QTableWidget, 
                            QTableWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt, QDate, QTime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class SleepTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("睡眠记录助手 😴")
        self.setGeometry(100, 100, 800, 600)
        
        # 数据文件路径
        self.data_file = "sleep_data.json"
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
        
        # 添加数据区域
        input_layout = QHBoxLayout()
        
        # 日期选择
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        input_layout.addWidget(QLabel("日期:"))
        input_layout.addWidget(self.date_edit)
        
        # 睡眠时间
        self.sleep_time = QTimeEdit()
        self.sleep_time.setTime(QTime(23, 0))
        input_layout.addWidget(QLabel("睡眠时间:"))
        input_layout.addWidget(self.sleep_time)
        
        # 起床时间
        self.wake_time = QTimeEdit()
        self.wake_time.setTime(QTime(7, 0))
        input_layout.addWidget(QLabel("起床时间:"))
        input_layout.addWidget(self.wake_time)
        
        # 添加按钮
        add_btn = QPushButton("添加记录 ✍️")
        add_btn.clicked.connect(self.add_record)
        input_layout.addWidget(add_btn)
        
        layout.addLayout(input_layout)
        
        # 数据显示表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # 增加一列显示成就
        self.table.setHorizontalHeaderLabels(["日期", "睡眠时间", "起床时间", "睡眠时长", "获得成就"])
        layout.addWidget(self.table)
        
        # 功能按钮
        btn_layout = QHBoxLayout()
        
        generate_report_btn = QPushButton("生成报告 📊")
        generate_report_btn.clicked.connect(self.generate_report)
        btn_layout.addWidget(generate_report_btn)
        
        view_achievements_btn = QPushButton("查看成就 🏆")
        view_achievements_btn.clicked.connect(self.view_achievements)
        btn_layout.addWidget(view_achievements_btn)
        
        layout.addLayout(btn_layout)
        
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
            "achievements": achieved
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
        self.table.setColumnCount(5)  # 增加一列显示成就
        self.table.setHorizontalHeaderLabels(["日期", "睡眠时间", "起床时间", "睡眠时长", "获得成就"])
        
        for i, record in enumerate(self.sleep_data):
            self.table.setItem(i, 0, QTableWidgetItem(record["date"]))
            self.table.setItem(i, 1, QTableWidgetItem(record["sleep_time"]))
            self.table.setItem(i, 2, QTableWidgetItem(record["wake_time"]))
            self.table.setItem(i, 3, QTableWidgetItem(str(record["duration"])))
            
            # 显示成就图标
            achievements_text = " ".join(emoji for _, emoji in record["achievements"])
            self.table.setItem(i, 4, QTableWidgetItem(achievements_text))

    def view_achievements(self):
        message = "🏆 成就系统 🏆\n\n"
        for name, achievement in self.daily_achievements.items():
            status = "✅" if achievement["achieved"] else "❌"
            message += f"{status} {name}: {achievement['description']}\n"
        
        QMessageBox.information(self, "成就系统", message)
        
    def generate_report(self):
        if not self.sleep_data:
            QMessageBox.warning(self, "警告", "没有用的睡眠数据！")
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
        plt.savefig('sleep_trend.png')
        
        # 生成更详细的Markdown报告
        report = f"""# 睡眠记录报告 😴

## 统计概要 📊
- 记录天数: {len(df)} 天
- 平均睡眠时长: {df['duration_hours'].mean():.2f} 小时
- 最长睡眠: {df['duration_hours'].max():.2f} 小时
- 最短睡眠: {df['duration_hours'].min():.2f} 小时

## 成就统计 🏆
"""
        # 统计各类成就获得次数
        achievement_counts = {}
        for record in self.sleep_data:
            for _, emoji in record["achievements"]:
                achievement_counts[emoji] = achievement_counts.get(emoji, 0) + 1
        
        for emoji, count in achievement_counts.items():
            report += f"{emoji} x{count} "
        
        report += "\n## 所有睡眠记录 📝\n"
        # 按日期排序
        df_sorted = df.sort_values('date', ascending=False)
        for i, record in df_sorted.iterrows():
            idx = df_sorted.index.get_loc(i)
            achievements_text = " ".join(emoji for _, emoji in self.sleep_data[idx]["achievements"])
            report += f"- {record['date'].strftime('%Y-%m-%d')}: "
            report += f"睡眠 {self.sleep_data[idx]['sleep_time']} → "
            report += f"起床 {self.sleep_data[idx]['wake_time']} "
            report += f"({record['duration_hours']:.2f}小时) "
            report += f"{achievements_text}\n"
            
        with open('sleep_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
            
        QMessageBox.information(self, "成功", "报告已生成！ 📊\n请查看 sleep_report.md 文件")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SleepTracker()
    window.show()
    sys.exit(app.exec())
