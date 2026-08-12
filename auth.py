"""Login and registration screens."""
from __future__ import annotations

import os
import tkinter as tk

from database import login_user, register_user
from lang import LANG_OPTIONS, get_lang, save_lang, t
from ui_theme import COLORS, FONT, FONT_MONO, LAYOUT, CyberButton, configure_ttk, install_backdrop, load_photo, make_entry, make_panel


_ICON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bomb32.png")


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
        container = tk.Frame(self, bg=COLORS["bg"])
        container.place(relx=0.5, y=24, anchor="n")

        tk.Label(container, text=t("language"), font=(FONT, 10, "bold"), bg=COLORS["bg"], fg=COLORS["muted"]).pack(
            side=tk.LEFT, padx=(0, 8)
        )

        segment = tk.Frame(container, bg=COLORS["border"], padx=1, pady=1)
        segment.pack(side=tk.LEFT)
        for code, name in LANG_OPTIONS:
            CyberButton(
                segment,
                text=name,
                variant="primary" if get_lang() == code else "secondary",
                command=lambda selected=code: self._change_language(selected),
                width=8,
            ).pack(side=tk.LEFT, padx=(0 if code == LANG_OPTIONS[0][0] else 1, 0))

    def _create_card(self, height: int) -> tuple[tk.Frame, tk.Frame]:
        card, inner = make_panel(self, bg=COLORS["surface"], border=COLORS["border_hot"])
        card.place(relx=0.5, rely=0.54, anchor="center", width=LAYOUT["auth"][0] - 150, height=height)
        self._auth_card = card
        return card, inner

    def _header(self, parent: tk.Misc, subtitle: str) -> None:
        tk.Label(
            parent,
            text=t("auth_kicker"),
            font=(FONT_MONO, 10, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["primary"],
        ).pack(pady=(20, 6))
        image = load_photo(_ICON, master=self)
        if image is not None:
            self._icon_image = image
            tk.Label(parent, image=image, bg=COLORS["surface"]).pack(pady=(0, 6))
        else:
            tk.Label(parent, text="MINE", font=(FONT, 15, "bold"), bg=COLORS["surface"], fg=COLORS["primary"]).pack(
                pady=(0, 6)
            )

        tk.Label(parent, text=t("title"), font=(FONT, 31, "bold"), bg=COLORS["surface"], fg=COLORS["text"]).pack()
        tk.Frame(parent, bg=COLORS["primary"], height=2).pack(fill=tk.X, padx=112, pady=(10, 10))
        tk.Label(parent, text=subtitle, font=(FONT, 13), bg=COLORS["surface"], fg=COLORS["muted"]).pack(
            pady=(0, 8)
        )
        tk.Label(parent, text=t("auth_status"), font=(FONT_MONO, 9), bg=COLORS["surface"], fg=COLORS["subtle"]).pack(
            pady=(0, 12)
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
            wraplength=440,
            justify="left",
            anchor="w",
        )
        self._inline_message.pack(fill=tk.X, pady=(0, 12))

    def _field(self, parent: tk.Misc, label: str, *, show: str = "") -> tk.Entry:
        tk.Label(parent, text=label, font=(FONT, 10), anchor="w", bg=COLORS["surface"], fg=COLORS["muted"]).pack(
            fill=tk.X, pady=(0, 6)
        )
        entry = make_entry(parent, show=show)
        entry.pack(fill=tk.X, ipady=9, pady=(0, 14))
        return entry

    def _show_login(self) -> None:
        self._mode = "login"
        self._clear()
        self._language_selector()
        _, card = self._create_card(620)
        self._header(card, t("login"))

        form = tk.Frame(card, bg=COLORS["surface"])
        form.pack(fill=tk.X, padx=68)
        self._inline_status(form)
        self._user = self._field(form, t("username"))
        self._pwd = self._field(form, t("password"), show="*")

        CyberButton(form, text=t("btn_login"), command=self._do_login).pack(
            fill=tk.X, pady=(2, 14)
        )

        tk.Frame(form, bg=COLORS["border"], height=1).pack(fill=tk.X, pady=(2, 12))
        tk.Label(form, text=t("no_account"), font=(FONT, 9), bg=COLORS["surface"], fg=COLORS["subtle"]).pack(
            pady=(0, 7)
        )
        self.register_nav_button = CyberButton(form, text=t("to_register"), variant="secondary", command=self._show_register)
        self.register_nav_button.pack(fill=tk.X)

        self._user.focus_set()
        self._user.bind("<Return>", lambda _event: self._pwd.focus_set())
        self._pwd.bind("<Return>", lambda _event: self._do_login())

    def _show_register(self) -> None:
        self._mode = "register"
        self._clear()
        self._language_selector()
        _, card = self._create_card(720)
        self._header(card, t("register"))

        form = tk.Frame(card, bg=COLORS["surface"])
        form.pack(fill=tk.X, padx=68)
        self._inline_status(form)
        self._reg_user = self._field(form, t("username"))
        self._reg_pwd = self._field(form, t("pwd_hint"), show="*")
        self._reg_cfm = self._field(form, t("confirm_pwd"), show="*")

        CyberButton(form, text=t("btn_register"), command=self._do_register).pack(
            fill=tk.X, pady=(0, 12)
        )
        CyberButton(form, text=t("to_login"), variant="secondary", command=self._show_login).pack(fill=tk.X)

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
