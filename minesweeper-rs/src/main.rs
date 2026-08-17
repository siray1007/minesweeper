#![windows_subsystem = "windows"]

mod game;
mod solver;
mod sound;
mod storage;

use std::collections::HashSet;
use std::time::{Duration, Instant};

use eframe::egui::{self, Align2, Color32, FontId, Pos2, Rect, Sense, Stroke, StrokeKind, Vec2};

use game::{Board, RevealResult};

// —— 配色 token（对齐 Python 版深色主题）——
const BG: Color32 = Color32::from_rgb(0x10, 0x2a, 0x43);
const SURFACE: Color32 = Color32::from_rgb(0x17, 0x3b, 0x57);
const SURFACE_ALT: Color32 = Color32::from_rgb(0x21, 0x4c, 0x69);
const SURFACE_METAL: Color32 = Color32::from_rgb(0x2b, 0x58, 0x73);
const SURFACE_HOVER: Color32 = Color32::from_rgb(0x35, 0x69, 0x83);
const BORDER: Color32 = Color32::from_rgb(0x5c, 0x7f, 0x96);
const BORDER_HOT: Color32 = Color32::from_rgb(0x64, 0xdd, 0xf2);
const TEXT: Color32 = Color32::from_rgb(0xf5, 0xfb, 0xff);
const MUTED: Color32 = Color32::from_rgb(0xc4, 0xd7, 0xe2);
const PRIMARY: Color32 = Color32::from_rgb(0x55, 0xd8, 0xee);
const PRIMARY_DARK: Color32 = Color32::from_rgb(0x07, 0x10, 0x19);
const SUCCESS: Color32 = Color32::from_rgb(0x6e, 0xe7, 0xb7);
const DANGER: Color32 = Color32::from_rgb(0xff, 0x6f, 0x91);
// 棋盘未打开格渐变端点（青蓝 → 薄荷绿）
const GRAD_START: Color32 = Color32::from_rgb(0x33, 0xbf, 0xe4);
const GRAD_END: Color32 = Color32::from_rgb(0x64, 0xdf, 0xb8);

#[derive(Clone, Copy, PartialEq)]
enum Difficulty {
    Easy,
    Medium,
    Hard,
}

impl Difficulty {
    fn config(self) -> (usize, usize, usize, f32) {
        match self {
            Difficulty::Easy => (9, 9, 10, 36.0),
            Difficulty::Medium => (27, 27, 100, 22.0),
            Difficulty::Hard => (81, 81, 800, 14.0),
        }
    }

    fn label(self) -> &'static str {
        match self {
            Difficulty::Easy => "训练 9×9",
            Difficulty::Medium => "进阶 27×27",
            Difficulty::Hard => "极限 81×81",
        }
    }

    fn key(self) -> &'static str {
        match self {
            Difficulty::Easy => "9x9",
            Difficulty::Medium => "27x27",
            Difficulty::Hard => "81x81",
        }
    }
}

enum Screen {
    Auth,
    Lobby,
    Game,
    Leaderboard,
}

#[derive(PartialEq, Clone, Copy)]
enum AuthMode {
    Login,
    Register,
}

struct AuthState {
    mode: AuthMode,
    username: String,
    password: String,
    confirm: String,
    message: String,
}

impl AuthState {
    fn new() -> Self {
        AuthState {
            mode: AuthMode::Login,
            username: String::new(),
            password: String::new(),
            confirm: String::new(),
            message: String::new(),
        }
    }
}

/// 爆炸粒子（坐标相对棋盘左上角）。
struct Particle {
    pos: Vec2,
    vel: Vec2,
    color: Color32,
    born: Instant,
    life: f32,
    size: f32,
}

struct GameState {
    board: Board,
    difficulty: Difficulty,
    cell_size: f32,
    start_time: Option<Instant>,
    elapsed: Duration,
    wrong_flags: HashSet<usize>,
    particles: Vec<Particle>,
    recorded: bool,
}

impl GameState {
    fn new(difficulty: Difficulty) -> Self {
        let (rows, cols, mines, cell_size) = difficulty.config();
        GameState {
            board: Board::new(rows, cols, mines),
            difficulty,
            cell_size,
            start_time: None,
            elapsed: Duration::ZERO,
            wrong_flags: HashSet::new(),
            particles: Vec::new(),
            recorded: false,
        }
    }
}

struct App {
    screen: Screen,
    current_user: Option<String>,
    auth: AuthState,
    game: GameState,
}

impl App {
    fn new() -> Self {
        App {
            screen: Screen::Auth,
            current_user: None,
            auth: AuthState::new(),
            game: GameState::new(Difficulty::Easy),
        }
    }

    fn number_color(value: i32) -> Color32 {
        match value {
            1 => Color32::from_rgb(0x4f, 0xa8, 0xe8),
            2 => Color32::from_rgb(0x3f, 0xc8, 0x86),
            3 => Color32::from_rgb(0xff, 0x6b, 0x81),
            4 => Color32::from_rgb(0xa9, 0x8c, 0xff),
            5 => Color32::from_rgb(0xff, 0xc0, 0x5a),
            6 => Color32::from_rgb(0x3f, 0xd0, 0xc8),
            7 => Color32::from_rgb(0xe0, 0xe6, 0xee),
            _ => Color32::from_rgb(0x9a, 0xa8, 0xb8),
        }
    }

    fn start_game(&mut self, difficulty: Difficulty) {
        self.game = GameState::new(difficulty);
        self.screen = Screen::Game;
    }

    fn record_result(&mut self, won: bool) {
        if self.game.recorded {
            return;
        }
        self.game.recorded = true;
        if let Some(user) = &self.current_user {
            let secs = self.game.elapsed.as_secs() as u32;
            storage::add_record(user, self.game.difficulty.key(), secs, won);
        }
    }
}

impl eframe::App for App {
    fn ui(&mut self, ui: &mut egui::Ui, _frame: &mut eframe::Frame) {
        let ctx = ui.ctx().clone();
        let dt = ui.input(|i| i.stable_dt).min(0.05);

        match self.screen {
            Screen::Auth => self.auth_screen(ui),
            Screen::Lobby => self.lobby_screen(ui),
            Screen::Game => self.game_screen(ui, &ctx, dt),
            Screen::Leaderboard => self.leaderboard_screen(ui),
        }
    }
}

impl App {
    fn auth_screen(&mut self, ui: &mut egui::Ui) {
        ui.vertical_centered(|ui| {
            ui.add_space(48.0);
            ui.label(egui::RichText::new("扫 雷").size(42.0).strong().color(PRIMARY));
            ui.label(egui::RichText::new("MINESWEEPER").size(12.0).color(MUTED));
            ui.add_space(28.0);

            let is_register = self.auth.mode == AuthMode::Register;
            egui::Frame::new()
                .fill(SURFACE)
                .stroke(Stroke::new(1.0, BORDER))
                .corner_radius(12.0)
                .inner_margin(egui::Margin::same(24))
                .show(ui, |ui| {
                    ui.set_width(300.0);
                    let title = if is_register { "创建账号" } else { "登录账号" };
                    ui.label(egui::RichText::new(title).size(18.0).strong().color(TEXT));
                    ui.add_space(12.0);

                    ui.add(egui::TextEdit::singleline(&mut self.auth.username).hint_text("用户名").desired_width(260.0));
                    ui.add_space(8.0);
                    ui.add(egui::TextEdit::singleline(&mut self.auth.password).password(true).hint_text("密码").desired_width(260.0));
                    if is_register {
                        ui.add_space(8.0);
                        ui.add(egui::TextEdit::singleline(&mut self.auth.confirm).password(true).hint_text("确认密码").desired_width(260.0));
                    }
                    ui.add_space(16.0);

                    let btn_text = if is_register { "注册" } else { "登录" };
                    let btn = egui::Button::new(egui::RichText::new(btn_text).size(15.0).strong().color(PRIMARY_DARK))
                        .fill(PRIMARY)
                        .corner_radius(6.0)
                        .min_size(Vec2::new(260.0, 36.0));
                    if ui.add(btn).clicked() {
                        if is_register {
                            let (u, p, c) = (self.auth.username.clone(), self.auth.password.clone(), self.auth.confirm.clone());
                            if p != c {
                                self.auth.message = "两次密码不一致".to_string();
                            } else {
                                match storage::register(&u, &p) {
                                    Ok(()) => {
                                        self.auth.message = "注册成功，请登录".to_string();
                                        self.auth.mode = AuthMode::Login;
                                    }
                                    Err(e) => self.auth.message = e,
                                }
                            }
                        } else {
                            let (u, p) = (self.auth.username.clone(), self.auth.password.clone());
                            match storage::login(&u, &p) {
                                Ok(()) => {
                                    self.current_user = Some(u);
                                    self.screen = Screen::Lobby;
                                }
                                Err(e) => self.auth.message = e,
                            }
                        }
                    }

                    if !self.auth.message.is_empty() {
                        ui.add_space(8.0);
                        ui.colored_label(DANGER, &self.auth.message);
                    }

                    ui.add_space(12.0);
                    let toggle_text = if is_register { "已有账号？去登录" } else { "没有账号？去注册" };
                    if ui.add_sized([260.0, 32.0], egui::Button::new(toggle_text)).clicked() {
                        self.auth.mode = if is_register { AuthMode::Login } else { AuthMode::Register };
                        self.auth.message.clear();
                    }
                });
        });
    }

    fn lobby_screen(&mut self, ui: &mut egui::Ui) {
        ui.vertical_centered(|ui| {
            ui.add_space(28.0);
            ui.label(egui::RichText::new("作战大厅").size(28.0).strong().color(TEXT));
            if let Some(user) = &self.current_user {
                ui.label(egui::RichText::new(format!("当前玩家：{}", user)).size(13.0).color(MUTED));
            }
            ui.add_space(20.0);

            for d in [Difficulty::Easy, Difficulty::Medium, Difficulty::Hard] {
                let (rows, cols, mines, _) = d.config();
                let best = self.current_user.as_ref().and_then(|u| storage::best_time(u, d.key()));
                egui::Frame::new()
                    .fill(SURFACE)
                    .stroke(Stroke::new(1.0, BORDER))
                    .corner_radius(10.0)
                    .inner_margin(egui::Margin::symmetric(18, 14))
                    .show(ui, |ui| {
                        ui.set_width(320.0);
                        ui.horizontal(|ui| {
                            ui.label(egui::RichText::new(d.label()).size(16.0).strong().color(TEXT));
                            ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                                let btn = egui::Button::new(egui::RichText::new("开始").strong().color(PRIMARY_DARK))
                                    .fill(PRIMARY)
                                    .corner_radius(6.0);
                                if ui.add(btn).clicked() {
                                    self.start_game(d);
                                }
                            });
                        });
                        ui.label(egui::RichText::new(format!("{}×{} · {} 雷", rows, cols, mines)).size(12.0).color(MUTED));
                        if let Some(t) = best {
                            ui.label(egui::RichText::new(format!("最佳：{}", format_time(t))).size(12.0).color(SUCCESS));
                        }
                    });
                ui.add_space(10.0);
            }

            ui.add_space(14.0);
            if ui.add_sized([320.0, 34.0], egui::Button::new("🏆 排行榜")).clicked() {
                self.screen = Screen::Leaderboard;
            }
            ui.add_space(8.0);
            if ui.add_sized([320.0, 34.0], egui::Button::new("退出登录")).clicked() {
                self.current_user = None;
                self.screen = Screen::Auth;
            }
        });
    }

    fn leaderboard_screen(&mut self, ui: &mut egui::Ui) {
        ui.vertical_centered(|ui| {
            ui.add_space(24.0);
            ui.label(egui::RichText::new("排行榜").size(28.0).strong().color(TEXT));
            ui.add_space(16.0);

            for d in [Difficulty::Easy, Difficulty::Medium, Difficulty::Hard] {
                let records = storage::leaderboard(d.key(), 10);
                egui::Frame::new()
                    .fill(SURFACE)
                    .stroke(Stroke::new(1.0, BORDER))
                    .corner_radius(10.0)
                    .inner_margin(egui::Margin::symmetric(18, 14))
                    .show(ui, |ui| {
                        ui.set_width(360.0);
                        ui.label(egui::RichText::new(d.label()).size(15.0).strong().color(PRIMARY));
                        ui.add_space(6.0);
                        if records.is_empty() {
                            ui.label(egui::RichText::new("暂无记录").color(MUTED));
                        } else {
                            egui::Grid::new(format!("grid_{}", d.key()))
                                .num_columns(3)
                                .striped(true)
                                .min_col_width(80.0)
                                .show(ui, |ui| {
                                    ui.label(egui::RichText::new("名次").strong().color(MUTED));
                                    ui.label(egui::RichText::new("玩家").strong().color(MUTED));
                                    ui.label(egui::RichText::new("用时").strong().color(MUTED));
                                    ui.end_row();
                                    for (i, r) in records.iter().enumerate() {
                                        let rank_color = match i {
                                            0 => Color32::from_rgb(0xff, 0xd1, 0x66),
                                            1 => Color32::from_rgb(0xc4, 0xd7, 0xe2),
                                            2 => Color32::from_rgb(0xd0, 0x87, 0x70),
                                            _ => MUTED,
                                        };
                                        ui.label(egui::RichText::new(format!("{}", i + 1)).strong().color(rank_color));
                                        ui.label(&r.username);
                                        ui.label(egui::RichText::new(format_time(r.time_seconds)).monospace());
                                        ui.end_row();
                                    }
                                });
                        }
                    });
                ui.add_space(10.0);
            }

            ui.add_space(12.0);
            if ui.add_sized([360.0, 34.0], egui::Button::new("返回大厅")).clicked() {
                self.screen = Screen::Lobby;
            }
        });
    }

    fn game_screen(&mut self, ui: &mut egui::Ui, ctx: &egui::Context, dt: f32) {
        // 计时更新
        if let Some(start) = self.game.start_time {
            if !self.game.board.game_over && !self.game.board.won {
                self.game.elapsed = start.elapsed();
                ctx.request_repaint_after(Duration::from_millis(1000));
            }
        }

        // 粒子 + reveal 动画持续重绘
        if !self.game.particles.is_empty() {
            self.update_particles(dt);
            ctx.request_repaint();
        }
        // HUD
        ui.horizontal(|ui| {
            if ui.button("← 大厅").clicked() {
                self.screen = Screen::Lobby;
            }
            ui.separator();
            let remaining = self.game.board.remaining_mines();
            ui.label(egui::RichText::new(format!("💣 {}", remaining.max(0))).monospace().size(15.0).color(TEXT));
            ui.separator();
            let secs = self.game.elapsed.as_secs();
            ui.label(egui::RichText::new(format!("⏱ {:02}:{:02}", secs / 60, secs % 60)).monospace().size(15.0).color(TEXT));
            ui.separator();
            let restart = egui::Button::new(egui::RichText::new("重新开始").strong().color(PRIMARY_DARK))
                .fill(PRIMARY)
                .corner_radius(6.0);
            if ui.add(restart).clicked() {
                let d = self.game.difficulty;
                self.game = GameState::new(d);
            }
        });
        ui.separator();

        // 棋盘
        let board_size = Vec2::new(
            self.game.board.cols as f32 * self.game.cell_size,
            self.game.board.rows as f32 * self.game.cell_size,
        );
        ui.vertical_centered(|ui| {
            let (response, painter) = ui.allocate_painter(board_size, Sense::click());
            let origin = response.rect.min;
            self.handle_input(&response, origin);
            self.draw_board(&painter, origin);
            self.draw_particles(&painter, origin);
        });

        // 结果弹窗
        if self.game.board.game_over || self.game.board.won {
            let (text, color) = if self.game.board.won {
                ("🎉 你赢了！", Color32::from_rgb(0x3f, 0xc8, 0x86))
            } else {
                ("💥 踩到雷了", Color32::from_rgb(0xff, 0x6b, 0x81))
            };
            egui::Window::new("结果")
                .collapsible(false)
                .resizable(false)
                .anchor(Align2::CENTER_CENTER, [0.0, 0.0])
                .show(ctx, |ui| {
                    ui.colored_label(color, egui::RichText::new(text).size(18.0).strong());
                    ui.add_space(10.0);
                    let again = egui::Button::new(egui::RichText::new("再来一局").strong().color(PRIMARY_DARK))
                        .fill(PRIMARY)
                        .corner_radius(6.0)
                        .min_size(Vec2::new(160.0, 34.0));
                    if ui.add(again).clicked() {
                        let d = self.game.difficulty;
                        self.game = GameState::new(d);
                    }
                    if ui.add_sized([160.0, 32.0], egui::Button::new("返回大厅")).clicked() {
                        self.screen = Screen::Lobby;
                    }
                });
        }
    }
}

fn format_time(secs: u32) -> String {
    format!("{:02}:{:02}", secs / 60, secs % 60)
}

// —— 游戏逻辑与绘制 ——

impl App {
    fn lerp_color(a: Color32, b: Color32, t: f32) -> Color32 {
        let t = t.clamp(0.0, 1.0);
        let l = |x: u8, y: u8| (x as f32 + (y as f32 - x as f32) * t) as u8;
        Color32::from_rgb(l(a.r(), b.r()), l(a.g(), b.g()), l(a.b(), b.b()))
    }

    fn gradient_color(row: usize, col: usize, rows: usize, cols: usize) -> Color32 {
        let denom = (rows + cols - 2).max(1) as f32;
        let t = (row + col) as f32 / denom;
        Self::lerp_color(GRAD_START, GRAD_END, t)
    }

    fn draw_board(&self, painter: &egui::Painter, origin: Pos2) {
        let cs = self.game.cell_size;
        let open = Color32::from_rgb(0xd7, 0xe6, 0xec);
        let open_alt = Color32::from_rgb(0xcf, 0xde, 0xe5);
        let mine_bg = Color32::from_rgb(0xff, 0x6f, 0x91);
        let flag_bg = Color32::from_rgb(0xa8, 0x3f, 0x62);

        for r in 0..self.game.board.rows {
            for c in 0..self.game.board.cols {
                let idx = r * self.game.board.cols + c;
                let rect = Rect::from_min_size(
                    egui::pos2(origin.x + c as f32 * cs, origin.y + r as f32 * cs),
                    Vec2::splat(cs),
                );

                if self.game.board.revealed[idx] {
                    let base = if (r + c) % 2 == 0 { open } else { open_alt };
                    painter.rect_filled(rect, 0.0, base);
                    let value = self.game.board.cells[idx];
                    if value == -1 {
                        painter.rect_filled(rect.shrink(2.0), 2.0, mine_bg);
                    } else if value > 0 {
                        painter.text(
                            rect.center(),
                            Align2::CENTER_CENTER,
                            value.to_string(),
                            FontId::proportional(cs * 0.55),
                            Self::number_color(value),
                        );
                    }
                } else if self.game.board.flagged[idx] {
                    painter.rect_filled(rect, 0.0, flag_bg);
                    let wrong = self.game.wrong_flags.contains(&idx);
                    let mark = if wrong { "X" } else { "⚑" };
                    painter.text(
                        rect.center(),
                        Align2::CENTER_CENTER,
                        mark,
                        FontId::proportional(cs * 0.55),
                        Color32::WHITE,
                    );
                } else {
                    // 对角渐变：未打开格形成青蓝 → 薄荷绿的连续过渡
                    let bg = Self::gradient_color(r, c, self.game.board.rows, self.game.board.cols);
                    painter.rect_filled(rect, 0.0, bg);
                    painter.rect_stroke(rect, 0.0, Stroke::new(1.0, Color32::from_rgb(0x28, 0x71, 0x8c)), StrokeKind::Inside);
                }
            }
        }
    }

    fn cell_at(&self, response: &egui::Response, origin: Pos2) -> Option<usize> {
        let pos = response.interact_pointer_pos()?;
        let c = ((pos.x - origin.x) / self.game.cell_size) as i32;
        let r = ((pos.y - origin.y) / self.game.cell_size) as i32;
        if r < 0 || c < 0 || r >= self.game.board.rows as i32 || c >= self.game.board.cols as i32 {
            return None;
        }
        Some(r as usize * self.game.board.cols + c as usize)
    }

    fn handle_input(&mut self, response: &egui::Response, origin: Pos2) {
        if self.game.start_time.is_none() && !self.game.board.game_over && !self.game.board.won {
            if response.clicked() || response.secondary_clicked() {
                self.game.start_time = Some(Instant::now());
            }
        }

        if response.secondary_clicked() {
            if let Some(idx) = self.cell_at(response, origin) {
                let before = self.game.board.flagged[idx];
                self.game.board.toggle_flag(idx);
                if self.game.board.flagged[idx] != before {
                    sound::play_flag();
                }
            }
        }

        if response.clicked() || response.double_clicked() || response.middle_clicked() {
            if let Some(idx) = self.cell_at(response, origin) {
                // 中键 = chord；双击已翻开的数字格 = chord；其余（含双击未翻开格）= 翻开
                let is_chord = response.middle_clicked()
                    || (response.double_clicked()
                        && self.game.board.revealed[idx]
                        && self.game.board.cells[idx] > 0);
                if is_chord {
                    let result = self.game.board.chord(idx);
                    self.apply_result(result);
                } else {
                    self.reveal_at(idx);
                }
            }
        }
    }

    fn reveal_at(&mut self, idx: usize) {
        let before = self.game.board.revealed_count();
        let result = self.game.board.reveal(idx);
        if self.game.board.revealed_count() > before {
            sound::play_reveal();
        }
        self.apply_result(result);
    }

    fn apply_result(&mut self, result: RevealResult) {
        match result {
            RevealResult::GameOver => {
                sound::play_explosion();
                self.game.wrong_flags = self.game.board.reveal_all_mines();
                if let Some(mine) = self.game.board.triggered_mine {
                    self.spawn_explosion(mine);
                }
                self.record_result(false);
            }
            RevealResult::Win => {
                sound::play_win();
                self.game.board.flagged = self.game.board.cells.iter().map(|&c| c == -1).collect();
                self.record_result(true);
            }
            RevealResult::Continue => {}
        }
    }

    fn spawn_explosion(&mut self, idx: usize) {
        let r = idx / self.game.board.cols;
        let c = idx % self.game.board.cols;
        let center = Vec2::new(
            c as f32 * self.game.cell_size + self.game.cell_size / 2.0,
            r as f32 * self.game.cell_size + self.game.cell_size / 2.0,
        );
        let now = Instant::now();
        for _ in 0..28 {
            let angle = rand::random::<f32>() * std::f32::consts::TAU;
            let speed = 40.0 + rand::random::<f32>() * 140.0;
            let vel = Vec2::new(angle.cos() * speed, angle.sin() * speed);
            self.game.particles.push(Particle {
                pos: center,
                vel,
                color: Color32::from_rgb(0xff, 0x6f, 0x91),
                born: now,
                life: 0.5 + rand::random::<f32>() * 0.5,
                size: 2.0 + rand::random::<f32>() * 3.5,
            });
        }
    }

    fn update_particles(&mut self, dt: f32) {
        for p in &mut self.game.particles {
            p.vel.y += 220.0 * dt;
            p.pos += p.vel * dt;
        }
        self.game.particles.retain(|p| p.born.elapsed().as_secs_f32() < p.life);
    }

    fn draw_particles(&self, painter: &egui::Painter, origin: Pos2) {
        for p in &self.game.particles {
            let t = p.born.elapsed().as_secs_f32() / p.life;
            let alpha = (1.0 - t).clamp(0.0, 1.0);
            let color = Color32::from_rgba_unmultiplied(
                p.color.r(),
                p.color.g(),
                p.color.b(),
                (alpha * 255.0) as u8,
            );
            painter.circle_filled(origin + p.pos, p.size, color);
        }
    }
}

/// 加载系统中文字体（黑体）。
fn install_fonts(ctx: &egui::Context) {
    let mut fonts = egui::FontDefinitions::default();
    // 优先微软雅黑（更精致），回退黑体
    for path in ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"] {
        if let Ok(bytes) = std::fs::read(path) {
            let name = if path.contains("msyh") { "msyh" } else { "simhei" };
            fonts
                .font_data
                .insert(name.to_owned(), std::sync::Arc::new(egui::FontData::from_owned(bytes)));
            for family in [egui::FontFamily::Proportional, egui::FontFamily::Monospace] {
                fonts
                    .families
                    .entry(family)
                    .or_default()
                    .insert(0, name.to_owned());
            }
            break;
        }
    }
    ctx.set_fonts(fonts);
}

/// 深色赛博主题：圆角、按钮三态、间距。
fn install_theme(ctx: &egui::Context) {
    let mut visuals = egui::Visuals::dark();
    visuals.panel_fill = BG;
    visuals.window_fill = SURFACE;
    visuals.extreme_bg_color = Color32::from_rgb(0x0e, 0x22, 0x38);
    visuals.faint_bg_color = SURFACE_ALT;
    visuals.override_text_color = Some(TEXT);
    visuals.window_corner_radius = 10.0.into();
    visuals.window_stroke = Stroke::new(1.0, BORDER);

    let radius = 6.0f32.into();
    visuals.widgets.noninteractive.bg_fill = SURFACE_ALT;
    visuals.widgets.noninteractive.fg_stroke = Stroke::new(1.0, MUTED);
    visuals.widgets.noninteractive.corner_radius = radius;

    visuals.widgets.inactive.weak_bg_fill = SURFACE_METAL;
    visuals.widgets.inactive.bg_fill = SURFACE_METAL;
    visuals.widgets.inactive.bg_stroke = Stroke::new(1.0, BORDER);
    visuals.widgets.inactive.fg_stroke = Stroke::new(1.0, TEXT);
    visuals.widgets.inactive.corner_radius = radius;

    visuals.widgets.hovered.weak_bg_fill = SURFACE_HOVER;
    visuals.widgets.hovered.bg_fill = SURFACE_HOVER;
    visuals.widgets.hovered.bg_stroke = Stroke::new(1.0, BORDER_HOT);
    visuals.widgets.hovered.fg_stroke = Stroke::new(1.5, TEXT);
    visuals.widgets.hovered.corner_radius = radius;

    visuals.widgets.active.weak_bg_fill = PRIMARY;
    visuals.widgets.active.bg_fill = PRIMARY;
    visuals.widgets.active.bg_stroke = Stroke::new(1.0, PRIMARY);
    visuals.widgets.active.fg_stroke = Stroke::new(1.0, PRIMARY_DARK);
    visuals.widgets.active.corner_radius = radius;

    visuals.selection.bg_fill = PRIMARY;
    visuals.selection.stroke = Stroke::new(1.0, BORDER_HOT);

    ctx.set_visuals(visuals);

    ctx.all_styles_mut(|style| {
        style.spacing.item_spacing = Vec2::new(10.0, 10.0);
        style.spacing.button_padding = Vec2::new(16.0, 8.0);
        style.spacing.interact_size = Vec2::new(48.0, 36.0);
    });
}

fn main() -> eframe::Result {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([640.0, 720.0])
            .with_title("扫雷"),
        ..Default::default()
    };
    eframe::run_native(
        "扫雷",
        options,
        Box::new(|cc| {
            install_fonts(&cc.egui_ctx);
            install_theme(&cc.egui_ctx);
            sound::init();
            Ok(Box::new(App::new()))
        }),
    )
}
