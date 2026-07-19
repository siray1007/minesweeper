"""扫雷游戏 - 登录 / 注册模块（嵌入主窗口）"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
from database import register_user, login_user
from lang import t, save_lang, LANG_OPTIONS, get_lang

_ICON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bomb32.png')
_BG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bg_pattern.png')

def _bomb_label(parent, text, font, **kw):
    f = tk.Frame(parent, bg=kw.get('bg', '#f0f0f0'))
    if os.path.exists(_ICON):
        img = tk.PhotoImage(file=_ICON); f.img = img
        tk.Label(f, image=img, bg=kw.get('bg', '#f0f0f0')).pack(side=tk.LEFT, padx=(0,6))
    tk.Label(f, text=text, font=font, bg=kw.get('bg', '#f0f0f0'), fg=kw.get('fg','#333')).pack(side=tk.LEFT)
    return f

class AuthFrame(tk.Frame):
    def __init__(self, parent, on_login):
        super().__init__(parent, bg='#f0f0f0')
        self.on_login = on_login
        if os.path.exists(_BG):
            self._bg = tk.PhotoImage(file=_BG)
            tk.Label(self, image=self._bg, bg='#f0f0f0').place(x=0,y=0,relwidth=1,relheight=1)
        self._show_login()
    def _clear(self):
        for w in self.winfo_children(): w.destroy()
    def _lang_selector(self):
        f = tk.Frame(self, bg='#f0f0f0'); f.place(x=10, y=10)
        cur_name = dict(LANG_OPTIONS).get(get_lang(), '简体中文')
        tk.Label(f, text=f'🌐 {cur_name}', font=('微软雅黑', 9, 'bold'), bg='#f0f0f0', fg='#555').pack(anchor='w')
        sorted_opts = sorted(LANG_OPTIONS, key=lambda x: x[0])
        var = tk.StringVar(value=cur_name)
        cb = ttk.Combobox(f, textvariable=var, values=[o[1] for o in sorted_opts], state='readonly', width=12, font=('微软雅黑', 9))
        cb.pack(pady=(2,0))
        def on_change(e=None):
            for code, name in sorted_opts:
                if name == var.get(): save_lang(code); self._refresh(); break
        cb.bind('<<ComboboxSelected>>', on_change)
        return f
    def _refresh(self):
        if hasattr(self, '_user'): self._show_login()
        else: self._show_register()
    def _show_login(self):
        self._clear(); self._lang_selector()
        _bomb_label(self, t('title'), ('微软雅黑', 26, 'bold'), bg='#f0f0f0', fg='#333').pack(pady=(50,5))
        tk.Label(self, text=t('login'), font=('微软雅黑', 14), bg='#f0f0f0', fg='#666').pack(pady=(0,25))
        f = tk.Frame(self, bg='#f0f0f0'); f.pack()
        tk.Label(f, text=t('username'), bg='#f0f0f0', font=('微软雅黑', 10)).pack()
        self._user = ttk.Entry(f, width=28, font=('微软雅黑', 11)); self._user.pack(pady=(5,10)); self._user.focus_set()
        tk.Label(f, text=t('password'), bg='#f0f0f0', font=('微软雅黑', 10)).pack()
        self._pwd = ttk.Entry(f, width=28, font=('微软雅黑', 11), show='●'); self._pwd.pack(pady=(5,15))
        ttk.Button(f, text=t('btn_login'), command=self._do_login, width=18).pack(pady=(5,5))
        link = tk.Frame(f, bg='#f0f0f0'); link.pack()
        tk.Label(link, text=t('no_account'), bg='#f0f0f0', font=('微软雅黑', 9)).pack(side=tk.LEFT)
        ttk.Button(link, text=t('to_register'), command=self._show_register).pack(side=tk.LEFT)
        self._pwd.bind('<Return>', lambda e: self._do_login())
    def _show_register(self):
        self._clear(); self._lang_selector()
        _bomb_label(self, t('title'), ('微软雅黑', 26, 'bold'), bg='#f0f0f0', fg='#333').pack(pady=(50,5))
        tk.Label(self, text=t('register'), font=('微软雅黑', 14), bg='#f0f0f0', fg='#666').pack(pady=(0,25))
        f = tk.Frame(self, bg='#f0f0f0'); f.pack()
        tk.Label(f, text=t('username'), bg='#f0f0f0', font=('微软雅黑', 10)).pack()
        self._reg_user = ttk.Entry(f, width=28, font=('微软雅黑', 11)); self._reg_user.pack(pady=(5,10)); self._reg_user.focus_set()
        tk.Label(f, text=t('pwd_hint'), bg='#f0f0f0', font=('微软雅黑', 10)).pack()
        self._reg_pwd = ttk.Entry(f, width=28, font=('微软雅黑', 11), show='●'); self._reg_pwd.pack(pady=(5,10))
        tk.Label(f, text=t('confirm_pwd'), bg='#f0f0f0', font=('微软雅黑', 10)).pack()
        self._reg_cfm = ttk.Entry(f, width=28, font=('微软雅黑', 11), show='●'); self._reg_cfm.pack(pady=(5,15))
        ttk.Button(f, text=t('btn_register'), command=self._do_register, width=18).pack(pady=(5,5))
        link = tk.Frame(f, bg='#f0f0f0'); link.pack()
        tk.Label(link, text=t('has_account'), bg='#f0f0f0', font=('微软雅黑', 9)).pack(side=tk.LEFT)
        ttk.Button(link, text=t('to_login'), command=self._show_login).pack(side=tk.LEFT)
        self._reg_cfm.bind('<Return>', lambda e: self._do_register())
    def _do_login(self):
        u, p = self._user.get(), self._pwd.get()
        if not u or not p: messagebox.showwarning(t('warn_empty'), t('warn_empty')); return
        ok, result = login_user(u, p)
        if ok: self.on_login(result)
        else: messagebox.showerror(t('login_fail'), result)
    def _do_register(self):
        u, p, c = self._reg_user.get(), self._reg_pwd.get(), self._reg_cfm.get()
        if p != c: messagebox.showerror(t('reg_fail'), t('pwd_mismatch')); return
        ok, msg = register_user(u, p)
        if ok: messagebox.showinfo(t('reg_ok'), t('reg_ok')); self._show_login()
        else: messagebox.showerror(t('reg_fail'), msg)
