"""
扫雷游戏 - 登录 / 注册模块
提供用户认证的图形界面
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import register_user, login_user


class AuthWindow(tk.Toplevel):
    """登录 / 注册窗口"""

    def __init__(self, master, on_success):
        super().__init__(master)
        self.on_success = on_success
        self.title("扫雷 - 登录")
        self.resizable(False, False)
        self.configure(bg='#f0f0f0')

        w, h = 380, 420
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws - w) // 2
        y = (hs - h) // 2
        self.geometry(f'{w}x{h}+{x}+{y}')

        self.create_login_ui()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # ── 界面清理 ──────────────────────────────────────────

    def _clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    # ── 登录界面 ──────────────────────────────────────────

    def create_login_ui(self):
        self._clear()
        self.title("扫雷 - 登录")

        tk.Label(self, text="💣 扫雷游戏", font=('微软雅黑', 22, 'bold'),
                 bg='#f0f0f0', fg='#333').pack(pady=(30, 5))
        tk.Label(self, text="登录账号", font=('微软雅黑', 14),
                 bg='#f0f0f0', fg='#666').pack(pady=(0, 20))

        tk.Label(self, text="用户名", bg='#f0f0f0', font=('微软雅黑', 10)).pack()
        self.login_username = ttk.Entry(self, width=30, font=('微软雅黑', 11))
        self.login_username.pack(pady=(5, 10))
        self.login_username.focus_set()

        tk.Label(self, text="密码", bg='#f0f0f0', font=('微软雅黑', 10)).pack()
        self.login_password = ttk.Entry(self, width=30, font=('微软雅黑', 11), show='●')
        self.login_password.pack(pady=(5, 10))

        ttk.Button(self, text="登 录", command=self.do_login, width=20).pack(pady=(10, 5))

        link = tk.Frame(self, bg='#f0f0f0')
        link.pack(pady=5)
        tk.Label(link, text="还没有账号？", bg='#f0f0f0', font=('微软雅黑', 9)).pack(side=tk.LEFT)
        ttk.Button(link, text="立即注册", command=self.create_register_ui).pack(side=tk.LEFT)

        self.login_password.bind('<Return>', lambda e: self.do_login())

    # ── 注册界面 ──────────────────────────────────────────

    def create_register_ui(self):
        self._clear()
        self.title("扫雷 - 注册")

        tk.Label(self, text="💣 扫雷游戏", font=('微软雅黑', 22, 'bold'),
                 bg='#f0f0f0', fg='#333').pack(pady=(30, 5))
        tk.Label(self, text="注册新账号", font=('微软雅黑', 14),
                 bg='#f0f0f0', fg='#666').pack(pady=(0, 20))

        tk.Label(self, text="用户名", bg='#f0f0f0', font=('微软雅黑', 10)).pack()
        self.reg_username = ttk.Entry(self, width=30, font=('微软雅黑', 11))
        self.reg_username.pack(pady=(5, 10))
        self.reg_username.focus_set()

        tk.Label(self, text="密码（至少 4 位）", bg='#f0f0f0', font=('微软雅黑', 10)).pack()
        self.reg_password = ttk.Entry(self, width=30, font=('微软雅黑', 11), show='●')
        self.reg_password.pack(pady=(5, 10))

        tk.Label(self, text="确认密码", bg='#f0f0f0', font=('微软雅黑', 10)).pack()
        self.reg_confirm = ttk.Entry(self, width=30, font=('微软雅黑', 11), show='●')
        self.reg_confirm.pack(pady=(5, 10))

        ttk.Button(self, text="注 册", command=self.do_register, width=20).pack(pady=(10, 5))

        link = tk.Frame(self, bg='#f0f0f0')
        link.pack(pady=5)
        tk.Label(link, text="已有账号？", bg='#f0f0f0', font=('微软雅黑', 9)).pack(side=tk.LEFT)
        ttk.Button(link, text="返回登录", command=self.create_login_ui).pack(side=tk.LEFT)

        self.reg_confirm.bind('<Return>', lambda e: self.do_register())

    # ── 业务逻辑 ──────────────────────────────────────────

    def do_login(self):
        username = self.login_username.get()
        password = self.login_password.get()
        if not username or not password:
            messagebox.showwarning("提示", "请输入用户名和密码！")
            return

        success, result = login_user(username, password)
        if success:
            self.destroy()
            self.on_success(result)
        else:
            messagebox.showerror("登录失败", result)

    def do_register(self):
        username = self.reg_username.get()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()

        if password != confirm:
            messagebox.showerror("注册失败", "两次密码输入不一致！")
            return

        success, msg = register_user(username, password)
        if success:
            messagebox.showinfo("注册成功", msg)
            self.create_login_ui()
        else:
            messagebox.showerror("注册失败", msg)
