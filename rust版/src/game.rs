//! 扫雷核心逻辑：棋盘、布雷、翻开、标记、快速展开。
//!
//! 与 UI 完全解耦，方便移植与测试。

use std::collections::HashSet;

use rand::seq::SliceRandom;

use crate::solver::is_no_guess;

pub enum RevealResult {
    Continue,
    GameOver,
    Win,
}

pub struct Board {
    pub rows: usize,
    pub cols: usize,
    pub mines: usize,
    pub cells: Vec<i32>,
    pub revealed: Vec<bool>,
    pub flagged: Vec<bool>,
    pub game_over: bool,
    pub won: bool,
    pub first_click: bool,
    pub mines_generated: bool,
    pub triggered_mine: Option<usize>,
}

impl Board {
    pub fn new(rows: usize, cols: usize, mines: usize) -> Self {
        let n = rows * cols;
        Board {
            rows,
            cols,
            mines,
            cells: vec![0; n],
            revealed: vec![false; n],
            flagged: vec![false; n],
            game_over: false,
            won: false,
            first_click: true,
            mines_generated: false,
            triggered_mine: None,
        }
    }

    pub fn len(&self) -> usize {
        self.rows * self.cols
    }

    pub fn neighbors(&self, idx: usize) -> Vec<usize> {
        let r = (idx / self.cols) as i32;
        let c = (idx % self.cols) as i32;
        let mut out = Vec::with_capacity(8);
        for dr in -1i32..=1 {
            for dc in -1i32..=1 {
                if dr == 0 && dc == 0 {
                    continue;
                }
                let nr = r + dr;
                let nc = c + dc;
                if nr >= 0 && nr < self.rows as i32 && nc >= 0 && nc < self.cols as i32 {
                    out.push(nr as usize * self.cols + nc as usize);
                }
            }
        }
        out
    }

    /// 首次点击后生成雷区，保证无猜（约束传播可解）。
    pub fn generate_mines(&mut self, safe_idx: usize) {
        if self.mines_generated {
            return;
        }
        let mut safe = HashSet::new();
        safe.insert(safe_idx);
        if self.len() > self.mines + 9 {
            for nb in self.neighbors(safe_idx) {
                safe.insert(nb);
            }
        }
        let candidates: Vec<usize> = (0..self.len()).filter(|i| !safe.contains(i)).collect();
        let max_retries = if self.len() <= 27 * 27 { 60 } else { 6 };
        let mut rng = rand::rng();
        for _ in 0..max_retries {
            let mut chosen = candidates.clone();
            chosen.shuffle(&mut rng);
            chosen.truncate(self.mines);
            let mine_set: HashSet<usize> = chosen.into_iter().collect();
            self.place_mines(&mine_set);
            if is_no_guess(self.rows, self.cols, &self.cells, safe_idx) {
                break;
            }
        }
        self.mines_generated = true;
    }

    fn place_mines(&mut self, mine_set: &HashSet<usize>) {
        for (i, cell) in self.cells.iter_mut().enumerate() {
            *cell = if mine_set.contains(&i) { -1 } else { 0 };
        }
        for i in 0..self.len() {
            if self.cells[i] != -1 {
                self.cells[i] = self
                    .neighbors(i)
                    .iter()
                    .filter(|&&nb| self.cells[nb] == -1)
                    .count() as i32;
            }
        }
    }

    pub fn reveal(&mut self, idx: usize) -> RevealResult {
        if self.game_over || self.won {
            return RevealResult::Continue;
        }
        if self.revealed[idx] || self.flagged[idx] {
            return RevealResult::Continue;
        }
        if self.first_click {
            self.generate_mines(idx);
            self.first_click = false;
        }
        if self.cells[idx] == -1 {
            self.game_over = true;
            self.revealed[idx] = true;
            self.triggered_mine = Some(idx);
            return RevealResult::GameOver;
        }
        self.flood_fill(idx);
        if self.revealed_count() >= self.len() - self.mines {
            self.won = true;
            return RevealResult::Win;
        }
        RevealResult::Continue
    }

    fn flood_fill(&mut self, start: usize) {
        let mut stack = vec![start];
        while let Some(cur) = stack.pop() {
            if self.revealed[cur] || self.flagged[cur] || self.cells[cur] == -1 {
                continue;
            }
            self.revealed[cur] = true;
            if self.cells[cur] == 0 {
                stack.extend(self.neighbors(cur));
            }
        }
    }

    pub fn toggle_flag(&mut self, idx: usize) {
        if self.game_over || self.won {
            return;
        }
        if !self.revealed[idx] {
            self.flagged[idx] = !self.flagged[idx];
        }
    }

    pub fn chord(&mut self, idx: usize) -> RevealResult {
        if self.game_over || self.won {
            return RevealResult::Continue;
        }
        if !self.revealed[idx] || self.cells[idx] <= 0 {
            return RevealResult::Continue;
        }
        let flag_count = self.neighbors(idx).iter().filter(|&&nb| self.flagged[nb]).count();
        if flag_count != self.cells[idx] as usize {
            return RevealResult::Continue;
        }
        let mut result = RevealResult::Continue;
        for nb in self.neighbors(idx) {
            if !self.revealed[nb] && !self.flagged[nb] {
                match self.reveal(nb) {
                    RevealResult::GameOver => result = RevealResult::GameOver,
                    RevealResult::Win => {
                        if !matches!(result, RevealResult::GameOver) {
                            result = RevealResult::Win;
                        }
                    }
                    RevealResult::Continue => {}
                }
            }
        }
        result
    }

    pub fn revealed_count(&self) -> usize {
        self.revealed.iter().filter(|&&r| r).count()
    }

    pub fn remaining_mines(&self) -> i32 {
        let flagged = self.flagged.iter().filter(|&&f| f).count() as i32;
        self.mines as i32 - flagged
    }

    /// 失败时翻开所有雷，返回插错位置的旗子集合。
    pub fn reveal_all_mines(&mut self) -> HashSet<usize> {
        let mut wrong_flags = HashSet::new();
        for i in 0..self.len() {
            if self.cells[i] == -1 {
                if !self.flagged[i] {
                    self.revealed[i] = true;
                }
            } else if self.flagged[i] {
                wrong_flags.insert(i);
            }
        }
        wrong_flags
    }
}
