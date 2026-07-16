"""
扫雷游戏 - 排行榜模块
按难度分 Tab 展示排名，高亮当前用户
"""
import tkinter as tk
from tkinter import ttk
from database import get_rankings

DIFFICULTY_LABELS = [
    ('9x9',   '🟢 简单 9×9'),
    ('27x27', '🟡 进阶 27×27'),
    ('81x81', '🔴 困难 81×81'),
]


class RankingWindow(tk.Toplevel):
    """排行榜窗口"""

    def __init__(self, master, current_user: dict):
        super().__init__(master)
        self.current_user = current_user
        self.title("扫雷 - 排行榜")
        self.resizable(False, False)
        self.configure(bg='#f5f5f5')

        self.geometry("680x520")
        self._center()
        self._build_ui()
        self.grab_set()

    def _center(self):
        self.update_idletasks()
        w, h = 680, 520
        ws, hs = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'+{(ws-w)//2}+{(hs-h)//2}')

    def _build_ui(self):
        # 标题
        tk.Label(self, text="🏆 排行榜", font=('微软雅黑', 22, 'bold'),
                 bg='#f5f5f5', fg='#333').pack(pady=(18, 2))
        tk.Label(self, text=f"当前用户：{self.current_user['username']}",
                 font=('微软雅黑', 10), bg='#f5f5f5', fg='#888').pack(pady=(0, 12))

        # 选项卡
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        for diff_key, diff_label in DIFFICULTY_LABELS:
            frame = tk.Frame(nb, bg='#fafafa')
            nb.add(frame, text=diff_label)
            self._build_table(frame, diff_key)

        ttk.Button(self, text="关闭", command=self.destroy).pack(pady=12)

    def _build_table(self, parent, difficulty: str):
        """在 parent 中构建一个排行榜表格"""
        cols = ('rank', 'username', 'time', 'date')
        tree = ttk.Treeview(parent, columns=cols, show='headings', height=15)

        tree.heading('rank',     text='排名')
        tree.heading('username', text='用户名')
        tree.heading('time',     text='用时')
        tree.heading('date',     text='完成日期')

        tree.column('rank',     width=60,  anchor='center')
        tree.column('username', width=160, anchor='center')
        tree.column('time',     width=140, anchor='center')
        tree.column('date',     width=220, anchor='center')

        sb = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=sb.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # 加载数据
        rankings = get_rankings(difficulty)
        if not rankings:
            tree.insert('', tk.END, values=('—', '暂无记录', '—', '—'))
        else:
            for i, rec in enumerate(rankings):
                m, s = divmod(rec['time_seconds'], 60)
                tags = ('me',) if rec['username'] == self.current_user['username'] else ()
                tree.insert('', tk.END, values=(
                    i + 1,
                    rec['username'],
                    f"{m:02d}:{s:02d}",
                    rec['completed_at'],
                ), tags=tags)

        tree.tag_configure('me', background='#ffe0b2', font=('微软雅黑', 9, 'bold'))
