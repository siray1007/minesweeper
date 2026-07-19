"""扫雷游戏 - 核心模块（嵌入主窗口）"""
import tkinter as tk
from tkinter import ttk, messagebox
import random,threading,os,colorsys
from database import save_ranking, _gitee_append_ranking
from lang import t

_BOMB_PNG=os.path.join(os.path.dirname(os.path.abspath(__file__)),'bomb16.png')
NUM_COLORS={1:'#0000FF',2:'#008000',3:'#FF0000',4:'#000080',5:'#800000',6:'#008080',7:'#000000',8:'#808080'}
DIFFICULTY_CONFIG={'9x9':{'rows':9,'cols':9,'mines':10,'cell':48,'title':t('easy_title')},'27x27':{'rows':27,'cols':27,'mines':100,'cell':20,'title':t('medium_title')},'81x81':{'rows':81,'cols':81,'mines':800,'cell':14,'title':t('hard_title')}}

def _random_pastel():
    h=random.random();s=random.uniform(0.25,0.45);v=random.uniform(0.75,0.90)
    r,g,b=colorsys.hsv_to_rgb(h,s,v)
    return (int(r*255),int(g*255),int(b*255))
def _cell_color(c1,c2,t):
    r=int(c1[0]+(c2[0]-c1[0])*t);g=int(c1[1]+(c2[1]-c1[1])*t);b=int(c1[2]+(c2[2]-c1[2])*t)
    return f'#{r:02x}{g:02x}{b:02x}'
def _lighten(hex_color,amount):
    r=int(hex_color[1:3],16);g=int(hex_color[3:5],16);b=int(hex_color[5:7],16)
    r=min(255,int(r+255*amount));g=min(255,int(g+255*amount));b=min(255,int(b+255*amount))
    return f'#{r:02x}{g:02x}{b:02x}'

class MinesweeperGame:
    def __init__(self,difficulty:str):
        cfg=DIFFICULTY_CONFIG[difficulty];self.difficulty=difficulty
        self.rows=cfg['rows'];self.cols=cfg['cols'];self.total_mines=cfg['mines']
        self.board=[[0]*self.cols for _ in range(self.rows)]
        self.revealed=[[False]*self.cols for _ in range(self.rows)]
        self.flagged=[[False]*self.cols for _ in range(self.rows)]
        self.game_over=False;self.game_won=False;self.first_click=True
        self.mines_generated=False;self.mine_positions=set()
        self.revealed_count=0;self.total_safe_cells=self.rows*self.cols-self.total_mines
    def generate_mines(self,safe_row:int,safe_col:int):
        safe={(safe_row,safe_col)}
        if self.rows*self.cols>self.total_mines+9:
            for dr in(-1,0,1):
                for dc in(-1,0,1):
                    nr,nc=safe_row+dr,safe_col+dc
                    if 0<=nr<self.rows and 0<=nc<self.cols:safe.add((nr,nc))
        all_pos=[(r,c) for r in range(self.rows) for c in range(self.cols) if(r,c) not in safe]
        count=min(self.total_mines,len(all_pos))
        self.mine_positions=set(random.sample(all_pos,count))
        for r,c in self.mine_positions:self.board[r][c]=-1
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c]==-1:continue
                self.board[r][c]=sum(1 for dr in(-1,0,1) for dc in(-1,0,1)
                    if(dr or dc) and 0<=r+dr<self.rows and 0<=c+dc<self.cols and self.board[r+dr][c+dc]==-1)
        self.mines_generated=True
    def reveal(self,row:int,col:int)->str:
        if self.game_over or self.game_won:return 'continue'
        if not(0<=row<self.rows and 0<=col<self.cols):return 'continue'
        if self.revealed[row][col] or self.flagged[row][col]:return 'continue'
        if self.first_click:self.generate_mines(row,col);self.first_click=False
        if self.board[row][col]==-1:self.game_over=True;self.revealed[row][col]=True;return 'game_over'
        self._flood_fill(row,col)
        if self.revealed_count>=self.total_safe_cells:self.game_won=True;return 'win'
        return 'continue'
    def _flood_fill(self,sr:int,sc:int):
        stack=[(sr,sc)]
        while stack:
            r,c=stack.pop()
            if not(0<=r<self.rows and 0<=c<self.cols):continue
            if self.revealed[r][c] or self.flagged[r][c]:continue
            if self.board[r][c]==-1:continue
            self.revealed[r][c]=True;self.revealed_count+=1
            if self.board[r][c]==0:
                for dr in(-1,0,1):
                    for dc in(-1,0,1):
                        if dr or dc:stack.append((r+dr,c+dc))
    def chord(self,row:int,col:int)->str:
        if self.game_over or self.game_won:return 'continue'
        if not self.revealed[row][col] or self.board[row][col]<=0:return 'continue'
        flag_cnt=0
        for dr in(-1,0,1):
            for dc in(-1,0,1):
                if dr==0 and dc==0:continue
                nr,nc=row+dr,col+dc
                if 0<=nr<self.rows and 0<=nc<self.cols and self.flagged[nr][nc]:flag_cnt+=1
        if flag_cnt!=self.board[row][col]:return 'continue'
        final='continue'
        for dr in(-1,0,1):
            for dc in(-1,0,1):
                if dr==0 and dc==0:continue
                nr,nc=row+dr,col+dc
                if 0<=nr<self.rows and 0<=nc<self.cols:
                    if not self.revealed[nr][nc] and not self.flagged[nr][nc]:
                        r=self.reveal(nr,nc)
                        if r=='game_over':final='game_over'
                        elif r=='win' and final!='game_over':final='win'
        return final
    def toggle_flag(self,row:int,col:int):
        if self.game_over or self.game_won:return
        if not(0<=row<self.rows and 0<=col<self.cols):return
        if self.revealed[row][col]:return
        self.flagged[row][col]=not self.flagged[row][col]
    @property
    def remaining_mines(self)->int:
        return self.total_mines-sum(self.flagged[r][c] for r in range(self.rows) for c in range(self.cols))

class GameFrame(tk.Frame):
    def __init__(self,parent,user:dict,difficulty:str,on_back):
        super().__init__(parent,bg='#e0e0e0')
        self.user=user;self.difficulty=difficulty;self.on_back=on_back
        self.cfg=DIFFICULTY_CONFIG[difficulty];self.game=MinesweeperGame(difficulty)
        self.cell_size=self.cfg['cell'];self.timer_running=False;self.timer_seconds=0;self._after_id=None;self.zoom=1.0
        self._gen_colors();self._build_ui();self._apply_window_size()
    def _gen_colors(self):
        self._grad_c1=_random_pastel();self._grad_c2=_random_pastel()
        self._grad_max=max(self.cfg['rows']+self.cfg['cols']-2,1)
    def _grad(self,r,c):return _cell_color(self._grad_c1,self._grad_c2,(r+c)/self._grad_max)
    def _apply_window_size(self):
        root=self.winfo_toplevel()
        if self.difficulty=='81x81':root.geometry("960x740")
        elif self.difficulty=='27x27':root.geometry("680x730")
        else:root.geometry("540x640")
        root.minsize(400,350);root.resizable(True,True)
        root.title(f"{t('title')} - {self.cfg['title']} - {self.user['username']}")
        root.bind('<Configure>',self._on_resize)
    def _on_resize(self,event):
        root=self.winfo_toplevel()
        if event.widget!=root or self.difficulty=='81x81':return
        if hasattr(self,'_resize_after'):self.after_cancel(self._resize_after)
        self._resize_after=self.after(150,self._do_resize)
    def _do_resize(self):
        root=self.winfo_toplevel()
        if not root.winfo_exists():return
        w=root.winfo_width()-28;h=root.winfo_height()-135
        new_cs=min(w//self.cfg['cols'],h//self.cfg['rows']);new_cs=max(16,min(new_cs,120))
        if new_cs!=self.cell_size:
            self.cell_size=new_cs
            self.canvas.configure(width=self.cfg['cols']*self.cell_size,height=self.cfg['rows']*self.cell_size)
            self._redraw()
    def _build_ui(self):
        bar=tk.Frame(self,bg='#d0d0d0',height=48);bar.pack(fill=tk.X,padx=3,pady=(3,0));bar.pack_propagate(False)
        ttk.Button(bar,text=t('btn_back'),command=self._back).pack(side=tk.LEFT,padx=6,pady=4)
        if os.path.exists(_BOMB_PNG):
            self._bomb_counter_img=tk.PhotoImage(file=_BOMB_PNG)
            tk.Label(bar,image=self._bomb_counter_img,bg='#d0d0d0').pack(side=tk.LEFT,padx=(10,2))
        self.mine_label=tk.Label(bar,font=('Consolas',15,'bold'),bg='#d0d0d0',fg='#333');self.mine_label.pack(side=tk.LEFT)
        tk.Label(bar,text=self.cfg['title'],font=('微软雅黑',12),bg='#d0d0d0',fg='#555').pack(side=tk.LEFT,expand=True)
        self.timer_label=tk.Label(bar,text="⏱ 00:00",font=('Consolas',15,'bold'),bg='#d0d0d0',fg='#333');self.timer_label.pack(side=tk.RIGHT,padx=15)
        self._update_mine_label()
        if self.difficulty=='81x81':self._build_large_board()
        else:self._build_small_board()
        bottom=tk.Frame(self,bg='#e0e0e0');bottom.pack(fill=tk.X,padx=10,pady=8)
        ttk.Button(bottom,text=t('btn_restart'),command=self.restart).pack(side=tk.LEFT,padx=5)
    def _build_small_board(self):
        w=self.cfg['cols']*self.cell_size;h=self.cfg['rows']*self.cell_size
        self.canvas=tk.Canvas(self,width=w,height=h,bg='#bdbdbd',highlightthickness=0,cursor='crosshair')
        self.canvas.pack(padx=8,pady=8,expand=True)
        self.canvas.bind('<Button-1>',self._left_click);self.canvas.bind('<Double-Button-1>',self._double_click)
        self.canvas.bind('<Button-3>',self._right_click);self.canvas.bind('<Button-2>',self._right_click)
        self._draw_small()
    def _draw_small(self):
        self.canvas.delete('all');cs=self.cell_size;g=self.game
        for r in range(g.rows):
            for c in range(g.cols):
                x1,y1=c*cs,r*cs;x2,y2=x1+cs,y1+cs;cx,cy=x1+cs//2,y1+cs//2
                if g.revealed[r][c]:
                    self.canvas.create_rectangle(x1,y1,x2,y2,fill='#ffffff',outline='#ccc')
                    val=g.board[r][c]
                    if val==-1:self.canvas.create_text(cx,cy,text='💣',font=('Arial',cs//2))
                    elif val>0:self.canvas.create_text(cx,cy,text=str(val),font=('Arial',cs//2,'bold'),fill=NUM_COLORS.get(val,'#000'))
                elif g.flagged[r][c]:
                    clr=self._grad(r,c);self.canvas.create_rectangle(x1,y1,x2,y2,fill=clr,outline='#999')
                    self.canvas.create_text(cx,cy,text='🚩',font=('Arial',cs//2))
                else:
                    clr=self._grad(r,c)
                    if(r+c)%2==1:clr=_lighten(clr,0.06)
                    self.canvas.create_rectangle(x1,y1,x2,y2,fill=clr,outline='#999')
                    self.canvas.create_rectangle(x1+1,y1+1,x2-1,y2-1,fill=clr,outline='')
    def _build_large_board(self):
        outer=tk.Frame(self,bg='#e0e0e0');outer.pack(fill=tk.BOTH,expand=True,padx=8,pady=8)
        outer.grid_rowconfigure(0,weight=1);outer.grid_columnconfigure(0,weight=1)
        cw=min(self.cfg['cols']*self.cell_size,780);ch=min(self.cfg['rows']*self.cell_size,560)
        self.scroll_canvas=tk.Canvas(outer,width=cw,height=ch,bg='#bdbdbd',highlightthickness=0)
        self.h_bar=ttk.Scrollbar(outer,orient=tk.HORIZONTAL,command=self.scroll_canvas.xview)
        self.v_bar=ttk.Scrollbar(outer,orient=tk.VERTICAL,command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(xscrollcommand=self.h_bar.set,yscrollcommand=self.v_bar.set)
        self.scroll_canvas.grid(row=0,column=0,sticky='nsew')
        self.h_bar.grid(row=1,column=0,sticky='ew');self.v_bar.grid(row=0,column=1,sticky='ns')
        fw=self.cfg['cols']*self.cell_size;fh=self.cfg['rows']*self.cell_size
        self.canvas=tk.Canvas(self.scroll_canvas,width=fw,height=fh,bg='#bdbdbd',highlightthickness=0)
        self.scroll_canvas.create_window(0,0,window=self.canvas,anchor='nw')
        self.scroll_canvas.configure(scrollregion=(0,0,fw,fh))
        self.canvas.bind('<Button-1>',self._left_click);self.canvas.bind('<Double-Button-1>',self._double_click)
        self.canvas.bind('<Button-3>',self._right_click);self.canvas.bind('<Button-2>',self._right_click)
        zf=tk.Frame(self,bg='#e0e0e0');zf.pack(fill=tk.X,padx=8,pady=(0,5))
        ttk.Button(zf,text="🔍−",command=self._zoom_out,width=4).pack(side=tk.LEFT,padx=2)
        self.zoom_label=tk.Label(zf,text="100%",font=('微软雅黑',9),bg='#e0e0e0',width=5);self.zoom_label.pack(side=tk.LEFT,padx=4)
        ttk.Button(zf,text="🔍+",command=self._zoom_in,width=4).pack(side=tk.LEFT,padx=2)
        ttk.Button(zf,text="适应窗口",command=self._zoom_reset,width=9).pack(side=tk.LEFT,padx=10)
        self.canvas.bind('<MouseWheel>',self._on_mousewheel);self._draw_large()
    def _draw_large(self):
        self.canvas.delete('all');cs=max(2,int(self.cell_size*self.zoom));self._actual_cs=cs;g=self.game
        for r in range(g.rows):
            for c in range(g.cols):
                x1,y1=c*cs+1,r*cs+1;x2,y2=x1+cs-2,y1+cs-2;cx,cy=x1+(cs-2)//2,y1+(cs-2)//2
                if g.revealed[r][c]:
                    self.canvas.create_rectangle(x1,y1,x2,y2,fill='#ffffff',outline='')
                    val=g.board[r][c]
                    if val==-1:
                        if cs>=10:self.canvas.create_text(cx,cy,text='💣',font=('Arial',max(8,cs//2)))
                    elif val>0:
                        if cs>=10:self.canvas.create_text(cx,cy,text=str(val),font=('Arial',max(8,cs//2),'bold'),fill=NUM_COLORS.get(val,'#000'))
                        else:
                            clr={1:'#bbdefb',2:'#c8e6c9',3:'#ffcdd2',4:'#b39ddb',5:'#ffccbc',6:'#b2dfdb',7:'#cfd8dc',8:'#d7ccc8'}.get(val,'#d8d8d8')
                            self.canvas.create_rectangle(x1,y1,x2,y2,fill=clr,outline='')
                elif g.flagged[r][c]:
                    clr=self._grad(r,c);self.canvas.create_rectangle(x1,y1,x2,y2,fill=clr,outline='')
                    if cs>=12:self.canvas.create_text(cx,cy,text='🚩',font=('Arial',max(8,cs//2)))
                else:
                    clr=self._grad(r,c)
                    if(r+c)%2==1:clr=_lighten(clr,0.06)
                    self.canvas.create_rectangle(x1,y1,x2,y2,fill=clr,outline='')
        fw=g.cols*cs;fh=g.rows*cs
        self.canvas.configure(width=fw,height=fh);self.scroll_canvas.configure(scrollregion=(0,0,fw,fh))
    def _zoom_in(self):self.zoom=min(3.0,self.zoom+0.25);self.zoom_label.config(text=f"{int(self.zoom*100)}%");self._draw_large()
    def _zoom_out(self):self.zoom=max(0.25,self.zoom-0.25);self.zoom_label.config(text=f"{int(self.zoom*100)}%");self._draw_large()
    def _zoom_reset(self):self.zoom=1.0;self.zoom_label.config(text="100%");self._draw_large()
    def _on_mousewheel(self,event):
        if event.state&0x4:
            if event.delta>0:self._zoom_in()
            else:self._zoom_out()
        else:self.scroll_canvas.yview_scroll(-1*(event.delta//120),'units')
    def _get_cell(self,x:int,y:int):
        cs=getattr(self,'_actual_cs',self.cell_size)
        r,c=int(y//cs),int(x//cs)
        if 0<=r<self.game.rows and 0<=c<self.game.cols:return r,c
        return None,None
    def _left_click(self,event):
        if self.game.game_over or self.game.game_won:return
        r,c=self._get_cell(event.x,event.y)
        if r is None:return
        if not self.timer_running:self._start_timer()
        result=self.game.reveal(r,c);self._redraw();self._update_mine_label()
        if result=='game_over':self._stop_timer();self._reveal_all_mines();self.after(200,lambda:messagebox.showinfo(t('game_over'),t('game_over_msg')))
        elif result=='win':self._stop_timer();self.after(200,self._on_win)
    def _right_click(self,event):
        if self.game.game_over or self.game.game_won:return
        r,c=self._get_cell(event.x,event.y)
        if r is None:return
        self.game.toggle_flag(r,c);self._redraw();self._update_mine_label()
    def _double_click(self,event):
        if self.game.game_over or self.game.game_won:return
        r,c=self._get_cell(event.x,event.y)
        if r is None:return
        if not self.game.revealed[r][c]:return
        result=self.game.chord(r,c);self._redraw();self._update_mine_label()
        if result=='game_over':self._stop_timer();self._reveal_all_mines();self.after(200,lambda:messagebox.showinfo(t('game_over'),t('game_over_msg')))
        elif result=='win':self._stop_timer();self.after(200,self._on_win)
    def _redraw(self):
        if self.difficulty=='81x81':self._draw_large()
        else:self._draw_small()
    def _start_timer(self):self.timer_running=True;self.timer_seconds=0;self._tick()
    def _tick(self):
        if not self.timer_running:return
        self.timer_seconds+=1;m,s=divmod(self.timer_seconds,60)
        self.timer_label.config(text=f"⏱ {m:02d}:{s:02d}");self._after_id=self.after(1000,self._tick)
    def _stop_timer(self):
        self.timer_running=False
        if self._after_id:self.after_cancel(self._after_id);self._after_id=None
    def _update_mine_label(self):self.mine_label.config(text=str(self.game.remaining_mines))
    def _reveal_all_mines(self):
        g=self.game
        for r in range(g.rows):
            for c in range(g.cols):
                if g.board[r][c]==-1 and not g.flagged[r][c]:g.revealed[r][c]=True
        self._redraw()
    def _on_win(self):
        save_ranking(self.user['id'],self.difficulty,self.timer_seconds)
        m,s=divmod(self.timer_seconds,60)
        messagebox.showinfo(t('win_title'),t('win_msg',self.cfg['title'],f"{m:02d}:{s:02d}"))
        threading.Thread(target=_gitee_append_ranking,args=(self.user['username'],self.difficulty,self.timer_seconds),daemon=True).start()
    def _back(self):
        self._stop_timer();root=self.winfo_toplevel();root.unbind('<Configure>');self.on_back()
    def restart(self):
        self._stop_timer();self.timer_seconds=0;self.timer_label.config(text="⏱ 00:00")
        self.game=MinesweeperGame(self.difficulty)
        self._gen_colors();self._redraw();self._update_mine_label()
