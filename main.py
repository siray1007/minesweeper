"""
扫雷游戏 - 主入口
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import init_db
from auth import AuthWindow
from game import GameWindow, DIFFICULTY_CONFIG
from ranking import RankingWindow

class MainApp:
    def __init__(self):
        self.root=tk.Tk();self.root.withdraw()
        self.current_user=None;self.menu=None
        init_db();self._show_auth();self.root.mainloop()
    def _show_auth(self):
        auth=AuthWindow(self.root,self._on_login)
        self.root.wait_window(auth)
        if not self.current_user:self.root.quit()
    def _on_login(self,user:dict):self.current_user=user;self._show_menu()
    def _show_menu(self):
        if self.menu and self.menu.winfo_exists():self.menu.destroy()
        self.menu=tk.Toplevel(self.root)
        self.menu.title("扫雷游戏 - 主菜单")
        self.menu.resizable(True,True)
        self.menu.minsize(450,400)
        self.menu.configure(bg='#f0f0f0')
        self.menu.protocol("WM_DELETE_WINDOW",self._quit)
        w,h=520,500;ws=self.menu.winfo_screenwidth();hs=self.menu.winfo_screenheight()
        self.menu.geometry(f'{w}x{h}+{(ws-w)//2}+{(hs-h)//2}')
        tk.Label(self.menu,text="💣 扫雷游戏",font=('微软雅黑',28,'bold'),bg='#f0f0f0',fg='#333').pack(pady=(30,5))
        tk.Label(self.menu,text=f"欢迎，{self.current_user['username']}！",font=('微软雅黑',12),bg='#f0f0f0',fg='#666').pack(pady=(0,25))
        tk.Label(self.menu,text="—— 选择难度 ——",font=('微软雅黑',13,'bold'),bg='#f0f0f0',fg='#555').pack(pady=(0,15))
        row=tk.Frame(self.menu,bg='#f0f0f0');row.pack(pady=5)
        difficulties=[('9x9','🟢 简单 9×9','#4CAF50','10 个地雷 · 经典入门'),('27x27','🟡 进阶 27×27','#FF9800','100 个地雷 · 高手进阶'),('81x81','🔴 困难 81×81','#F44336','800 个地雷 · 极限挑战')]
        for diff_key,label,color,desc in difficulties:
            card=tk.Frame(row,bg='white',bd=1,relief='solid',highlightbackground='#ddd',highlightthickness=1)
            card.pack(side=tk.LEFT,padx=10,ipadx=5,ipady=8)
            tk.Label(card,text=label,font=('微软雅黑',14,'bold'),bg='white',fg=color).pack(pady=(10,2))
            tk.Label(card,text=desc,font=('微软雅黑',9),bg='white',fg='#999').pack(pady=(0,8))
            btn=tk.Button(card,text="开始游戏",font=('微软雅黑',10,'bold'),bg=color,fg='white',activebackground=color,cursor='hand2',width=12,height=1,command=lambda d=diff_key:self._start_game(d))
            btn.pack(pady=(0,10))
        bottom=tk.Frame(self.menu,bg='#f0f0f0');bottom.pack(pady=25)
        ttk.Button(bottom,text="🏆 排行榜",command=self._show_ranking,width=15).pack(side=tk.LEFT,padx=10)
        ttk.Button(bottom,text="🚪 登出",command=self._logout,width=15).pack(side=tk.LEFT,padx=10)
    def _start_game(self,difficulty:str):GameWindow(self.menu,self.current_user,difficulty,self._on_game_close)
    def _on_game_close(self):
        if self.menu and self.menu.winfo_exists():self.menu.deiconify();self.menu.lift()
    def _show_ranking(self):RankingWindow(self.menu,self.current_user)
    def _logout(self):
        if messagebox.askyesno("登出","确定要登出吗？"):
            self.current_user=None
            if self.menu and self.menu.winfo_exists():self.menu.destroy()
            self._show_auth()
    def _quit(self):
        if messagebox.askyesno("退出","确定要退出游戏吗？"):self.root.quit()

if __name__=='__main__':MainApp()
