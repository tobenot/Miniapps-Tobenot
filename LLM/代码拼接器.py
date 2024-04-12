import tkinter as tk
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

        # 文件名显示框架
        self.file_names_frame = Frame(master)
        self.file_names_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky='w')

        master.columnconfigure(1, weight=1)
        master.rowconfigure(1, weight=1)
        
        self.file_paths = []
        self.file_labels = []

    def add_files(self):
        file_paths = filedialog.askopenfilenames(
            title='选择文件',
            filetypes=(('C++ Source Files', '*.cpp;*.h'), ('All Files', '*.*'))
        )

        if file_paths:
            self.file_paths.extend(file_paths)

            for file_path in file_paths:
                file_label = Label(self.file_names_frame, text=basename(file_path))
                file_label.pack(anchor="w")
                self.file_labels.append(file_label)

            self.update_content()

    def update_content(self):
        self.text_area.delete('1.0', tk.END)  # 清空文本框内容

        for file_path in self.file_paths:
            try:
                # 利用codecs模块打开文件，指定编码为utf-8
                with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    content = "\n" + self.prefix_entry.get() + "\n" + content + "\n" + self.suffix_entry.get() + "\n"
                    self.text_area.insert(tk.END, content + '\n\n')
            except Exception as e:
                tk.messagebox.showerror("错误", f"无法读取文件 {file_path}:\n{e}")
                self.file_paths.remove(file_path)  # 移除无法读取的文件

if __name__ == '__main__':
    root = tk.Tk()
    app = ConcatenateApp(root)
    root.mainloop()
