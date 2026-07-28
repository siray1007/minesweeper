"""扫雷 - 登录 / 注册模块"""
import tkinter as tk
from tkinter import messagebox
import os
from database import register_user, login_user
from lang import t, save_lang, LANG_OPTIONS, get_lang

_ICON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bomb32.png')

def _hover_btn(btn, normal, hover):
    btn.bind('<Enter>', lambda e: btn.configure(bg=hover))
    btn.bind('<Leave>', lambda e: btn.configure(bg=normal))

class AuthFrame(tk.Frame):
    def __init__(self, parent, on_login):
        super().__init__(parent, bg='#0f0f23')
        self.on_login = on_login; self._show_login()
    def _clear(self):
        for w in self.winfo_children(): w.destroy()
    def _lang_selector(self):
        f = tk.Frame(self, bg='#0f0f23'); f.place(x=16, y=16)
        names = [o[1] for o in LANG_OPTIONS]
        cur = dict(LANG_OPTIONS).get(get_lang(), names[0])
        var = tk.StringVar(value=cur)
        mb = tk.Menubutton(f, textvariable=var, font=('微软雅黑', 9), bg='#1a1a2e', fg='#e94560', activebackground='#e94560', activeforeground='white', relief='flat', bd=4, padx=8, pady=2, cursor='hand2', indicatoron=True)
        mb.bind('<Enter>', lambda e: mb.configure(bg='#253350'))
        mb.bind('<Leave>', lambda e: mb.configure(bg='#1a1a2e'))
        mb.pack()
        menu = tk.Menu(mb, tearoff=0, bg='#1a1a2e', fg='#e0e0e0', activebackground='#e94560', activeforeground='white', font=('微软雅黑', 9))
        for code, name in LANG_OPTIONS:
            menu.add_command(label=name, command=lambda c=code, n=name, v=var: (save_lang(c), v.set(n), self._refresh()))
        mb.configure(menu=menu)
    def _refresh(self):
        if hasattr(self, '_user'): self._show_login()
        else: self._show_register()
    def _card(self):
        card = tk.Frame(self, bg='#0f3460', bd=0); inner = tk.Frame(card, bg='#16213e')
        inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        return card, inner
    def _show_login(self):
        self._clear(); self._lang_selector()
        card, f = self._card(); card.place(relx=0.5, rely=0.5, anchor='center', width=420, height=460)
        if os.path.exists(_ICON):
            img = tk.PhotoImage(file=_ICON); f.img = img
            tk.Label(f, image=img, bg='#16213e').pack(pady=(35, 5))
        tk.Label(f, text=t('title'), font=('微软雅黑', 28, 'bold'), bg='#16213e', fg='#e94560').pack()
        tk.Label(f, text=t('login'), font=('微软雅黑', 14), bg='#16213e', fg='#c0c0c0').pack(pady=(0, 25))
        ff = tk.Frame(f, bg='#16213e'); ff.pack(pady=10)
        tk.Label(ff, text=t('username'), bg='#16213e', fg='#808090', font=('微软雅黑', 10), anchor='w').pack(fill=tk.X, padx=40)
        self._user = tk.Entry(ff, width=30, font=('微软雅黑', 12), bg='#0a0a1a', fg='#e0e0e0', insertbackground='#e94560', relief='flat', bd=10)
        self._user.pack(pady=(4, 14), padx=40); self._user.focus_set()
        tk.Label(ff, text=t('password'), bg='#16213e', fg='#808090', font=('微软雅黑', 10), anchor='w').pack(fill=tk.X, padx=40)
        self._pwd = tk.Entry(ff, width=30, font=('微软雅黑', 12), show='●', bg='#0a0a1a', fg='#e0e0e0', insertbackground='#e94560', relief='flat', bd=10)
        self._pwd.pack(pady=(4, 20), padx=40)
        b = tk.Button(ff, text=t('btn_login'), font=('微软雅黑', 12, 'bold'), bg='#e94560', fg='white', activebackground='#c73550', relief='flat', bd=0, padx=50, pady=10, cursor='hand2', command=self._do_login)
        _hover_btn(b, '#e94560', '#ff5a75'); b.pack(pady=(10, 8))
        link = tk.Frame(f, bg='#16213e'); link.pack()
        tk.Label(link, text=t('no_account'), bg='#16213e', fg='#707080', font=('微软雅黑', 9)).pack(side=tk.LEFT)
        tk.Button(link, text=t('to_register'), font=('微软雅黑', 9, 'bold'), bg='#16213e', fg='#e94560', activebackground='#16213e', relief='flat', bd=0, cursor='hand2', command=self._show_register).pack(side=tk.LEFT)
        self._pwd.bind('<Return>', lambda e: self._do_login())
    def _show_register(self):
        self._clear(); self._lang_selector()
        card, f = self._card(); card.place(relx=0.5, rely=0.5, anchor='center', width=420, height=520)
        if os.path.exists(_ICON):
            img = tk.PhotoImage(file=_ICON); f.img = img
            tk.Label(f, image=img, bg='#16213e').pack(pady=(30, 5))
        tk.Label(f, text=t('title'), font=('微软雅黑', 28, 'bold'), bg='#16213e', fg='#e94560').pack()
        tk.Label(f, text=t('register'), font=('微软雅黑', 14), bg='#16213e', fg='#c0c0c0').pack(pady=(0, 20))
        ff = tk.Frame(f, bg='#16213e'); ff.pack(pady=5)
        for label_text, attr, show in [(t('username'), '_reg_user', False), (t('pwd_hint'), '_reg_pwd', True), (t('confirm_pwd'), '_reg_cfm', True)]:
            tk.Label(ff, text=label_text, bg='#16213e', fg='#808090', font=('微软雅黑', 10), anchor='w').pack(fill=tk.X, padx=40)
            e = tk.Entry(ff, width=30, font=('微软雅黑', 12), bg='#0a0a1a', fg='#e0e0e0', insertbackground='#e94560', relief='flat', bd=10, show='●' if show else '')
            e.pack(pady=(4, 8), padx=40); setattr(self, attr, e)
        self._reg_user.focus_set()
        b = tk.Button(ff, text=t('btn_register'), font=('微软雅黑', 12, 'bold'), bg='#e94560', fg='white', activebackground='#c73550', relief='flat', bd=0, padx=50, pady=10, cursor='hand2', command=self._do_register)
        _hover_btn(b, '#e94560', '#ff5a75'); b.pack(pady=(12, 5))
        link = tk.Frame(f, bg='#16213e'); link.pack()
        tk.Label(link, text=t('has_account'), bg='#16213e', fg='#707080', font=('微软雅黑', 9)).pack(side=tk.LEFT)
        tk.Button(link, text=t('to_login'), font=('微软雅黑', 9, 'bold'), bg='#16213e', fg='#e94560', activebackground='#16213e', relief='flat', bd=0, cursor='hand2', command=self._show_login).pack(side=tk.LEFT)
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
