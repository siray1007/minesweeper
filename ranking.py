"""
扫雷游戏 - 排行榜模块
"""
import tkinter as tk
from tkinter import ttk
from database import get_rankings_local, _gitee_fetch_rankings

DIFFICULTY_LABELS = [
    ('9x9','🟢 简单 9×9'),('27x27','🟡 进阶 27×27'),('81x81','🔴 困难 81×81'),
]

class RankingWindow(tk.Toplevel):
    def __init__(self,master,current_user:dict):
        super().__init__(master)
        self.current_user=current_user
        self.title("扫雷 - 排行榜")
        self.resizable(True,True)
        self.minsize(500,400)
        self.configure(bg='#f5f5f5')
        self.geometry("680x520")
        self._trees={}
        self._center()
        self._build_ui()
        self.grab_set()
        self._cloud_idx=0
        self.after(100,self._fetch_cloud_step)
    def _center(self):
        self.update_idletasks()
        w,h=680,520;ws,hs=self.winfo_screenwidth(),self.winfo_screenheight()
        self.geometry(f'+{(ws-w)//2}+{(hs-h)//2}')
    def _build_ui(self):
        tk.Label(self,text="🏆 排行榜",font=('微软雅黑',22,'bold'),bg='#f5f5f5',fg='#333').pack(pady=(18,2))
        tk.Label(self,text=f"当前用户：{self.current_user['username']}",font=('微软雅黑',10),bg='#f5f5f5',fg='#888').pack(pady=(0,12))
        nb=ttk.Notebook(self);nb.pack(fill=tk.BOTH,expand=True,padx=20,pady=5)
        for diff_key,diff_label in DIFFICULTY_LABELS:
            frame=tk.Frame(nb,bg='#fafafa');nb.add(frame,text=diff_label);self._build_table(frame,diff_key)
        ttk.Button(self,text="关闭",command=self.destroy).pack(pady=12)
    def _build_table(self,parent,difficulty:str):
        cols=('rank','username','time','date')
        tree=ttk.Treeview(parent,columns=cols,show='headings',height=15)
        tree.heading('rank',text='排名');tree.heading('username',text='用户名')
        tree.heading('time',text='用时');tree.heading('date',text='完成日期')
        tree.column('rank',width=60,anchor='center');tree.column('username',width=160,anchor='center')
        tree.column('time',width=140,anchor='center');tree.column('date',width=220,anchor='center')
        sb=ttk.Scrollbar(parent,orient=tk.VERTICAL,command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side=tk.LEFT,fill=tk.BOTH,expand=True);sb.pack(side=tk.RIGHT,fill=tk.Y)
        tree.tag_configure('me',background='#ffe0b2',font=('微软雅黑',9,'bold'))
        self._trees[difficulty]=tree
        self._populate_tree(tree,get_rankings_local(difficulty))
    def _populate_tree(self,tree,rankings):
        for item in tree.get_children():tree.delete(item)
        if not rankings:tree.insert('',tk.END,values=('—','暂无记录','—','—'))
        else:
            for i,rec in enumerate(rankings):
                m,s=divmod(rec['time_seconds'],60)
                tags=('me',) if rec['username']==self.current_user['username'] else ()
                date=rec.get('completed_at') or rec.get('created_at','')
                tree.insert('',tk.END,values=(i+1,rec['username'],f"{m:02d}:{s:02d}",date),tags=tags)
    def _fetch_cloud_step(self):
        if self._cloud_idx>=len(DIFFICULTY_LABELS):return
        diff_key=DIFFICULTY_LABELS[self._cloud_idx][0];self._cloud_idx+=1
        def do_fetch():
            online=_gitee_fetch_rankings(diff_key,50) or []
            local=get_rankings_local(diff_key)
            seen=set();merged=[]
            for r in online:seen.add((r['username'],r['time_seconds']));merged.append(r)
            for r in local:
                key=(r['username'],r['time_seconds'])
                if key not in seen:seen.add(key);merged.append(r)
            merged.sort(key=lambda x:x.get('time_seconds',99999))
            tree=self._trees.get(diff_key)
            if tree and tree.winfo_exists():self._populate_tree(tree,merged)
        self.after(50,do_fetch);self.after(300,self._fetch_cloud_step)
