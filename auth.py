"""Login and registration screens."""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import messagebox, ttk

from database import login_user, register_user
from lang import LANG_OPTIONS, get_lang, save_lang, t
from ui_theme import COLORS, FONT, configure_ttk, load_photo, make_entry


_ICON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bomb32.png')


class AuthFrame(tk.Frame):
    def __init__(self, parent: tk.Misc, on_login):
        super().__init__(parent, bg=COLORS['bg'])
        configure_ttk(parent)
        self.on_login = on_login
        self._mode = 'login'
        self._show_login()

    def _clear(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

    def _change_language(self, language: str) -> None:
        save_lang(language)
        if self._mode == 'register':
            self._show_register()
        else:
            self._show_login()

    def _language_selector(self) -> None:
        container = tk.Frame(self, bg=COLORS['bg'])
        container.place(x=20, y=18)

        tk.Label(
            container, text='语言', font=(FONT, 9),
            bg=COLORS['bg'], fg=COLORS['muted'],
        ).pack(side=tk.LEFT, padx=(0, 8))

        current_name = dict(LANG_OPTIONS).get(get_lang(), '中文')
        menu_button = tk.Menubutton(
            container,
            text=f'{current_name}  ▾',
            font=(FONT, 10, 'bold'),
            bg=COLORS['surface'],
            fg=COLORS['text'],
            activebackground=COLORS['surface_hover'],
            activeforeground=COLORS['text'],
            relief='flat',
            bd=0,
            padx=12,
            pady=7,
            cursor='hand2',
        )
        menu_button.pack(side=tk.LEFT)
        menu = tk.Menu(
            menu_button, tearoff=0,
            bg=COLORS['surface'], fg=COLORS['text'],
            activebackground=COLORS['primary'],
            activeforeground='white', font=(FONT, 10),
        )
        for code, name in LANG_OPTIONS:
            menu.add_command(
                label=name, command=lambda selected=code: self._change_language(selected))
        menu_button.configure(menu=menu)

    def _create_card(self, height: int) -> tuple[tk.Frame, tk.Frame]:
        card = tk.Frame(
            self, bg=COLORS['border'], bd=0,
            highlightthickness=0,
        )
        inner = tk.Frame(card, bg=COLORS['surface'])
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        card.place(relx=0.5, rely=0.52, anchor='center', width=440, height=height)
        self._auth_card = card
        return card, inner

    def _header(self, parent: tk.Misc, subtitle: str) -> None:
        image = load_photo(_ICON, master=self)
        if image is not None:
            self._icon_image = image
            tk.Label(parent, image=image, bg=COLORS['surface']).pack(pady=(26, 6))
        else:
            tk.Label(
                parent, text='●', font=(FONT, 22, 'bold'),
                bg=COLORS['surface'], fg=COLORS['primary'],
            ).pack(pady=(26, 6))

        tk.Label(
            parent, text=t('title'), font=(FONT, 28, 'bold'),
            bg=COLORS['surface'], fg=COLORS['text'],
        ).pack()
        tk.Label(
            parent, text=subtitle, font=(FONT, 12),
            bg=COLORS['surface'], fg=COLORS['muted'],
        ).pack(pady=(4, 22))

    def _field(self, parent: tk.Misc, label: str, *, show: str = '') -> tk.Entry:
        tk.Label(
            parent, text=label, font=(FONT, 10), anchor='w',
            bg=COLORS['surface'], fg=COLORS['muted'],
        ).pack(fill=tk.X, pady=(0, 6))
        entry = make_entry(parent, show=show)
        entry.pack(fill=tk.X, ipady=10, pady=(0, 16))
        return entry

    def _show_login(self) -> None:
        self._mode = 'login'
        self._clear()
        self._language_selector()
        _, card = self._create_card(570)
        self._header(card, t('login'))

        form = tk.Frame(card, bg=COLORS['surface'])
        form.pack(fill=tk.X, padx=52)
        self._user = self._field(form, t('username'))
        self._pwd = self._field(form, t('password'), show='●')

        login_button = ttk.Button(
            form, text=t('btn_login'), style='Primary.TButton', command=self._do_login)
        login_button.pack(fill=tk.X, pady=(2, 14))

        separator = tk.Frame(form, bg=COLORS['border'], height=1)
        separator.pack(fill=tk.X, pady=(2, 12))
        tk.Label(
            form, text=t('no_account'), font=(FONT, 9),
            bg=COLORS['surface'], fg=COLORS['subtle'],
        ).pack(pady=(0, 7))
        self.register_nav_button = ttk.Button(
            form, text=t('to_register'), style='Secondary.TButton',
            command=self._show_register,
        )
        self.register_nav_button.pack(fill=tk.X)

        self._user.focus_set()
        self._user.bind('<Return>', lambda _event: self._pwd.focus_set())
        self._pwd.bind('<Return>', lambda _event: self._do_login())

    def _show_register(self) -> None:
        self._mode = 'register'
        self._clear()
        self._language_selector()
        _, card = self._create_card(650)
        self._header(card, t('register'))

        form = tk.Frame(card, bg=COLORS['surface'])
        form.pack(fill=tk.X, padx=52)
        self._reg_user = self._field(form, t('username'))
        self._reg_pwd = self._field(form, t('pwd_hint'), show='●')
        self._reg_cfm = self._field(form, t('confirm_pwd'), show='●')

        register_button = ttk.Button(
            form, text=t('btn_register'), style='Primary.TButton',
            command=self._do_register,
        )
        register_button.pack(fill=tk.X, pady=(0, 12))
        ttk.Button(
            form, text=t('to_login'), style='Ghost.TButton',
            command=self._show_login,
        ).pack(fill=tk.X)

        self._reg_user.focus_set()
        self._reg_user.bind('<Return>', lambda _event: self._reg_pwd.focus_set())
        self._reg_pwd.bind('<Return>', lambda _event: self._reg_cfm.focus_set())
        self._reg_cfm.bind('<Return>', lambda _event: self._do_register())

    def _do_login(self) -> None:
        username = self._user.get().strip()
        password = self._pwd.get()
        if not username or not password:
            messagebox.showwarning(t('login'), t('warn_empty'), parent=self)
            return

        ok, result = login_user(username, password)
        if ok:
            self.on_login(result)
        else:
            messagebox.showerror(t('login_fail'), result, parent=self)
            self._pwd.selection_range(0, tk.END)
            self._pwd.focus_set()

    def _do_register(self) -> None:
        username = self._reg_user.get().strip()
        password = self._reg_pwd.get()
        confirm = self._reg_cfm.get()
        if not username or not password or not confirm:
            messagebox.showwarning(t('register'), t('warn_empty'), parent=self)
            return
        if password != confirm:
            messagebox.showerror(t('reg_fail'), t('pwd_mismatch'), parent=self)
            self._reg_cfm.selection_range(0, tk.END)
            self._reg_cfm.focus_set()
            return

        ok, message = register_user(username, password)
        if ok:
            messagebox.showinfo(t('reg_ok'), message, parent=self)
            self._show_login()
            self._user.insert(0, username)
            self._pwd.focus_set()
        else:
            messagebox.showerror(t('reg_fail'), message, parent=self)
