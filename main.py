"""
扫雷游戏 - 主入口（单窗口多视图）
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '扫雷图标.png')

from database import init_db
from auth import AuthFrame
from game import GameFrame, DIFFICULTY_CONFIG
from ranking import RankingFrame

class MainApp:
    def __init__(self):
        self.root=tk.Tk()
        if os.path.exists(_ICON_PATH):
            self._icon=tk.PhotoImage(file=_ICON_PATH)
            self.root.iconphoto(True,self._icon)
        self.root.title("扫雷游戏")
        self.root.geometry("520x500")
        self.root.minsize(420,380)
        self.root.resizable(True,True)
        self.root.configure(bg='#f0f0f0')
        self.current_user=None;self.current_frame=None
        init_db();self._show_auth()
        self.root.protocol("WM_DELETE_WINDOW",self._quit)
        self.root.mainloop()
    def _swap(self,frame_class,*args):
        if self.current_frame:self.current_frame.destroy()
        self.current_frame=frame_class(self.root,*args)
        self.current_frame.pack(fill=tk.BOTH,expand=True)
    def _show_auth(self):
        self.root.title("扫雷游戏 - 登录")
        self.root.geometry("520x500")
        self._swap(AuthFrame,self._on_login)
    def _on_login(self,user:dict):self.current_user=user;self._show_menu()
    def _show_menu(self):
        self.root.title("扫雷游戏 - 主菜单")
        self.root.geometry("520x500")
        if self.current_frame:self.current_frame.destroy()
        frame=tk.Frame(self.root,bg='#f0f0f0');self.current_frame=frame;frame.pack(fill=tk.BOTH,expand=True)
        tk.Label(frame,text="💣 扫雷游戏",font=('微软雅黑',28,'bold'),bg='#f0f0f0',fg='#333').pack(pady=(30,5))
        tk.Label(frame,text=f"欢迎，{self.current_user['username']}！",font=('微软雅黑',12),bg='#f0f0f0',fg='#666').pack(pady=(0,25))
        tk.Label(frame,text="—— 选择难度 ——",font=('微软雅黑',13,'bold'),bg='#f0f0f0',fg='#555').pack(pady=(0,15))
        row=tk.Frame(frame,bg='#f0f0f0');row.pack(pady=5)
        difficulties=[('9x9','🟢 简单 9×9','#4CAF50','10 个地雷 · 经典入门'),('27x27','🟡 进阶 27×27','#FF9800','100 个地雷 · 高手进阶'),('81x81','🔴 困难 81×81','#F44336','800 个地雷 · 极限挑战')]
        for diff_key,label,color,desc in difficulties:
            card=tk.Frame(row,bg='white',bd=1,relief='solid',highlightbackground='#ddd',highlightthickness=1)
            card.pack(side=tk.LEFT,padx=10,ipadx=5,ipady=8)
            tk.Label(card,text=label,font=('微软雅黑',14,'bold'),bg='white',fg=color).pack(pady=(10,2))
            tk.Label(card,text=desc,font=('微软雅黑',9),bg='white',fg='#999').pack(pady=(0,8))
            btn=tk.Button(card,text="开始游戏",font=('微软雅黑',10,'bold'),bg=color,fg='white',activebackground=color,cursor='hand2',width=12,height=1,command=lambda d=diff_key:self._start_game(d))
            btn.pack(pady=(0,10))
        bottom=tk.Frame(frame,bg='#f0f0f0');bottom.pack(pady=25)
        ttk.Button(bottom,text="🏆 排行榜",command=self._show_ranking,width=15).pack(side=tk.LEFT,padx=10)
        ttk.Button(bottom,text="🚪 登出",command=self._logout,width=15).pack(side=tk.LEFT,padx=10)
    def _start_game(self,difficulty:str):self._swap(GameFrame,self.current_user,difficulty,self._show_menu)
    def _show_ranking(self):self._swap(RankingFrame,self.current_user,self._show_menu)
    def _logout(self):
        if messagebox.askyesno("登出","确定要登出吗？"):self.current_user=None;self._show_auth()
    def _quit(self):
        if self.current_user:
            if messagebox.askyesno("退出","确定要退出游戏吗？"):self.root.quit()
        else:self.root.quit()
if __name__=='__main__':MainApp()
