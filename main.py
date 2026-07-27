"""扫雷游戏 - 主入口（Uiverse 风格重制）"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '扫雷图标.png')
_BOMB_ICON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bomb32.png')

from database import init_db
from auth import AuthFrame
from game import GameFrame, DIFFICULTY_CONFIG
from ranking import RankingFrame
from lang import t

class MainApp:
    def __init__(self):
        self.root=tk.Tk()
        if os.path.exists(_ICON_PATH):
            self._icon=tk.PhotoImage(file=_ICON_PATH)
            self.root.iconphoto(True,self._icon)
        self.root.title(t('title'))
        self.root.geometry("560x580")
        self.root.minsize(480,500)
        self.root.resizable(True,True)
        self.root.configure(bg='#0f0f23')
        self.current_user=None;self.current_frame=None
        init_db();self._show_auth()
        self.root.protocol("WM_DELETE_WINDOW",self._quit)
        self.root.mainloop()
    def _swap(self,frame_class,*args):
        if self.current_frame:self.current_frame.destroy()
        self.current_frame=frame_class(self.root,*args)
        self.current_frame.pack(fill=tk.BOTH,expand=True)
    def _show_auth(self):
        self.root.title(t('title'))
        self.root.geometry("520x560")
        self._swap(AuthFrame,self._on_login)
    def _on_login(self,user:dict):self.current_user=user;self._show_menu()
    def _show_menu(self):
        self.root.title(t('title'))
        self.root.geometry("600x620")
        self.root.configure(bg='#0f0f23')
        if self.current_frame:self.current_frame.destroy()
        self.current_frame=tk.Frame(self.root,bg='#0f0f23')
        self.current_frame.pack(fill=tk.BOTH,expand=True)
        f=tk.Frame(self.current_frame,bg='#0f0f23');f.pack(expand=True)
        if os.path.exists(_BOMB_ICON):
            img=tk.PhotoImage(file=_BOMB_ICON);f.img=img
            tk.Label(f,image=img,bg='#0f0f23').pack(pady=(20,0))
        tk.Label(f,text=t('title'),font=('微软雅黑',32,'bold'),bg='#0f0f23',fg='#e94560').pack()
        tk.Label(f,text=t('welcome',self.current_user['username']),font=('微软雅黑',12),bg='#0f0f23',fg='#a0a0b0').pack(pady=(2,25))
        card_row=tk.Frame(f,bg='#0f0f23');card_row.pack(pady=10)
        difficulties=[('9x9',t('diff_easy'),'#00b894','#55efc4',t('desc_easy')),('27x27',t('diff_medium'),'#fdcb6e','#ffeaa7',t('desc_medium')),('81x81',t('diff_hard'),'#e17055','#fab1a0',t('desc_hard'))]
        for diff_key,label,color,light_color,desc in difficulties:
            card=tk.Frame(card_row,bg='#1a1a2e',bd=0,highlightbackground=color,highlightthickness=1)
            card.pack(side=tk.LEFT,padx=10,ipadx=10,ipady=10)
            tk.Frame(card,bg=color,height=4).pack(fill=tk.X)
            inner=tk.Frame(card,bg='#1a1a2e');inner.pack(padx=20,pady=15)
            tk.Label(inner,text=label,font=('微软雅黑',15,'bold'),bg='#1a1a2e',fg=color).pack()
            tk.Label(inner,text=desc,font=('微软雅黑',9),bg='#1a1a2e',fg='#606070').pack(pady=(2,10))
            btn=tk.Button(inner,text=t('btn_start'),font=('微软雅黑',10,'bold'),bg=color,fg='#0f0f23',activebackground=light_color,relief='flat',bd=0,padx=20,pady=6,cursor='hand2',command=lambda d=diff_key:self._start_game(d))
            btn.pack()
        bottom=tk.Frame(f,bg='#0f0f23');bottom.pack(pady=25)
        for text,cmd in [(t('btn_ranking'),self._show_ranking),(t('btn_logout'),self._logout)]:
            tk.Button(bottom,text=text,font=('微软雅黑',10),bg='#1a1a2e',fg='#a0a0b0',activebackground='#16213e',relief='flat',bd=0,padx=24,pady=8,cursor='hand2',command=cmd).pack(side=tk.LEFT,padx=8)
    def _start_game(self,difficulty:str):self._swap(GameFrame,self.current_user,difficulty,self._show_menu)
    def _show_ranking(self):self._swap(RankingFrame,self.current_user,self._show_menu)
    def _logout(self):
        if messagebox.askyesno(t('btn_logout'),t('logout_confirm')):self.current_user=None;self._show_auth()
    def _quit(self):
        if self.current_user:
            if messagebox.askyesno(t('title'),t('quit_confirm')):self.root.quit()
        else:self.root.quit()
if __name__=='__main__':MainApp()
