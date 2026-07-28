"""
扫雷 - 主入口
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

def _hover_btn(btn, normal, hover):
    btn.bind('<Enter>', lambda e: btn.configure(bg=hover))
    btn.bind('<Leave>', lambda e: btn.configure(bg=normal))

class MainApp:
    def __init__(self):
        self.root=tk.Tk()
        if os.path.exists(_ICON_PATH):
            self._icon=tk.PhotoImage(file=_ICON_PATH)
            self.root.iconphoto(True,self._icon)
        self.root.title(t('title'))
        self.root.geometry("580x600")
        self.root.minsize(500,520)
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
        self.root.geometry("520x580")
        self._swap(AuthFrame,self._on_login)
    def _on_login(self,user:dict):self.current_user=user;self._show_menu()
    def _show_menu(self):
        self.root.title(t('title'))
        self.root.geometry("620x640")
        self.root.configure(bg='#0f0f23')
        if self.current_frame:self.current_frame.destroy()
        self.current_frame=tk.Frame(self.root,bg='#0f0f23')
        self.current_frame.pack(fill=tk.BOTH,expand=True)
        f=tk.Frame(self.current_frame,bg='#0f0f23');f.pack(expand=True)
        if os.path.exists(_BOMB_ICON):
            img=tk.PhotoImage(file=_BOMB_ICON);f.img=img
            tk.Label(f,image=img,bg='#0f0f23').pack(pady=(25,0))
        tk.Label(f,text=t('title'),font=('微软雅黑',36,'bold'),bg='#0f0f23',fg='#e94560').pack()
        tk.Label(f,text=t('welcome',self.current_user['username']),font=('微软雅黑',13),bg='#0f0f23',fg='#a0a0b0').pack(pady=(4,30))
        card_row=tk.Frame(f,bg='#0f0f23');card_row.pack(pady=10)
        difficulties=[('9x9',t('diff_easy'),'#00b894','#55efc4',t('desc_easy')),('27x27',t('diff_medium'),'#fdcb6e','#ffeaa7',t('desc_medium')),('81x81',t('diff_hard'),'#e17055','#fab1a0',t('desc_hard'))]
        for diff_key,label,color,light,desc in difficulties:
            card=tk.Frame(card_row,bg='#1a1a2e',bd=0,highlightbackground=color,highlightthickness=1)
            card.pack(side=tk.LEFT,padx=12,ipadx=12,ipady=12)
            tk.Frame(card,bg=color,height=4).pack(fill=tk.X)
            inner=tk.Frame(card,bg='#1a1a2e');inner.pack(padx=22,pady=18)
            tk.Label(inner,text=label,font=('微软雅黑',16,'bold'),bg='#1a1a2e',fg=color).pack()
            tk.Label(inner,text=desc,font=('微软雅黑',10),bg='#1a1a2e',fg='#707080').pack(pady=(4,12))
            btn=tk.Button(inner,text=t('btn_start'),font=('微软雅黑',11,'bold'),bg=color,fg='#0f0f23',activebackground=light,relief='flat',bd=0,padx=22,pady=8,cursor='hand2',command=lambda d=diff_key:self._start_game(d))
            _hover_btn(btn,color,light);btn.pack()
        bottom=tk.Frame(f,bg='#0f0f23');bottom.pack(pady=30)
        for text,cmd in [(t('btn_ranking'),self._show_ranking),(t('btn_logout'),self._logout)]:
            b=tk.Button(bottom,text=text,font=('微软雅黑',11),bg='#1a1a2e',fg='#a0a0b0',activebackground='#16213e',relief='flat',bd=0,padx=28,pady=10,cursor='hand2',command=cmd)
            _hover_btn(b,'#1a1a2e','#253350');b.pack(side=tk.LEFT,padx=10)
    def _start_game(self,difficulty:str):self._swap(GameFrame,self.current_user,difficulty,self._show_menu)
    def _show_ranking(self):self._swap(RankingFrame,self.current_user,self._show_menu)
    def _logout(self):
        if messagebox.askyesno(t('btn_logout'),t('logout_confirm')):self.current_user=None;self._show_auth()
    def _quit(self):
        if self.current_user:
            if messagebox.askyesno(t('title'),t('quit_confirm')):self.root.quit()
        else:self.root.quit()
if __name__=='__main__':MainApp()
