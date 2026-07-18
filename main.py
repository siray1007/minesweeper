"""
扫雷游戏 - 主入口（单窗口多视图）
"""
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

def _bomb_label(parent, text, font, **kw):
    f = tk.Frame(parent, bg=kw.get('bg', '#f0f0f0'))
    if os.path.exists(_BOMB_ICON):
        img = tk.PhotoImage(file=_BOMB_ICON); f.img = img
        tk.Label(f, image=img, bg=kw.get('bg', '#f0f0f0')).pack(side=tk.LEFT, padx=(0, 6))
    tk.Label(f, text=text, font=font, bg=kw.get('bg', '#f0f0f0'), fg=kw.get('fg', '#333')).pack(side=tk.LEFT)
    return f

class MainApp:
    def __init__(self):
        self.root=tk.Tk()
        if os.path.exists(_ICON_PATH):
            self._icon=tk.PhotoImage(file=_ICON_PATH)
            self.root.iconphoto(True,self._icon)
        self.root.title(t('title'))
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
        self.root.title(t('title') + ' - ' + t('login'))
        self.root.geometry("520x500")
        self._swap(AuthFrame,self._on_login)
    def _on_login(self,user:dict):self.current_user=user;self._show_menu()
    def _show_menu(self):
        self.root.title(t('title') + ' - ' + t('menu_title'))
        self.root.geometry("520x500")
        if self.current_frame:self.current_frame.destroy()
        frame=tk.Frame(self.root,bg='#f0f0f0');self.current_frame=frame;frame.pack(fill=tk.BOTH,expand=True)
        _bomb_label(frame,t('title'),('微软雅黑',28,'bold'),bg='#f0f0f0',fg='#333').pack(pady=(30,5))
        tk.Label(frame,text=t('welcome',self.current_user['username']),font=('微软雅黑',12),bg='#f0f0f0',fg='#666').pack(pady=(0,25))
        tk.Label(frame,text='—— '+t('menu_title')+' ——',font=('微软雅黑',13,'bold'),bg='#f0f0f0',fg='#555').pack(pady=(0,15))
        row=tk.Frame(frame,bg='#f0f0f0');row.pack(pady=5)
        difficulties=[('9x9',t('diff_easy'),'#4CAF50',t('desc_easy')),('27x27',t('diff_medium'),'#FF9800',t('desc_medium')),('81x81',t('diff_hard'),'#F44336',t('desc_hard'))]
        for diff_key,label,color,desc in difficulties:
            card=tk.Frame(row,bg='white',bd=1,relief='solid',highlightbackground='#ddd',highlightthickness=1)
            card.pack(side=tk.LEFT,padx=10,ipadx=5,ipady=8)
            tk.Label(card,text=label,font=('微软雅黑',14,'bold'),bg='white',fg=color).pack(pady=(10,2))
            tk.Label(card,text=desc,font=('微软雅黑',9),bg='white',fg='#999').pack(pady=(0,8))
            btn=tk.Button(card,text=t('btn_start'),font=('微软雅黑',10,'bold'),bg=color,fg='white',activebackground=color,cursor='hand2',width=12,height=1,command=lambda d=diff_key:self._start_game(d))
            btn.pack(pady=(0,10))
        bottom=tk.Frame(frame,bg='#f0f0f0');bottom.pack(pady=25)
        ttk.Button(bottom,text=t('btn_ranking'),command=self._show_ranking,width=15).pack(side=tk.LEFT,padx=10)
        ttk.Button(bottom,text=t('btn_logout'),command=self._logout,width=15).pack(side=tk.LEFT,padx=10)
    def _start_game(self,difficulty:str):self._swap(GameFrame,self.current_user,difficulty,self._show_menu)
    def _show_ranking(self):self._swap(RankingFrame,self.current_user,self._show_menu)
    def _logout(self):
        if messagebox.askyesno(t('btn_logout'),t('logout_confirm')):self.current_user=None;self._show_auth()
    def _quit(self):
        if self.current_user:
            if messagebox.askyesno(t('title'),t('quit_confirm')):self.root.quit()
        else:self.root.quit()
if __name__=='__main__':MainApp()
