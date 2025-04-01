# 导入必要的库
from tkinter import *  # 导入tkinter GUI库的所有组件
from tkinter import ttk  # 导入ttk模块用于更现代的UI控件
import random  # 导入随机数生成模块
import time  # 导入时间模块用于模拟思考延迟
from PIL import Image, ImageTk  # 导入PIL库用于处理图片
import os  # 导入os模块用于处理文件路径
import json  # 导入json模块用于处理聊天历史
import uuid  # 导入uuid模块用于生成唯一ID
import tkinter.messagebox as messagebox  # 导入消息框模块用于确认删除

class ChatWindow:
    """问答对话窗口的主类，模仿DeepSeek Chat网站的设计"""
    def __init__(self, master):
        """初始化聊天窗口
        
        Args:
            master: tkinter根窗口对象
        """
        self.master = master  # 保存主窗口引用
        master.title("DeepSeek Chat")  # 修改窗口标题
        master.geometry('1400x800')  # 设置更大的窗口尺寸
        master.configure(bg='#111827')  # 使用深色背景，与DeepSeek相似
        master.minsize(800, 600)  # 设置最小窗口大小
        
        # 初始化保存的对话列表
        self.saved_conversations = {}
        self.current_conversation_id = str(uuid.uuid4())
        
        # 创建左侧边栏框架
        self.sidebar_frame = Frame(master, bg='#1F2937', width=250)
        self.sidebar_frame.pack(side=LEFT, fill=Y, padx=0, pady=0)
        self.sidebar_frame.pack_propagate(False)  # 防止框架大小变化
        
        # 在左侧边栏添加DeepSeek标题
        self.logo_label = Label(
            self.sidebar_frame, 
            text="DeepSeek Chat", 
            font=('Segoe UI', 18, 'bold'), 
            bg='#1F2937', 
            fg='#FFFFFF',
            pady=20
        )
        self.logo_label.pack(side=TOP, fill=X)
        
        # 创建"新对话"按钮
        self.new_chat_button = Button(
            self.sidebar_frame,
            text="+ 新对话",
            font=('Segoe UI', 12),
            bg='#2563EB',
            fg='#FFFFFF',
            activebackground='#1D4ED8',
            activeforeground='#FFFFFF',
            borderwidth=0,
            padx=10,
            pady=8,
            relief=FLAT,
            cursor="hand2",
            command=self.start_new_conversation
        )
        self.new_chat_button.pack(side=TOP, fill=X, padx=15, pady=10)
        
        # 添加标题：历史对话
        self.history_title = Label(
            self.sidebar_frame,
            text="历史对话",
            font=('Segoe UI', 12, 'bold'),
            bg='#1F2937',
            fg='#FFFFFF',
            anchor='w',
            padx=15,
            pady=10
        )
        self.history_title.pack(side=TOP, fill=X)
        
        # 创建历史对话的滚动区域
        self.history_canvas = Canvas(self.sidebar_frame, bg='#1F2937', highlightthickness=0)
        self.history_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 添加滚动条
        self.history_scrollbar = Scrollbar(self.sidebar_frame, orient=VERTICAL, command=self.history_canvas.yview)
        self.history_scrollbar.pack(side=RIGHT, fill=Y)
        
        # 配置画布
        self.history_canvas.configure(yscrollcommand=self.history_scrollbar.set)
        self.history_canvas.bind('<Configure>', lambda e: self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all")))
        
        # 创建框架放置历史记录
        self.history_frame = Frame(self.history_canvas, bg='#1F2937')
        self.history_canvas.create_window((0, 0), window=self.history_frame, anchor="nw", width=230)
        
        # 创建主聊天区域框架
        self.chat_frame = Frame(master, bg='#111827')
        self.chat_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # 创建主聊天区域的内部布局
        self.chat_inner_frame = Frame(self.chat_frame, bg='#111827')
        self.chat_inner_frame.pack(fill=BOTH, expand=True)
        
        # 聊天标题
        self.chat_title = Label(
            self.chat_inner_frame,
            text="新对话",
            font=('Segoe UI', 16, 'bold'),
            bg='#111827',
            fg='#FFFFFF',
            pady=15,
            cursor="hand2"  # 添加指针样式以提示可以点击
        )
        self.chat_title.pack(side=TOP, fill=X)
        
        # 给标题添加点击事件，使其可以重命名
        self.chat_title.bind("<Button-1>", self.rename_current_conversation)
        
        # 添加鼠标悬停效果
        self.chat_title.bind("<Enter>", lambda e: self.chat_title.config(fg='#60A5FA'))
        self.chat_title.bind("<Leave>", lambda e: self.chat_title.config(fg='#FFFFFF'))
        
        # 创建消息显示区域
        self.conversation_frame = Frame(self.chat_inner_frame, bg='#111827')
        self.conversation_frame.pack(side=TOP, fill=BOTH, expand=True, padx=20, pady=10)
        
        # 创建聊天消息显示区域
        self.conversation = Text(
            self.conversation_frame,
            state='disabled',
            bg='#111827',
            fg='#E5E7EB',
            font=('Segoe UI', 12),
            wrap=WORD,
            borderwidth=0,
            padx=20,
            pady=20,
            highlightthickness=0
        )
        self.conversation.pack(fill=BOTH, expand=True)
        
        # 添加滚动条
        self.scrollbar = Scrollbar(self.conversation_frame, command=self.conversation.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.conversation.config(yscrollcommand=self.scrollbar.set)
        
        # 创建底部输入区域框架 - 固定在底部
        self.bottom_frame = Frame(self.chat_frame, bg='#111827', height=150)
        self.bottom_frame.pack(side=BOTTOM, fill=X)
        self.bottom_frame.pack_propagate(False)  # 防止框架大小变化
        
        # 创建输入区域
        self.input_frame = Frame(self.bottom_frame, bg='#1F2937', height=120)
        self.input_frame.pack(fill=X, padx=20, pady=20)
        
        # 创建文本输入框，而不是Entry
        self.user_input = Text(
            self.input_frame,
            font=('Segoe UI', 12),
            bg='#1F2937',
            fg='#E5E7EB',
            insertbackground='#E5E7EB',
            borderwidth=1,
            relief=SOLID,
            height=3,
            padx=15,
            pady=15
        )
        self.user_input.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        # 创建发送按钮
        self.send_button = Button(
            self.input_frame,
            text="发送",
            command=self.send_message,
            font=('Segoe UI', 12, 'bold'),
            bg='#2563EB',
            fg='#FFFFFF',
            activebackground='#1D4ED8',
            activeforeground='#FFFFFF',
            borderwidth=0,
            relief=FLAT,
            padx=25,
            pady=10,
            cursor="hand2"
        )
        self.send_button.pack(side=RIGHT, padx=(10, 0))
        
        # 绑定Enter键到send_message方法，但允许Shift+Enter换行
        self.user_input.bind('<Return>', self.handle_return)
        
        # 绑定窗口大小改变事件
        self.master.bind('<Configure>', self.on_window_resize)
        
        # 显示初始问候消息
        self.display_message("DeepSeek", "欢迎使用 DeepSeek Chat。我是您的AI助手，可以回答问题、提供信息、帮助解决问题或进行创意讨论。请问有什么我可以帮您的吗？")
        
        # 设置窗口图标
        self.set_window_icon()
        
        # 初始化聊天历史
        self.chat_history = []
    
    def on_window_resize(self, event):
        """处理窗口大小改变事件"""
        if event.widget == self.master:
            # 确保输入框始终可见
            window_height = event.height
            # 如果窗口高度小于特定值，调整底部框架高度
            if window_height < 500:  # 你可以调整这个阈值
                self.bottom_frame.configure(height=100)
            else:
                self.bottom_frame.configure(height=150)
    
    def start_new_conversation(self):
        """开始新的对话，保存当前对话到侧边栏"""
        # 检查当前对话是否有消息
        if len(self.chat_history) > 0 and self.current_conversation_id not in self.saved_conversations:
            # 生成对话标题（使用第一条用户消息）
            title = "新对话"
            for msg in self.chat_history:
                if msg["role"] == "user":
                    # 截取前20个字符作为标题
                    title = msg["content"][:20] + ("..." if len(msg["content"]) > 20 else "")
                    break
            
            # 保存当前对话
            self.saved_conversations[self.current_conversation_id] = {
                "title": title,
                "history": self.chat_history.copy(),
                "timestamp": time.time()
            }
            
            # 添加到侧边栏
            self.add_conversation_to_sidebar(self.current_conversation_id, title)
        
        # 清空聊天区域
        self.conversation.configure(state='normal')
        self.conversation.delete("1.0", END)
        self.conversation.configure(state='disabled')
        
        # 重置聊天历史
        self.chat_history = []
        
        # 生成新的对话ID
        self.current_conversation_id = str(uuid.uuid4())
        
        # 更新标题
        self.chat_title.config(text="新对话")
        
        # 显示欢迎消息
        self.display_message("DeepSeek", "欢迎开始新的对话！请问有什么我可以帮您的吗？")
    
    def add_conversation_to_sidebar(self, conversation_id, title):
        """将对话添加到侧边栏
        
        Args:
            conversation_id: 对话ID
            title: 对话标题
        """
        # 创建对话项目
        conversation_item = Label(
            self.history_frame,
            text=title,
            font=('Segoe UI', 11),
            bg='#1F2937',
            fg='#D1D5DB',
            anchor='w',
            padx=10,
            pady=8,
            cursor="hand2"
        )
        # 为标签添加conversation_id属性，方便查找
        conversation_item.conversation_id = conversation_id
        conversation_item.pack(side=TOP, fill=X, pady=2)
        
        # 添加鼠标悬停效果
        conversation_item.bind("<Enter>", lambda e: e.widget.config(bg='#374151'))
        conversation_item.bind("<Leave>", lambda e: e.widget.config(bg='#1F2937'))
        
        # 绑定点击事件以加载对话
        conversation_item.bind("<Button-1>", lambda e, cid=conversation_id: self.load_conversation(cid))
        
        # 添加右键菜单功能
        conversation_item.bind("<Button-3>", lambda e, cid=conversation_id, item=conversation_item: self.show_conversation_menu(e, cid, item))
        
        # 更新滚动区域
        self.history_frame.update_idletasks()
        self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))
    
    def load_conversation(self, conversation_id):
        """加载历史对话
        
        Args:
            conversation_id: 要加载的对话ID
        """
        # 如果当前对话有内容，先保存当前对话
        if len(self.chat_history) > 0 and self.current_conversation_id not in self.saved_conversations:
            # 生成对话标题
            title = "新对话"
            for msg in self.chat_history:
                if msg["role"] == "user":
                    title = msg["content"][:20] + ("..." if len(msg["content"]) > 20 else "")
                    break
            
            # 保存当前对话
            self.saved_conversations[self.current_conversation_id] = {
                "title": title,
                "history": self.chat_history.copy(),
                "timestamp": time.time()
            }
            
            # 添加到侧边栏
            self.add_conversation_to_sidebar(self.current_conversation_id, title)
        
        # 获取要加载的对话
        conversation = self.saved_conversations.get(conversation_id)
        if conversation:
            # 更新当前对话ID
            self.current_conversation_id = conversation_id
            
            # 更新标题
            self.chat_title.config(text=conversation["title"])
            
            # 清空聊天区域
            self.conversation.configure(state='normal')
            self.conversation.delete("1.0", END)
            self.conversation.configure(state='disabled')
            
            # 加载聊天历史
            self.chat_history = conversation["history"].copy()
            
            # 显示消息
            for msg in self.chat_history:
                if msg["role"] == "user":
                    self.display_message("你", msg["content"], no_history=True)
                else:
                    self.display_message("DeepSeek", msg["content"], no_history=True)
        
    def handle_return(self, event):
        """处理按下回车键事件"""
        if event.state & 0x1:  # Shift键被按下
            return  # 允许默认行为 (换行)
        else:
            self.send_message()
            return "break"  # 防止默认行为
    
    def add_history_item(self, title):
        """添加一个聊天历史项目"""
        history_item = Label(
            self.history_frame,
            text=title,
            font=('Segoe UI', 11),
            bg='#1F2937',
            fg='#D1D5DB',
            anchor='w',
            padx=10,
            pady=8,
            cursor="hand2"
        )
        history_item.pack(side=TOP, fill=X, pady=2)
        # 添加鼠标悬停效果
        history_item.bind("<Enter>", lambda e: e.widget.config(bg='#374151'))
        history_item.bind("<Leave>", lambda e: e.widget.config(bg='#1F2937'))
    
    def set_window_icon(self):
        """设置窗口图标"""
        try:
            # 假设图标文件在 photos 目录下
            icon_path = os.path.join(os.path.dirname(__file__), 'photos', 'icon.png')
            if os.path.exists(icon_path):
                icon = Image.open(icon_path)
                photo = ImageTk.PhotoImage(icon)
                self.master.iconphoto(True, photo)
        except Exception as e:
            print(f"无法加载图标: {e}")
    
    def send_message(self):
        """处理发送消息逻辑"""
        message = self.user_input.get("1.0", END).strip()
        if message:
            self.display_message("你", message)
            self.user_input.delete("1.0", END)
            # 保存到聊天历史
            self.chat_history.append({"role": "user", "content": message})
            
            # 如果是第一条消息，更新对话标题
            if len(self.chat_history) == 1:
                title = message[:20] + ("..." if len(message) > 20 else "")
                self.chat_title.config(text=title)
            
            # 生成并显示系统响应
            self.respond_to_message(message)
    
    def respond_to_message(self, message):
        """生成并显示系统响应
        
        Args:
            message: 用户发送的消息内容
        """
        # 模拟思考延迟
        self.master.after(1000, lambda: self.start_typing_animation())
        
        # 模拟生成回复的时间
        response_time = 2000  # 2秒后回复
        
        # 设置固定回复
        response = "服务器繁忙，请稍后重试。"
        
        # 延迟后显示回复
        self.master.after(response_time, lambda: self.finish_typing_and_respond(response))
    
    def start_typing_animation(self):
        """开始显示打字动画"""
        self.display_message("DeepSeek", "思考中...", is_typing=True)
    
    def finish_typing_and_respond(self, response):
        """完成打字动画并显示回复"""
        # 移除打字动画
        self.conversation.configure(state='normal')
        # 查找最后一条消息的开始位置
        last_msg_pos = self.conversation.search("DeepSeek: 思考中...", "1.0", END)
        if last_msg_pos:
            # 获取行号
            line_num = last_msg_pos.split('.')[0]
            # 删除该行到下一行
            self.conversation.delete(f"{line_num}.0", f"{int(line_num)+1}.0")
            # 在同一位置添加"思考完成"
            self.conversation.insert(f"{line_num}.0", "DeepSeek: 思考完成\n", 'ai_complete')
        self.conversation.configure(state='disabled')
        
        # 稍微延迟显示实际回复
        self.master.after(500, lambda: self.show_final_response(response))
    
    def show_final_response(self, response):
        """显示最终回复"""
        # 显示实际回复
        self.display_message("DeepSeek", response)
        # 保存到聊天历史
        self.chat_history.append({"role": "assistant", "content": response})
    
    def display_message(self, sender, message, is_typing=False, no_history=False):
        """在对话区域显示消息
        
        Args:
            sender: 发送者名称
            message: 要显示的消息内容
            is_typing: 是否是打字动画
            no_history: 是否不添加到历史记录
        """
        self.conversation.configure(state='normal')
        
        # 添加分隔符
        if self.conversation.get("1.0", END).strip():
            self.conversation.insert(END, "\n\n")
        
        # 设置样式标签
        if sender == "你":
            name_tag = 'user_name'
            msg_tag = 'user_message'
            sender_display = "你"
        else:
            name_tag = 'ai_name'
            msg_tag = 'ai_message'
            sender_display = "DeepSeek"
        
        # 插入发送者名称
        self.conversation.insert(END, f"{sender_display}: ", name_tag)
        
        # 插入消息内容
        self.conversation.insert(END, message, msg_tag)
        
        # 配置标签样式
        self.conversation.tag_configure('user_name', foreground='#60A5FA', font=('Segoe UI', 12, 'bold'))
        self.conversation.tag_configure('user_message', foreground='#E5E7EB', font=('Segoe UI', 12))
        self.conversation.tag_configure('ai_name', foreground='#34D399', font=('Segoe UI', 12, 'bold'))
        self.conversation.tag_configure('ai_message', foreground='#E5E7EB', font=('Segoe UI', 12))
        self.conversation.tag_configure('ai_complete', foreground='#34D399', font=('Segoe UI', 12))
        
        self.conversation.configure(state='disabled')
        self.conversation.see(END)
    
    def show_conversation_menu(self, event, conversation_id, item):
        """显示对话右键菜单
        
        Args:
            event: 鼠标事件
            conversation_id: 对话ID
            item: 对话标签控件
        """
        # 创建右键菜单
        context_menu = Menu(self.master, tearoff=0, bg='#1F2937', fg='#D1D5DB', 
                           activebackground='#374151', activeforeground='#FFFFFF',
                           font=('Segoe UI', 10))
        
        # 添加重命名选项
        context_menu.add_command(label="重命名", 
                               command=lambda: self.rename_conversation(conversation_id, item))
        
        # 添加删除选项
        context_menu.add_command(label="删除对话", 
                               command=lambda: self.delete_conversation(conversation_id, item))
        
        # 在鼠标位置显示菜单
        context_menu.tk_popup(event.x_root, event.y_root)
    
    def rename_conversation(self, conversation_id, item):
        """重命名对话
        
        Args:
            conversation_id: 要重命名的对话ID
            item: 对话的标签控件
        """
        # 获取当前标题
        current_title = item.cget("text")
        
        # 创建顶层窗口用于重命名
        rename_window = Toplevel(self.master)
        rename_window.title("重命名对话")
        rename_window.configure(bg='#1F2937')
        rename_window.resizable(False, False)
        
        # 设置模态窗口
        rename_window.transient(self.master)
        rename_window.grab_set()
        
        # 居中显示
        window_width = 300
        window_height = 120
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        rename_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 添加标签
        Label(
            rename_window,
            text="请输入新名称：",
            font=('Segoe UI', 11),
            bg='#1F2937',
            fg='#FFFFFF',
            pady=10
        ).pack(padx=20)
        
        # 添加输入框
        entry = Entry(
            rename_window,
            font=('Segoe UI', 11),
            bg='#374151',
            fg='#FFFFFF',
            insertbackground='#FFFFFF',
            width=30
        )
        entry.pack(padx=20, pady=5)
        entry.insert(0, current_title)
        entry.select_range(0, END)  # 选中所有文本
        entry.focus_set()  # 设置焦点
        
        # 创建按钮框架
        button_frame = Frame(rename_window, bg='#1F2937')
        button_frame.pack(pady=10)
        
        # 定义确认重命名的函数
        def confirm_rename():
            new_title = entry.get().strip()
            # 检查是否为空
            if not new_title:
                # 如果为空，则恢复原名称
                new_title = current_title
            
            # 更新界面显示
            item.config(text=new_title)
            
            # 更新保存的对话信息
            if conversation_id in self.saved_conversations:
                self.saved_conversations[conversation_id]["title"] = new_title
            
            # 如果是当前对话，更新标题
            if conversation_id == self.current_conversation_id:
                self.chat_title.config(text=new_title)
            
            # 关闭窗口
            rename_window.destroy()
        
        # 添加确认和取消按钮
        Button(
            button_frame,
            text="确认",
            font=('Segoe UI', 11),
            bg='#2563EB',
            fg='#FFFFFF',
            activebackground='#1D4ED8',
            activeforeground='#FFFFFF',
            padx=10,
            command=confirm_rename
        ).pack(side=LEFT, padx=5)
        
        Button(
            button_frame,
            text="取消",
            font=('Segoe UI', 11),
            bg='#4B5563',
            fg='#FFFFFF',
            activebackground='#374151',
            activeforeground='#FFFFFF',
            padx=10,
            command=rename_window.destroy
        ).pack(side=LEFT, padx=5)
        
        # 绑定回车键
        entry.bind("<Return>", lambda e: confirm_rename())
        
        # 等待窗口关闭
        self.master.wait_window(rename_window)
    
    def delete_conversation(self, conversation_id, item):
        """删除对话
        
        Args:
            conversation_id: 要删除的对话ID
            item: 对话的标签控件
        """
        # 显示确认对话框
        confirm = messagebox.askyesno("确认删除", "确定要删除这个对话吗？", 
                                    parent=self.master)
        
        if confirm:
            # 从保存的对话字典中删除
            if conversation_id in self.saved_conversations:
                del self.saved_conversations[conversation_id]
            
            # 从UI中移除对话项
            item.destroy()
            
            # 如果删除的是当前对话，则开始新对话
            if conversation_id == self.current_conversation_id:
                self.start_new_conversation()
            
            # 更新滚动区域
            self.history_frame.update_idletasks()
            self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))
    
    def rename_current_conversation(self, event=None):
        """重命名当前对话的标题
        
        Args:
            event: 事件对象
        """
        # 如果当前没有对话或是新对话且没有消息，则不允许重命名
        if len(self.chat_history) == 0:
            return
            
        # 获取当前标题
        current_title = self.chat_title.cget("text")
        
        # 创建顶层窗口用于重命名
        rename_window = Toplevel(self.master)
        rename_window.title("重命名对话")
        rename_window.configure(bg='#1F2937')
        rename_window.resizable(False, False)
        
        # 设置模态窗口
        rename_window.transient(self.master)
        rename_window.grab_set()
        
        # 居中显示
        window_width = 300
        window_height = 120
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        rename_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 添加标签
        Label(
            rename_window,
            text="请输入新名称：",
            font=('Segoe UI', 11),
            bg='#1F2937',
            fg='#FFFFFF',
            pady=10
        ).pack(padx=20)
        
        # 添加输入框
        entry = Entry(
            rename_window,
            font=('Segoe UI', 11),
            bg='#374151',
            fg='#FFFFFF',
            insertbackground='#FFFFFF',
            width=30
        )
        entry.pack(padx=20, pady=5)
        entry.insert(0, current_title)
        entry.select_range(0, END)  # 选中所有文本
        entry.focus_set()  # 设置焦点
        
        # 创建按钮框架
        button_frame = Frame(rename_window, bg='#1F2937')
        button_frame.pack(pady=10)
        
        # 定义确认重命名的函数
        def confirm_rename():
            new_title = entry.get().strip()
            # 检查是否为空
            if not new_title:
                # 如果为空，则恢复原名称
                new_title = current_title
            
            # 更新标题显示
            self.chat_title.config(text=new_title)
            
            # 更新保存的对话信息
            if self.current_conversation_id in self.saved_conversations:
                self.saved_conversations[self.current_conversation_id]["title"] = new_title
                
                # 同时更新侧边栏中的对话标题
                for child in self.history_frame.winfo_children():
                    if isinstance(child, Label) and hasattr(child, 'conversation_id') and child.conversation_id == self.current_conversation_id:
                        child.config(text=new_title)
                        break
            
            # 关闭窗口
            rename_window.destroy()
        
        # 添加确认和取消按钮
        Button(
            button_frame,
            text="确认",
            font=('Segoe UI', 11),
            bg='#2563EB',
            fg='#FFFFFF',
            activebackground='#1D4ED8',
            activeforeground='#FFFFFF',
            padx=10,
            command=confirm_rename
        ).pack(side=LEFT, padx=5)
        
        Button(
            button_frame,
            text="取消",
            font=('Segoe UI', 11),
            bg='#4B5563',
            fg='#FFFFFF',
            activebackground='#374151',
            activeforeground='#FFFFFF',
            padx=10,
            command=rename_window.destroy
        ).pack(side=LEFT, padx=5)
        
        # 绑定回车键
        entry.bind("<Return>", lambda e: confirm_rename())
        
        # 等待窗口关闭
        self.master.wait_window(rename_window)

# 创建tkinter根窗口
root = Tk()
# 创建聊天窗口实例
chat_app = ChatWindow(root)
# 进入主事件循环
root.mainloop()