"""Login and registration screens."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from database import login_user, register_user
from lang import LANG_OPTIONS, get_lang, save_lang, t
from sound import is_enabled, set_enabled
from ui_theme import COLORS, FONT, FONT_MONO, LAYOUT, CyberButton, configure_ttk, get_theme, install_backdrop, make_entry, make_panel, set_theme


class AuthFrame(tk.Frame):
    def __init__(self, parent: tk.Misc, on_login):
        super().__init__(parent, bg=COLORS["bg"])
        configure_ttk(parent)
        self._backdrop = install_backdrop(self)
        self.on_login = on_login
        self._mode = "login"
        self._inline_message: tk.Label | None = None
        self._inline_message_text = t("auth_ready")
        self._inline_message_kind = "info"
        self._show_login()

    def _clear(self) -> None:
        for widget in self.winfo_children():
            if widget is self._backdrop:
                continue
            widget.destroy()

    def _change_language(self, language: str) -> None:
        values = {}
        focused_name = None
        for name in ("_user", "_pwd", "_reg_user", "_reg_pwd", "_reg_cfm"):
            field = getattr(self, name, None)
            if field is not None and field.winfo_exists():
                values[name] = field.get()
                if field is self.focus_get():
                    focused_name = name
        save_lang(language)
        if self._inline_message_kind == "info":
            self._inline_message_text = t("auth_ready")
        self.winfo_toplevel().title(t("title"))
        if self._mode == "register":
            self._show_register()
        else:
            self._show_login()
        for name, value in values.items():
            field = getattr(self, name, None)
            if field is not None and field.winfo_exists():
                field.insert(0, value)
        focused_field = getattr(self, focused_name, None) if focused_name else None
        if focused_field is not None and focused_field.winfo_exists():
            focused_field.focus_set()
            focused_field.icursor(tk.END)

    def _language_selector(self) -> None:
        # 紧凑模块：尺寸贴合文字，不预留大块空白
        module = tk.Frame(self, bg=COLORS["border"], padx=1, pady=1)
        module.place(x=30, y=28, anchor="nw")
        self._language_module = module
        container = tk.Frame(module, bg=COLORS["surface_alt"])
        container.pack(fill=tk.BOTH, expand=True)

        row = tk.Frame(container, bg=COLORS["surface_alt"])
        row.pack(fill=tk.BOTH, expand=True)

        left_box = tk.Frame(
            row,
            bg=COLORS["surface_alt"],
            highlightthickness=1,
            highlightbackground=COLORS["border_dim"],
            highlightcolor=COLORS["border_dim"],
        )
        left_box.pack(side=tk.LEFT, fill=tk.Y)
        self._language_left_box = left_box
        tk.Label(
            left_box,
            text=t("language"),
            font=(FONT, 10, "bold"),
            bg=COLORS["surface_alt"],
            fg=COLORS["muted"],
            padx=12,
            pady=9,
        ).pack()

        names = [name for _code, name in LANG_OPTIONS]
        current_name = dict(LANG_OPTIONS).get(get_lang(), names[0])
        self._language_var = tk.StringVar(value=current_name)
        combo_shell = tk.Frame(
            row,
            bg=COLORS["surface_alt"],
            highlightthickness=1,
            highlightbackground=COLORS["border_dim"],
            highlightcolor=COLORS["border_dim"],
        )
        combo_shell.pack(side=tk.LEFT, fill=tk.Y)
        self._language_combo_shell = combo_shell
        self._language_combo = ttk.Combobox(
            combo_shell,
            textvariable=self._language_var,
            values=names,
            state="readonly",
            style="Language.TCombobox",
            width=10,
            font=(FONT, 10, "bold"),
        )
        self._language_combo.pack(fill=tk.Y, padx=4, pady=4)
        self._language_combo.bind("<FocusIn>", lambda _event: self._set_language_focus(True), add="+")
        self._language_combo.bind("<FocusOut>", lambda _event: self._set_language_focus(False), add="+")
        self._language_combo.bind("<<ComboboxSelected>>", self._language_selected)

    def _set_language_focus(self, focused: bool) -> None:
        if getattr(self, "_language_module", None) is not None:
            self._language_module.configure(bg=COLORS["border_hot"] if focused else COLORS["border"])

    def _language_selected(self, _event=None) -> None:
        selected_name = self._language_var.get()
        selected_code = next((code for code, name in LANG_OPTIONS if name == selected_name), get_lang())
        if selected_code != get_lang():
            self._change_language(selected_code)

    def _theme_label(self) -> str:
        return "浅色" if get_theme() == "light" else "深色"

    def _sound_label(self) -> str:
        return "音效开" if is_enabled() else "音效关"

    def _toggle_sound(self) -> None:
        set_enabled(not is_enabled())
        if self._sound_button is not None and self._sound_button.winfo_exists():
            self._sound_button.configure(text=self._sound_label())

    def _settings_row(self, parent: tk.Misc) -> None:
        row = tk.Frame(parent, bg=COLORS["surface"])
        row.pack(fill=tk.X, pady=(8, 16))
        self._theme_button = CyberButton(
            row, text=self._theme_label(), command=self._toggle_theme, variant="secondary", size="normal"
        )
        self._theme_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        self._sound_button = CyberButton(
            row, text=self._sound_label(), command=self._toggle_sound, variant="secondary", size="normal"
        )
        self._sound_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

    def _toggle_theme(self) -> None:
        values = {}
        for name in ("_user", "_pwd", "_reg_user", "_reg_pwd", "_reg_cfm"):
            field = getattr(self, name, None)
            if field is not None and field.winfo_exists():
                values[name] = field.get()
        new_theme = "light" if get_theme() == "dark" else "dark"
        set_theme(new_theme)
        backdrop = getattr(self, "_backdrop", None)
        if backdrop is not None:
            backdrop.destroy()
        self._backdrop = install_backdrop(self)
        if self._mode == "register":
            self._show_register()
        else:
            self._show_login()
        for name, value in values.items():
            field = getattr(self, name, None)
            if field is not None and field.winfo_exists():
                field.insert(0, value)

    def _create_card(self, height: int) -> tuple[tk.Frame, tk.Frame]:
        card, inner = make_panel(self, bg=COLORS["surface"], border=COLORS["border"])
        card.place(relx=0.5, rely=0.53, anchor="center", width=LAYOUT["auth"][0] - 140, height=height)
        self._auth_card = card
        return card, inner

    def _header(self, parent: tk.Misc, subtitle: str) -> None:
        tk.Label(
            parent,
            text=t("auth_kicker"),
            font=(FONT_MONO, 10, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["primary"],
        ).pack(pady=(10, 2))
        tk.Label(parent, text=t("title"), font=(FONT, 26, "bold"), bg=COLORS["surface"], fg=COLORS["text"]).pack()
        tk.Frame(parent, bg=COLORS["primary"], height=2).pack(fill=tk.X, padx=110, pady=(6, 6))
        tk.Label(parent, text=subtitle, font=(FONT, 12), bg=COLORS["surface"], fg=COLORS["muted"]).pack(pady=(0, 2))
        tk.Label(parent, text=t("auth_status"), font=(FONT_MONO, 9), bg=COLORS["surface"], fg=COLORS["subtle"]).pack(
            pady=(0, 6)
        )

    def _message_color(self) -> str:
        return {
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "error": COLORS["danger"],
        }.get(self._inline_message_kind, COLORS["muted"])

    def _set_inline_message(self, text: str, kind: str = "info") -> None:
        self._inline_message_text = text
        self._inline_message_kind = kind
        if self._inline_message is not None and self._inline_message.winfo_exists():
            self._inline_message.configure(text=text, fg=self._message_color())

    def _inline_status(self, parent: tk.Misc) -> None:
        self._inline_message = tk.Label(
            parent,
            text=self._inline_message_text,
            font=(FONT, 10, "bold"),
            bg=COLORS["surface"],
            fg=self._message_color(),
            wraplength=520,
            justify="left",
            anchor="w",
        )
        self._inline_message.pack(fill=tk.X, pady=(0, 9))

    def _field(self, parent: tk.Misc, label: str, *, show: str = "") -> tk.Entry:
        tk.Label(parent, text=label, font=(FONT, 10), anchor="w", bg=COLORS["surface"], fg=COLORS["muted"]).pack(
            fill=tk.X, pady=(0, 3)
        )
        entry = make_entry(parent, show=show)
        entry.pack(fill=tk.X, ipady=7, pady=(0, 7))
        return entry

    def _action_button(self, parent: tk.Misc, text: str, command, *, variant: str = "primary") -> CyberButton:
        """Render every auth action in the same fixed-height control slot."""
        slot = tk.Frame(parent, bg=COLORS["surface"], height=62)
        slot.pack(fill=tk.X, pady=(0, 12))
        slot.pack_propagate(False)
        button = CyberButton(slot, text=text, command=command, variant=variant)
        button.pack(fill=tk.BOTH, expand=True)
        return button

    def _show_login(self) -> None:
        self._mode = "login"
        self._clear()
        self._language_selector()
        _, card = self._create_card(610)
        self._header(card, t("login"))

        form = tk.Frame(card, bg=COLORS["surface"])
        form.pack(fill=tk.X, padx=70)
        self._inline_status(form)
        self._user = self._field(form, t("username"))
        self._pwd = self._field(form, t("password"), show="*")

        self.login_submit_button = self._action_button(form, t("btn_login"), self._do_login)

        tk.Frame(form, bg=COLORS["border"], height=1).pack(fill=tk.X, pady=(0, 10))
        tk.Label(form, text=t("no_account"), font=(FONT, 9), bg=COLORS["surface"], fg=COLORS["subtle"]).pack(
            pady=(0, 5)
        )
        self.register_nav_button = self._action_button(form, t("to_register"), self._show_register, variant="secondary")
        self.register_nav_button.pack_configure(pady=(0, 0))
        self._settings_row(form)

        self._user.focus_set()
        self._user.bind("<Return>", lambda _event: self._pwd.focus_set())
        self._pwd.bind("<Return>", lambda _event: self._do_login())

    def _show_register(self) -> None:
        self._mode = "register"
        self._clear()
        self._language_selector()
        _, card = self._create_card(660)
        self._header(card, t("register"))

        form = tk.Frame(card, bg=COLORS["surface"])
        form.pack(fill=tk.X, padx=70)
        self._inline_status(form)
        self._reg_user = self._field(form, t("username"))
        self._reg_pwd = self._field(form, t("pwd_hint"), show="*")
        self._reg_cfm = self._field(form, t("confirm_pwd"), show="*")

        self.register_submit_button = self._action_button(form, t("btn_register"), self._do_register)
        self.login_nav_button = self._action_button(form, t("to_login"), self._show_login, variant="secondary")
        self.login_nav_button.pack_configure(pady=(0, 0))
        self._settings_row(form)

        self._reg_user.focus_set()
        self._reg_user.bind("<Return>", lambda _event: self._reg_pwd.focus_set())
        self._reg_pwd.bind("<Return>", lambda _event: self._reg_cfm.focus_set())
        self._reg_cfm.bind("<Return>", lambda _event: self._do_register())

    def _do_login(self) -> None:
        username = self._user.get().strip()
        password = self._pwd.get()
        if not username or not password:
            self._set_inline_message(t("warn_empty"), "warning")
            if not username:
                self._user.focus_set()
            else:
                self._pwd.focus_set()
            return

        ok, result = login_user(username, password)
        if ok:
            self.on_login(result)
        else:
            self._set_inline_message(result, "error")
            self._pwd.selection_range(0, tk.END)
            self._pwd.focus_set()

    def _do_register(self) -> None:
        username = self._reg_user.get().strip()
        password = self._reg_pwd.get()
        confirm = self._reg_cfm.get()
        if not username or not password or not confirm:
            self._set_inline_message(t("warn_empty"), "warning")
            return
        if password != confirm:
            self._set_inline_message(t("pwd_mismatch"), "error")
            self._reg_cfm.selection_range(0, tk.END)
            self._reg_cfm.focus_set()
            return

        ok, message = register_user(username, password)
        if ok:
            self._set_inline_message(message, "success")
            self._show_login()
            self._user.insert(0, username)
            self._pwd.focus_set()
        else:
            self._set_inline_message(message, "error")
