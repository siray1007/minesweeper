"""
扫雷游戏 - 登录 / 注册模块（嵌入主窗口）
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import register_user, login_user

class AuthFrame(tk.Frame):
    def __init__(self,parent,on_login):
        super().__init__(parent,bg='#f0f0f0')
        self.on_login=on_login;self._show_login()
    def _clear(self):
        for w in self.winfo_children():w.destroy()
    def _show_login(self):
        self._clear()
        tk.Label(self,text="💣 扫雷游戏",font=('微软雅黑',26,'bold'),bg='#f0f0f0',fg='#333').pack(pady=(50,5))
        tk.Label(self,text="登录账号",font=('微软雅黑',14),bg='#f0f0f0',fg='#666').pack(pady=(0,25))
        f=tk.Frame(self,bg='#f0f0f0');f.pack()
        tk.Label(f,text="用户名",bg='#f0f0f0',font=('微软雅黑',10)).pack()
        self._user=ttk.Entry(f,width=28,font=('微软雅黑',11));self._user.pack(pady=(5,10));self._user.focus_set()
        tk.Label(f,text="密码",bg='#f0f0f0',font=('微软雅黑',10)).pack()
        self._pwd=ttk.Entry(f,width=28,font=('微软雅黑',11),show='●');self._pwd.pack(pady=(5,15))
        ttk.Button(f,text="登 录",command=self._do_login,width=18).pack(pady=(5,5))
        link=tk.Frame(f,bg='#f0f0f0');link.pack()
        tk.Label(link,text="还没有账号？",bg='#f0f0f0',font=('微软雅黑',9)).pack(side=tk.LEFT)
        ttk.Button(link,text="立即注册",command=self._show_register).pack(side=tk.LEFT)
        self._pwd.bind('<Return>',lambda e:self._do_login())
    def _show_register(self):
        self._clear()
        tk.Label(self,text="💣 扫雷游戏",font=('微软雅黑',26,'bold'),bg='#f0f0f0',fg='#333').pack(pady=(50,5))
        tk.Label(self,text="注册新账号",font=('微软雅黑',14),bg='#f0f0f0',fg='#666').pack(pady=(0,25))
        f=tk.Frame(self,bg='#f0f0f0');f.pack()
        tk.Label(f,text="用户名",bg='#f0f0f0',font=('微软雅黑',10)).pack()
        self._reg_user=ttk.Entry(f,width=28,font=('微软雅黑',11));self._reg_user.pack(pady=(5,10));self._reg_user.focus_set()
        tk.Label(f,text="密码（至少4位）",bg='#f0f0f0',font=('微软雅黑',10)).pack()
        self._reg_pwd=ttk.Entry(f,width=28,font=('微软雅黑',11),show='●');self._reg_pwd.pack(pady=(5,10))
        tk.Label(f,text="确认密码",bg='#f0f0f0',font=('微软雅黑',10)).pack()
        self._reg_cfm=ttk.Entry(f,width=28,font=('微软雅黑',11),show='●');self._reg_cfm.pack(pady=(5,15))
        ttk.Button(f,text="注 册",command=self._do_register,width=18).pack(pady=(5,5))
        link=tk.Frame(f,bg='#f0f0f0');link.pack()
        tk.Label(link,text="已有账号？",bg='#f0f0f0',font=('微软雅黑',9)).pack(side=tk.LEFT)
        ttk.Button(link,text="返回登录",command=self._show_login).pack(side=tk.LEFT)
        self._reg_cfm.bind('<Return>',lambda e:self._do_register())
    def _do_login(self):
        u,p=self._user.get(),self._pwd.get()
        if not u or not p:messagebox.showwarning("提示","请输入用户名和密码！");return
        ok,result=login_user(u,p)
        if ok:self.on_login(result)
        else:messagebox.showerror("登录失败",result)
    def _do_register(self):
        u,p,c=self._reg_user.get(),self._reg_pwd.get(),self._reg_cfm.get()
        if p!=c:messagebox.showerror("注册失败","两次密码输入不一致！");return
        ok,msg=register_user(u,p)
        if ok:messagebox.showinfo("注册成功",msg);self._show_login()
        else:messagebox.showerror("注册失败",msg)
