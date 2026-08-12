"""Login and registration screens."""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import messagebox, ttk

from database import login_user, register_user
from lang import LANG_OPTIONS, get_lang, save_lang, t
from ui_theme import COLORS, FONT, LAYOUT, configure_ttk, load_photo, make_entry, section_title


_ICON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bomb32.png')


class AuthFrame(tk.Frame):
    def __init__(self, parent: tk.Misc, on_login):
        super().__init__(parent, bg=COLORS['bg'])
        configure_ttk(parent)
        self.on_login = on_login
        self._mode = 'login'
        self._icon_image = None
        self._auth_card = None
        self.register_nav_button = None
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
        container.place(x=22, y=18)

        tk.Label(
            container, text=t('language'), font=(FONT, 9),
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
            pady=8,
            cursor='hand2',
        )
        menu_button.pack(side=tk.LEFT)
        menu = tk.Menu(
            menu_button,
            tearoff=0,
            bg=COLORS['surface'],
            fg=COLORS['text'],
            activebackground=COLORS['primary'],
            activeforeground='white',
            font=(FONT, 10),
        )
        for code, name in LANG_OPTIONS:
            menu.add_command(
                label=name,
                command=lambda selected=code: self._change_language(selected),
            )
        menu_button.configure(menu=menu)

    def _create_card(self, height: int) -> tuple[tk.Frame, tk.Frame]:
        card_width, _ = LAYOUT['auth']['card']
        card = tk.Frame(
            self,
            bg=COLORS['surface'],
            highlightthickness=1,
            highlightbackground=COLORS['border'],
        )
        card.place(relx=0.5, rely=0.53, anchor='center', width=card_width, height=height)
        card.grid_columnconfigure(1, weight=1)
        accent = tk.Frame(card, bg=COLORS['primary'], width=6)
        accent.pack(side=tk.LEFT, fill=tk.Y)
        inner = tk.Frame(card, bg=COLORS['surface'])
        inner.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._auth_card = card
        return card, inner

    def _header(self, parent: tk.Misc, subtitle: str) -> None:
        head = tk.Frame(parent, bg=COLORS['surface'])
        head.pack(fill=tk.X, padx=34, pady=(26, 18))
        image = load_photo(_ICON, master=self)
        if image is not None:
            self._icon_image = image
            tk.Label(head, image=image, bg=COLORS['surface']).pack(side=tk.LEFT, padx=(0, 16))
        else:
            tk.Label(
                head,
                text='◆',
                font=(FONT, 22, 'bold'),
                bg=COLORS['surface'],
                fg=COLORS['primary'],
            ).pack(side=tk.LEFT, padx=(0, 16))

        title_block = tk.Frame(head, bg=COLORS['surface'])
        title_block.pack(side=tk.LEFT, fill=tk.X, expand=True)
        section_title(title_block, t('title'), subtitle).pack(fill=tk.X)

    def _field(self, parent: tk.Misc, label: str, *, show: str = '') -> tk.Entry:
        tk.Label(
            parent, text=label, font=(FONT, 10), anchor='w',
            bg=COLORS['surface'], fg=COLORS['muted'],
        ).pack(fill=tk.X, pady=(0, 6))
        entry = make_entry(parent, show=show)
        entry.pack(fill=tk.X, ipady=10, pady=(0, 16))
        return entry

    def _form_frame(self, parent: tk.Misc) -> tk.Frame:
        form = tk.Frame(parent, bg=COLORS['surface'])
        form.pack(fill=tk.X, padx=36, pady=(0, 20))
        return form

    def _show_login(self) -> None:
        self._mode = 'login'
        self._clear()
        self._language_selector()
        _, card = self._create_card(640)
        self._header(card, t('login'))

        form = self._form_frame(card)
        self._user = self._field(form, t('username'))
        self._pwd = self._field(form, t('password'), show='*')

        ttk.Button(
            form, text=t('btn_login'), style='Primary.TButton', command=self._do_login,
        ).pack(fill=tk.X, pady=(2, 14))

        separator = tk.Frame(form, bg=COLORS['border'], height=1)
        separator.pack(fill=tk.X, pady=(2, 12))
        tk.Label(
            form, text=t('no_account'), font=(FONT, 9),
            bg=COLORS['surface'], fg=COLORS['subtle'],
        ).pack(pady=(0, 8))
        self.register_nav_button = ttk.Button(
            form, text=t('to_register'), style='Secondary.TButton', command=self._show_register,
        )
        self.register_nav_button.pack(fill=tk.X)

        self._user.focus_set()
        self._user.bind('<Return>', lambda _event: self._pwd.focus_set())
        self._pwd.bind('<Return>', lambda _event: self._do_login())

    def _show_register(self) -> None:
        self._mode = 'register'
        self._clear()
        self._language_selector()
        _, card = self._create_card(720)
        self._header(card, t('register'))

        form = self._form_frame(card)
        self._reg_user = self._field(form, t('username'))
        self._reg_pwd = self._field(form, t('pwd_hint'), show='*')
        self._reg_cfm = self._field(form, t('confirm_pwd'), show='*')

        ttk.Button(
            form, text=t('btn_register'), style='Primary.TButton',
            command=self._do_register,
        ).pack(fill=tk.X, pady=(0, 12))
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
