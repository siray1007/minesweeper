"""
扫雷游戏 - 排行榜模块（嵌入主窗口）
"""
import tkinter as tk
from tkinter import ttk
from database import get_rankings_local, _gitee_fetch_rankings

DIFFICULTY_LABELS=[('9x9','🟢 简单 9×9'),('27x27','🟡 进阶 27×27'),('81x81','🔴 困难 81×81')]

class RankingFrame(tk.Frame):
    def __init__(self,parent,current_user:dict,on_back):
        super().__init__(parent,bg='#f5f5f5')
        self.current_user=current_user;self.on_back=on_back
        self._trees={};self._cloud_idx=0
        self._build_ui();self.after(100,self._fetch_cloud_step)
    def _build_ui(self):
        bar=tk.Frame(self,bg='#e8e8e8',height=44);bar.pack(fill=tk.X);bar.pack_propagate(False)
        ttk.Button(bar,text="← 返回",command=self.on_back).pack(side=tk.LEFT,padx=10,pady=6)
        tk.Label(bar,text="🏆 排行榜",font=('微软雅黑',18,'bold'),bg='#e8e8e8',fg='#333').pack(side=tk.LEFT,padx=5)
        tk.Label(bar,text=f"用户：{self.current_user['username']}",font=('微软雅黑',9),bg='#e8e8e8',fg='#888').pack(side=tk.RIGHT,padx=15,pady=6)
        nb=ttk.Notebook(self);nb.pack(fill=tk.BOTH,expand=True,padx=10,pady=5)
        for diff_key,diff_label in DIFFICULTY_LABELS:
            frame=tk.Frame(nb,bg='#fafafa');nb.add(frame,text=diff_label);self._build_table(frame,diff_key)
        my_frame=tk.Frame(nb,bg='#fafafa');nb.add(my_frame,text='📋 我的战绩');self._build_my_records(my_frame)
    def _dedup_best(self,rankings):
        best={}
        for r in rankings:
            u=r['username']
            if u not in best or r['time_seconds']<best[u]['time_seconds']:best[u]=r
        return sorted(best.values(),key=lambda x:x['time_seconds'])
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
        self._populate_tree(tree,self._dedup_best(get_rankings_local(difficulty)))
    def _populate_tree(self,tree,rankings):
        for item in tree.get_children():tree.delete(item)
        if not rankings:tree.insert('',tk.END,values=('—','暂无记录','—','—'))
        else:
            for i,rec in enumerate(rankings):
                m,s=divmod(rec['time_seconds'],60)
                tags=('me',) if rec['username']==self.current_user['username'] else ()
                date=rec.get('completed_at') or rec.get('created_at','')
                tree.insert('',tk.END,values=(i+1,rec['username'],f"{m:02d}:{s:02d}",date),tags=tags)
    def _build_my_records(self,parent):
        cols=('difficulty','time','date')
        tree=ttk.Treeview(parent,columns=cols,show='headings',height=15)
        tree.heading('difficulty',text='难度');tree.heading('time',text='用时');tree.heading('date',text='日期')
        tree.column('difficulty',width=150,anchor='center');tree.column('time',width=200,anchor='center')
        tree.column('date',width=250,anchor='center')
        sb=ttk.Scrollbar(parent,orient=tk.VERTICAL,command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side=tk.LEFT,fill=tk.BOTH,expand=True);sb.pack(side=tk.RIGHT,fill=tk.Y)
        all_records=[]
        for diff_key,diff_label in DIFFICULTY_LABELS:
            for r in get_rankings_local(diff_key):
                if r['username']==self.current_user['username']:
                    all_records.append((diff_label,r['time_seconds'],r.get('completed_at') or r.get('created_at','')))
        all_records.sort(key=lambda x:x[1])
        if not all_records:tree.insert('',tk.END,values=('—','暂无战绩','—'))
        else:
            for rec in all_records:
                m,s=divmod(rec[1],60);tree.insert('',tk.END,values=(rec[0],f"{m:02d}:{s:02d}",rec[2]))
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
            deduped=self._dedup_best(merged)
            tree=self._trees.get(diff_key)
            if tree and tree.winfo_exists():self._populate_tree(tree,deduped)
        self.after(50,do_fetch);self.after(300,self._fetch_cloud_step)
