import json
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# 备份
import os
import shutil
import time
import zipfile
from datetime import datetime

import tkinter.ttk as ttk  # 导入ttk模块，用于进度条

# 备份工具，不支持原目录删除时备份也删除，这种情况请手动删除重新备份！

class BackupManagerGUI(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.title('备份管理程序')
        self.backup_root = ''  # 用于存储备份根目录
        self.backup_items = []
        self.total_size = 0  # 新增：备份项目的总大小
        self.completed_size = 0
        self.config_path = 'backup_config.json'  # 自动保存的配置文件路径
        self.create_widgets()
        self.load_settings()  # 启动时自动载入设置

    def create_widgets(self):
        # 备份根目录设置区域
        self.backup_root_label = tk.Label(self, text="备份根目录:")
        self.backup_root_label.grid(row=0, column=0, sticky='w')
        
        self.backup_root_entry = tk.Entry(self, width=50)
        self.backup_root_entry.grid(row=0, column=1, sticky='we')
        
        self.backup_root_button = tk.Button(self, text="选择", command=self.select_backup_root)
        self.backup_root_button.grid(row=0, column=2, sticky='w')
        
        # 备份目标列表区域
        self.targets_frame = tk.LabelFrame(self, text="备份目标")
        self.targets_frame.grid(row=1, column=0, columnspan=3, sticky='ew')
        
        self.targets_listbox = tk.Listbox(self.targets_frame, width=70, height=10)
        self.targets_listbox.pack(side="left", fill="y")
        
        self.scrollbar = tk.Scrollbar(self.targets_frame, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")
        
        self.targets_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.targets_listbox.yview)
        
        # 按钮区域
        self.add_target_button = tk.Button(self, text="添加备份目标", command=self.add_backup_target)
        self.add_target_button.grid(row=2, column=0, sticky='w')

        self.remove_target_button = tk.Button(self, text="删除备份目标", command=self.remove_backup_target)
        self.remove_target_button.grid(row=2, column=1, sticky='w')
        
        self.start_backup_button = tk.Button(self, text="开始备份", command=self.start_backup)
        self.start_backup_button.grid(row=2, column=2, sticky='e')

        self.export_settings_button = tk.Button(self, text="导出设置", command=self.export_settings)
        self.export_settings_button.grid(row=3, column=0, sticky='w')

        self.import_settings_button = tk.Button(self, text="导入设置", command=self.import_settings)
        self.import_settings_button.grid(row=3, column=2, sticky='e')

        self.create_log_widgets()
        
    def select_backup_root(self):
        # 选择备份根目录的方法实现
        directory = filedialog.askdirectory()
        self.backup_root_entry.delete(0, 'end')
        self.backup_root_entry.insert(0, directory)
        self.backup_root = directory
        self.auto_save_settings()  # 选择后自动保存设置

    def auto_save_settings(self):
        # 修改此方法以包含备份根目录
        config = {
            'backup_root': self.backup_root,
            'backup_items': self.backup_items
        }
        with open(self.config_path, 'w') as file:
            json.dump(config, file, indent=4)

    def add_backup_target(self):
        # 修改此方法以添加文件或目录为备份目标
        def add_item(target, is_dir):
            zip_option = messagebox.askyesno("选择", "是否为这个备份目标启用压缩?") if is_dir else False
            self.backup_items.append({"path": target, "zip": zip_option, "is_dir": is_dir})
            display_text = "{} ({}, {})".format(target, "压缩" if zip_option else "不压缩", "目录" if is_dir else "文件")
            self.targets_listbox.insert('end', display_text)
            self.auto_save_settings()  # 添加后自动保存设置
        
        target_type = messagebox.askquestion("添加备份目标", "添加目录吗？选否的话添加文件", type='yesno', icon='question', default='yes')
        if target_type == 'yes':
            target = filedialog.askdirectory()  # 添加目录
            if target:
                add_item(target, True)
        else:
            target = filedialog.askopenfilename()  # 添加文件
            if target:
                add_item(target, False)

    def remove_backup_target(self):
        # 实现删除备份目标的方法
        selected_items = self.targets_listbox.curselection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择要删除的备份目标")
            return
        for index in selected_items[::-1]:
            del self.backup_items[index]
            self.targets_listbox.delete(index)
        self.auto_save_settings()  # 删除后自动保存设置
        
    def load_settings(self):
        try:
            with open(self.config_path, 'r') as file:
                config = json.load(file)
                self.backup_root = config.get('backup_root', '')
                self.backup_root_entry.insert(0, self.backup_root)
                self.backup_items = config.get('backup_items', [])
                self.update_listbox_with_backup_items()
        except FileNotFoundError:
            # 如果配置文件不存在，可以在这里初始化或忽略
            pass

    def export_settings(self):
        # 修改此方法以包含备份根目录
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                  filetypes=[("JSON files", "*.json")])
        if file_path:
            config = {
                'backup_root': self.backup_root,
                'backup_items': self.backup_items
            }
            with open(file_path, 'w') as file:
                json.dump(config, file, indent=4)
                messagebox.showinfo("导出设置", "备份设置已导出。")

    def import_settings(self):
        # 修改此方法以导入备份根目录
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as file:
                config = json.load(file)
                self.backup_root = config.get('backup_root', '')
                self.backup_items = config.get('backup_items', [])
                self.backup_root_entry.delete(0, 'end')
                self.backup_root_entry.insert(0, self.backup_root)
                self.update_listbox_with_backup_items()
                messagebox.showinfo("导入设置", "备份设置已导入。")
                self.auto_save_settings()  # 导入后自动保存设置

    def update_listbox_with_backup_items(self):
        # 将更新listbox内容的代码提取到这个单独的函数中
        self.targets_listbox.delete(0, tk.END)
        for item in self.backup_items:
            display_text = "{} ({})".format(item['path'], "压缩" if item['zip'] else "不压缩")
            self.targets_listbox.insert('end', display_text)
                
    def start_backup(self):
        if not self.backup_root:
            messagebox.showerror("错误", "请设置一个有效的备份根目录。")
            return

        # 记录开始时间：
        start_time = time.time()

        # 创建回收站
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recycle_bin_path = os.path.join(self.backup_root, f"~备份工具回收站_{timestamp}")
        if not os.path.exists(recycle_bin_path):
            os.makedirs(recycle_bin_path)

        # 获取并记录总备份大小
        total_size, _ = self.calculate_total_backup_size()
        completed_size = 0

        self.completed_size = 0
        self.total_size = total_size

        # 启用取消按钮
        self.cancel_backup_button['state'] = 'normal'
        self.backup_canceled = False

        self.log_message(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 开始备份进程。")

        # 对于每个备份项：
        for item in self.backup_items:
            try:
                self.completed_size = completed_size
                self.update_remain_time(start_time)
                
                source = item['path']
                destination = os.path.join(self.backup_root, os.path.relpath(source, start=os.path.dirname(source)))
                is_dir = item['is_dir']
                should_zip = item['zip']

                # 检查源是否存在
                if not os.path.exists(source):
                    messagebox.showwarning('警告', f'源路径 {source} 不存在。')
                    continue

                # 检查是否需要更新
                updated = self.check_updated(source, destination)
                if not updated:
                    self.log_message(f"未更新不备份：{source}")
                    continue

                # 如果是目录：
                if is_dir:
                    # 决定是否压缩
                    if should_zip:
                        destination += '.zip'
                        if self.check_updated(source, destination):
                            if os.path.exists(destination):
                                self.move_to_recycle_bin(destination, recycle_bin_path)
                            self.zip_directory(source, destination)
                        else:
                            self.log_message(f"未更新不备份：{source}")
                            continue
                            
                    else:
                        # 对于目录中的每个文件，根据需要备份
                        for root, dirs, files in os.walk(source):
                            for file in files:
                                file_path = os.path.join(root, file)
                                rel_path = os.path.relpath(file_path, start=source)
                                dest_path = os.path.join(destination, rel_path)
                                if self.check_updated(file_path, dest_path):
                                    target_dir = os.path.dirname(dest_path)
                                    if not os.path.exists(target_dir):
                                        os.makedirs(target_dir)
                                    if os.path.exists(dest_path):
                                        self.move_to_recycle_bin(dest_path, recycle_bin_path)
                                    shutil.copy2(file_path, dest_path)
                                    self.log_message(f"备份文件：{file_path} 至 {dest_path}") # 增加此行

                # 如果是单个文件，直接备份
                else:
                    if self.check_updated(source, destination):
                        if os.path.exists(destination):
                            self.move_to_recycle_bin(destination, recycle_bin_path)
                        shutil.copy2(source, destination)

                # 在拷贝每个文件后更新进度和日志
                if not self.backup_canceled:
                    if is_dir and should_zip:
                        self.log_message(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 压缩并备份：{source}")
                        completed_size += self.update_progress_and_log(source, destination, total_size, completed_size)
                        completed_size_str = self.size_to_string(completed_size, total_size)
                        self.log_message(f"已完成 {round(100.0 * completed_size / total_size, 2)}% 的备份， {completed_size_str}")
                    else:
                        self.log_message(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 备份：{source}")
                        completed_size += self.update_progress_and_log(source, destination, total_size, completed_size)
                        completed_size_str = self.size_to_string(completed_size, total_size)
                        self.log_message(f"已完成 {round(100.0 * completed_size / total_size, 2)}% 的备份， {completed_size_str}")
                else:
                    self.log_message(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 备份已取消。")
                    break

            except PermissionError as pe:
                messagebox.showwarning("权限错误", f"无法访问 {source}。请检查文件的读写权限。")
                self.log_message(f"权限错误: {pe}")
                continue  # Skip current file and continue with the next

            except OSError as ose:
                messagebox.showwarning("操作系统错误", f"处理文件 {source} 时发生错误。")
                self.log_message(f"操作系统错误: {ose}")
                continue  # Skip current file and continue with the next
              
            except Exception as e:
                messagebox.showwarning("未知错误", f"备份 {source} 时发生未知错误。")
                self.log_message(f"未知错误: {e}")
                continue  # Skip current file and continue with the next
            
        # 备份完成或取消，禁用取消按钮，并重置进度条
        end_time = time.time() 
        elapsed_time = end_time - start_time 
        hours, remainder = divmod(int(elapsed_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        elapsed_time_str = f"{hours}小时{minutes}分钟{seconds}秒 ({elapsed_time:.2f}秒)"
        self.log_message(f"用时：{elapsed_time_str}")

        self.cancel_backup_button['state'] = 'disabled'
        self.progress_bar['value'] = 0

        # 检查回收站是否为空，如果是，则删除
        if os.path.exists(recycle_bin_path) and not os.listdir(recycle_bin_path):
            shutil.rmtree(recycle_bin_path)  # 删除空的回收站目录
            self.log_message(f"回收站 {recycle_bin_path} 是空的，已经被删除。")
        else:
            self.log_message(f"回收站 {recycle_bin_path} 不是空的，未被删除。")
            
        if not self.backup_canceled:
            self.log_message(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 备份已完成。")
            messagebox.showinfo("备份", "备份进程已完成。")

        self.backup_canceled = False

    def cancel_backup(self):
        self.backup_canceled = True

    def size_to_string(self, size, total_size):
        if total_size < 1024:
            return "{}B".format(size)
        elif total_size < 1024 ** 2:
            return "{:.2f}KB".format(size / 1024)
        elif total_size < 1024 ** 3:
            return "{:.2f}MB".format(size / 1024**2)
        else:
            return "{:.2f}GB".format(size / 1024**3)
        
    def check_updated(self, source, destination):
        # 如果目标不存在，那么认为是更新的
        if not os.path.exists(destination):
            return True
        # 如果两者都是文件，则只比较修改时间
        if os.path.isfile(source) and os.path.isfile(destination):
            src_mtime = os.stat(source).st_mtime
            dst_mtime = os.stat(destination).st_mtime
            return src_mtime > dst_mtime
        # 如果源是目录，可能需要检查压缩文件的更新时间
        if os.path.isdir(source):
            # 在这里，我们要考虑是否检查压缩文件
            if destination.endswith('.zip'):
                zip_mtime = os.stat(destination).st_mtime if os.path.exists(destination) else 0
                for root, _, files in os.walk(source):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.getmtime(file_path) > zip_mtime:
                            timee = os.path.getmtime(file_path)
                            self.log_message(f"{timee}")
                            return True
                return False  # 压缩文件是最新的
            else:
                # 非压缩的目录
                return self.check_directory_updated(source, destination)
        return False

    def check_directory_updated(self, source_dir, destination_dir):
        # 检查目录中是否有文件更新
        for root, _, files in os.walk(source_dir):
            for file in files:
                source_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(source_file_path, start=source_dir)
                destination_file_path = os.path.join(destination_dir, relative_path)
                
                # 目标位置已存在的文件，才做比较
                if os.path.exists(destination_file_path):
                    src_mtime = os.stat(source_file_path).st_mtime
                    dst_mtime = os.stat(destination_file_path).st_mtime
                    if src_mtime > dst_mtime:
                        return True
                # 目标位置不存在的情况下，表明是新增的文件，也是需要更新的
                else:
                    return True
        # 所有文件都是最新的，不需要更新
        return False

    def zip_directory(self, source_dir, destination_zip):
        try:
            # 实现目录压缩的方法
            with zipfile.ZipFile(destination_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=source_dir)
                        zipf.write(file_path, arcname)
        except Exception as e:
            messagebox.showwarning("错误", f"压缩目录时出错: {e}")
            self.log_message(f"压缩目录时出错: {e}")

    def move_to_recycle_bin(self, target, recycle_bin):
        try:
            # 实现移动文件到回收站的方法
            target_in_bin = os.path.join(recycle_bin, os.path.relpath(target, start=self.backup_root))
            target_dir = os.path.dirname(target_in_bin)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            shutil.move(target, target_in_bin)
        except Exception as e:
            messagebox.showwarning("错误", f"移动文件到回收站时出错: {e}")
            self.log_message(f"移动文件到回收站时出错: {e}")

    def create_log_widgets(self):
        # 日志标题
        self.log_label = tk.Label(self, text="备份日志:")
        self.log_label.grid(row=4, column=0, sticky='w')

        # 日志展示框
        self.log_text = tk.Text(self, height=10, state='disabled')
        self.log_text.grid(row=5, column=0, columnspan=3, sticky='ew')

        # 进度条
        self.progress_label = tk.Label(self, text="备份进度")
        self.progress_label.grid(row=6, column=0, sticky='w')
        
        self.progress_bar = ttk.Progressbar(self, orient='horizontal', length=100, mode='determinate')
        self.progress_bar.grid(row=6, column=1, sticky='we')
        
        # 取消备份按钮
        self.cancel_backup_button = tk.Button(self, text="取消备份", command=self.cancel_backup, state='disabled')
        self.cancel_backup_button.grid(row=6, column=2, sticky='e')

        self.remaining_time_label = tk.Label(self, text="剩余时间: 00:00:00")
        self.remaining_time_label.grid(row=7, column=0, columnspan=3)

    def log_message(self, message):
        # 添加信息到日志显示窗口的方法
        self.log_text.config(state='normal')
        self.log_text.insert('end', message + "\n")
        self.log_text.see('end')
        self.log_text.config(state='disabled')

    def update_progress_and_log(self, source, destination, total_size, completed_size):
        # 更新进度条和日志的方法
        item_size = os.path.getsize(source) if os.path.isfile(source) else self.get_directory_size(source)
        self.progress_bar['maximum'] = total_size
        self.progress_bar['value'] = completed_size + item_size
        self.progress_bar.update()
        return item_size

    def update_remain_time(self, start_time):
        elapsed_time = time.time() - start_time
        remaining_time = ((self.total_size - self.completed_size) / self.completed_size * elapsed_time
                          if self.completed_size > 0 else 0)
        remaining_time_str = self.format_time(remaining_time)
        self.remaining_time_label['text'] = f"剩余时间: {remaining_time_str}"

    def format_time(self, seconds):
        # 格式化时间为小时:分钟:秒
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def calculate_total_backup_size(self):
        # 计算备份总大小的方法
        total_size = 0
        for item in self.backup_items:
            source = item['path']
            item_size = os.path.getsize(source) if os.path.isfile(source) else self.get_directory_size(source)
            total_size += item_size
        return total_size, len(self.backup_items)

    def get_directory_size(self, path):
        # 递归获取目录大小的方法
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total += os.path.getsize(fp)
        return total
        
    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = BackupManagerGUI()
    app.run()
