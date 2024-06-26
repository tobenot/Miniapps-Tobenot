import tkinter as tk
from tkinter import ttk
import codecs
from tkinter import filedialog, scrolledtext, Entry, Label, Button, Frame, messagebox
from os.path import basename

class ConcatenateApp:
    def __init__(self, master):
        self.master = master
        self.master.title("代码拼接器")
        master.geometry('1000x618')  # 设置初始大小

        self.intro_label = Label(master, text="欢迎使用代码拼接器！", wraplength=550, justify="left")
        self.intro_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,0), sticky='w')
        
        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        self.text_area.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky='nsew')

        # 按钮框架
        self.buttons_frame = Frame(master)
        self.buttons_frame.grid(row=2, column=0, padx=10, pady=5, sticky='w')

        self.add_files_button = Button(self.buttons_frame, text="添加文件", command=self.add_files)
        self.add_files_button.pack(side=tk.LEFT, padx=(0, 20))

        self.update_button = Button(self.buttons_frame, text='更新内容', command=self.update_content)
        self.update_button.pack(side=tk.RIGHT)

        self.prefix_label = Label(master, text="前缀:")
        self.prefix_label.grid(row=3, column=0, padx=10, pady=(5,2), sticky='w')

        self.prefix_entry = Entry(master)
        self.prefix_entry.grid(row=3, column=1, padx=10, pady=(5,2), sticky='we')
        self.prefix_entry.insert(0, "接下来我会给你一系列代码：")

        self.suffix_label = Label(master, text="后缀:")
        self.suffix_label.grid(row=4, column=0, padx=10, pady=2, sticky='w')

        self.suffix_entry = Entry(master)
        self.suffix_entry.grid(row=4, column=1, padx=10, pady=2, sticky='we')
        self.suffix_entry.insert(0, "请你向我解释以上代码的结构。")

        # 文件名显示框架，修改部分开头
        self.file_names_frame = Frame(master)
        self.file_names_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky='nsew')
        
        self.scrollbar = tk.Scrollbar(self.file_names_frame) # 使用tk.Scrollbar
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y) # 使用tk的方向常量

        self.file_listbox = tk.Listbox(self.file_names_frame, yscrollcommand=self.scrollbar.set) # 使用tk.Listbox
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.file_listbox.yview)
        
        self.file_paths = []
        master.columnconfigure(1, weight=1)
        master.rowconfigure(1, weight=1)
        
        self.file_paths = []
        self.file_labels = []

    def add_files(self):
        file_paths = filedialog.askopenfilenames(
            title='选择文件',
            filetypes=(('All Files', '*.*'), ('C++ Source Files', '*.cpp;*.h'))
        )

        if file_paths:
            self.file_paths.extend(file_paths)

            for file_path in file_paths:
                self.file_listbox.insert(tk.END, basename(file_path)) # 使用tk.END

            self.update_content()

    def update_content(self):
        self.text_area.delete('1.0', tk.END)  # 清空文本框内容

        all_content = ""  # 初始化一个空字符串，用于存储所有文件内容

        for file_path in self.file_paths:
            try:
                file_name = basename(file_path)  # 提取文件名
                with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    all_content += f"# {file_name}\n{content}\n\n"  # 将文件名添加到文件内容前
            except Exception as e:
                tk.messagebox.showerror("错误", f"无法读取文件 {file_path}:\n{e}")
                self.file_paths.remove(file_path)  # 移除无法读取的文件

        # 在所有文件内容前后分别添加前缀和后缀
        all_content = self.prefix_entry.get() + "\n" + all_content + self.suffix_entry.get()

        self.text_area.insert(tk.END, all_content)  # 将最终内容显示在文本框中

        # 文本复制到粘贴板
        self.master.clipboard_clear()
        self.master.clipboard_append(all_content)

if __name__ == '__main__':
    root = tk.Tk()
    app = ConcatenateApp(root)
    root.mainloop()