//! 无猜求解器：约束传播验证棋盘能否不靠猜测解完全局。
//!
//! 借鉴扫雷求解器的约束传播思想（如 mrgriscom/minesweepr），两个基本规则：
//! - 规则 1（确定安全）：某数字格周围已标记雷数 == 该数字，则周围未翻开格都是安全的。
//! - 规则 2（确定是雷）：某数字格周围未标记未翻开格数 == 剩余雷数，则这些格全是雷。

use std::collections::HashSet;

/// 返回 idx 的所有邻居（8 方向）。
fn neighbors(rows: usize, cols: usize, idx: usize) -> Vec<usize> {
    let r = (idx / cols) as i32;
    let c = (idx % cols) as i32;
    let mut out = Vec::with_capacity(8);
    for dr in -1i32..=1 {
        for dc in -1i32..=1 {
            if dr == 0 && dc == 0 {
                continue;
            }
            let nr = r + dr;
            let nc = c + dc;
            if nr >= 0 && nr < rows as i32 && nc >= 0 && nc < cols as i32 {
                out.push(nr as usize * cols + nc as usize);
            }
        }
    }
    out
}

/// 约束传播求解器。
struct Solver<'a> {
    rows: usize,
    cols: usize,
    cells: &'a [i32],
    revealed: Vec<bool>,
    flagged: Vec<bool>,
    pending: HashSet<usize>,
}

impl<'a> Solver<'a> {
    /// 翻开 idx；若是 0 则 flood fill 展开。
    fn reveal_cell(&mut self, idx: usize) {
        if self.revealed[idx] || self.flagged[idx] || self.cells[idx] == -1 {
            return;
        }
        self.revealed[idx] = true;
        if self.cells[idx] == 0 {
            let mut stack = vec![idx];
            while let Some(cur) = stack.pop() {
                for nb in neighbors(self.rows, self.cols, cur) {
                    if !self.revealed[nb] && !self.flagged[nb] && self.cells[nb] != -1 {
                        self.revealed[nb] = true;
                        if self.cells[nb] == 0 {
                            stack.push(nb);
                        } else {
                            self.pending.insert(nb);
                        }
                    }
                }
            }
        } else {
            self.pending.insert(idx);
        }
        self.touch(idx);
    }

    /// idx 状态变化后，把周围已翻开的数字格重新加入待处理集合。
    fn touch(&mut self, idx: usize) {
        for nb in neighbors(self.rows, self.cols, idx) {
            if self.revealed[nb] && self.cells[nb] > 0 {
                self.pending.insert(nb);
            }
        }
    }

    fn solve(&mut self, start: usize) -> bool {
        self.reveal_cell(start);
        while !self.pending.is_empty() {
            let idx = *self.pending.iter().next().unwrap();
            self.pending.remove(&idx);
            if !self.revealed[idx] || self.cells[idx] <= 0 {
                continue;
            }
            let nbs = neighbors(self.rows, self.cols, idx);
            let flagged_n = nbs.iter().filter(|&&nb| self.flagged[nb]).count() as i32;
            let unknown: Vec<usize> = nbs
                .into_iter()
                .filter(|&nb| !self.revealed[nb] && !self.flagged[nb])
                .collect();
            let remaining = self.cells[idx] - flagged_n;
            if remaining == 0 {
                for nb in unknown {
                    self.reveal_cell(nb);
                }
            } else if remaining > 0 && unknown.len() as i32 == remaining {
                for nb in unknown {
                    self.flagged[nb] = true;
                    self.touch(nb);
                }
            }
        }
        for i in 0..self.rows * self.cols {
            if self.cells[i] != -1 && !self.revealed[i] {
                return false;
            }
        }
        true
    }
}

/// 从 start 出发，判断约束传播能否解开所有安全格。
pub fn is_no_guess(rows: usize, cols: usize, cells: &[i32], start: usize) -> bool {
    let mut solver = Solver {
        rows,
        cols,
        cells,
        revealed: vec![false; rows * cols],
        flagged: vec![false; rows * cols],
        pending: HashSet::new(),
    };
    solver.solve(start)
}
