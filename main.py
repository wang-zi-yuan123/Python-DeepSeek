# 导入必要的库
from tkinter import *  # 导入tkinter GUI库的所有组件
import random  # 导入随机数生成模块
import time  # 导入时间模块用于模拟思考延迟

class ChatWindow:
    """问答对话窗口的主类"""
    def __init__(self, master):
        """初始化聊天窗口
        
        Args:
            master: tkinter根窗口对象
        """
        self.master = master  # 保存主窗口引用
        master.title("Deepseek 智能助手")  # 修改窗口标题为Deepseek相关
        master.geometry('600x400')  # 设置窗口大小600x400像素
        master.configure(bg='#1E3A8A')  # 使用深蓝色作为背景颜色
        
        
        # 创建对话显示区域(Text组件)
        self.conversation = Text(master, state='disabled', bg='#ffffff', fg='#1E3A8A', font=('Segoe UI', 12, 'bold'), wrap=WORD, borderwidth=2, relief=GROOVE)
        self.conversation.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        
        # 添加滚动条
        scrollbar = Scrollbar(master, command=self.conversation.yview)
        scrollbar.grid(row=0, column=2, sticky='ns')
        self.conversation.config(yscrollcommand=scrollbar.set)
        
        # 创建用户输入框(Entry组件)，宽度50字符
        self.user_input = Entry(master, width=50, font=('Segoe UI', 12), bg='#ffffff', fg='#1E3A8A', borderwidth=2, relief=GROOVE)
        self.user_input.grid(row=1, column=0, padx=10, pady=10, sticky='ew')
        
        # 绑定Enter键到send_message方法
        self.user_input.bind('<Return>', lambda event: self.send_message())
        
        # 创建发送按钮，点击时调用send_message方法
        self.send_button = Button(master, text="发送", command=self.send_message, font=('Segoe UI', 12, 'bold'), bg='#1E3A8A', fg='#ffffff', activebackground='#162C62', borderwidth=2, relief=RAISED)
        self.send_button.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        
        # 配置网格布局权重，使对话区域可以随窗口缩放
        master.grid_rowconfigure(0, weight=1)  # 第0行可伸缩
        master.grid_columnconfigure(0, weight=1)  # 第0列可伸缩
        master.grid_columnconfigure(1, weight=1)  # 第1列可伸缩
        
        # 显示初始问候消息
        self.display_message("Deepseek", "你好！我是Deepseek智能助手，请问有什么可以帮助你的吗？")
    
    def send_message(self):
        """处理发送消息逻辑"""
        # 获取用户输入的消息
        message = self.user_input.get()
        if message:  # 如果消息不为空
            # 在对话区域显示用户消息
            self.display_message("你", message)
            # 清空输入框
            self.user_input.delete(0, END)
            # 生成并显示系统响应
            self.respond_to_message(message)
    
    def respond_to_message(self, message):
        """生成并显示系统响应
        
        Args:
            message: 用户发送的消息内容
        """
        # 模拟思考延迟
        time.sleep(2)
        # 显示系统响应
        self.display_message("Deepseek", "服务器繁忙，请稍后重试")
    
    def display_message(self, sender, message):
        """在对话区域显示消息
        
        Args:
            sender: 发送者名称(你/系统)
            message: 要显示的消息内容
        """
        # 临时启用Text组件以插入内容
        self.conversation.configure(state='normal')
        # 在末尾插入消息，格式为"发送者: 消息内容"
        self.conversation.insert(END, f"{sender}: {message}\n")
        # 重新禁用Text组件
        self.conversation.configure(state='disabled')
        # 自动滚动到最新消息
        self.conversation.see(END)

# 创建tkinter根窗口
root = Tk()
# 创建聊天窗口实例
chat_app = ChatWindow(root)
# 进入主事件循环
root.mainloop()