mod game;
mod solver;
mod sound;
mod storage;

use std::collections::{HashMap, HashSet};
use std::time::{Duration, Instant};

use eframe::egui::{self, Align2, Color32, FontId, Pos2, Rect, Sense, Stroke, StrokeKind, Vec2};

use game::{Board, RevealResult};

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
    reveal_anims: HashMap<usize, Instant>,
    prev_revealed: Vec<bool>,
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
            reveal_anims: HashMap::new(),
            prev_revealed: vec![false; rows * cols],
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
            ui.add_space(40.0);
            ui.heading("扫雷");
            ui.add_space(24.0);

            let is_register = self.auth.mode == AuthMode::Register;
            egui::Frame::group(ui.style()).show(ui, |ui| {
                ui.set_width(320.0);
                ui.add_space(8.0);
                ui.add(egui::TextEdit::singleline(&mut self.auth.username).hint_text("用户名"));
                ui.add_space(6.0);
                ui.add(egui::TextEdit::singleline(&mut self.auth.password).password(true).hint_text("密码"));
                if is_register {
                    ui.add_space(6.0);
                    ui.add(egui::TextEdit::singleline(&mut self.auth.confirm).password(true).hint_text("确认密码"));
                }
                ui.add_space(10.0);

                if is_register {
                    if ui.button("注册").clicked() {
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
                    }
                } else {
                    if ui.button("登录").clicked() {
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
                    ui.add_space(6.0);
                    ui.colored_label(Color32::from_rgb(0xff, 0x6b, 0x81), &self.auth.message);
                }

                ui.add_space(8.0);
                let toggle_text = if is_register { "已有账号？去登录" } else { "没有账号？去注册" };
                if ui.button(toggle_text).clicked() {
                    self.auth.mode = if is_register { AuthMode::Login } else { AuthMode::Register };
                    self.auth.message.clear();
                }
                ui.add_space(8.0);
            });
        });
    }

    fn lobby_screen(&mut self, ui: &mut egui::Ui) {
        ui.vertical_centered(|ui| {
            ui.add_space(24.0);
            ui.heading("作战大厅");
            if let Some(user) = &self.current_user {
                ui.label(format!("当前玩家：{}", user));
            }
            ui.add_space(20.0);

            for d in [Difficulty::Easy, Difficulty::Medium, Difficulty::Hard] {
                let (rows, cols, mines, _) = d.config();
                let best = self.current_user.as_ref().and_then(|u| storage::best_time(u, d.key()));
                let btn_text = match best {
                    Some(t) => format!("{}  ·  {}×{} ·  {} 雷  ·  最佳 {}", d.label(), rows, cols, mines, format_time(t)),
                    None => format!("{}  ·  {}×{} ·  {} 雷", d.label(), rows, cols, mines),
                };
                if ui.add_sized([280.0, 40.0], egui::Button::new(btn_text)).clicked() {
                    self.start_game(d);
                }
                ui.add_space(8.0);
            }

            ui.add_space(16.0);
            if ui.add_sized([280.0, 36.0], egui::Button::new("🏆 排行榜")).clicked() {
                self.screen = Screen::Leaderboard;
            }
            ui.add_space(8.0);
            if ui.add_sized([280.0, 36.0], egui::Button::new("退出登录")).clicked() {
                self.current_user = None;
                self.screen = Screen::Auth;
            }
        });
    }

    fn leaderboard_screen(&mut self, ui: &mut egui::Ui) {
        ui.vertical_centered(|ui| {
            ui.add_space(16.0);
            ui.heading("排行榜");
            ui.add_space(12.0);

            for d in [Difficulty::Easy, Difficulty::Medium, Difficulty::Hard] {
                ui.label(d.label());
                let records = storage::leaderboard(d.key(), 10);
                if records.is_empty() {
                    ui.label("暂无记录");
                } else {
                    egui::Grid::new(format!("grid_{}", d.key()))
                        .num_columns(3)
                        .striped(true)
                        .show(ui, |ui| {
                            ui.label("名次");
                            ui.label("玩家");
                            ui.label("用时");
                            ui.end_row();
                            for (i, r) in records.iter().enumerate() {
                                ui.label(format!("{}", i + 1));
                                ui.label(&r.username);
                                ui.label(format_time(r.time_seconds));
                                ui.end_row();
                            }
                        });
                }
                ui.add_space(12.0);
            }

            ui.add_space(8.0);
            if ui.button("返回大厅").clicked() {
                self.screen = Screen::Lobby;
            }
        });
    }

    fn game_screen(&mut self, ui: &mut egui::Ui, ctx: &egui::Context, dt: f32) {
        // 计时更新
        if let Some(start) = self.game.start_time {
            if !self.game.board.game_over && !self.game.board.won {
                self.game.elapsed = start.elapsed();
                ctx.request_repaint_after(Duration::from_millis(200));
            }
        }

        // 粒子 + reveal 动画持续重绘
        if !self.game.particles.is_empty() {
            self.update_particles(dt);
            ctx.request_repaint();
        }
        let now = Instant::now();
        if self.game.reveal_anims.values().any(|&t| now.duration_since(t).as_secs_f32() < 0.25) {
            ctx.request_repaint();
        }

        // HUD
        ui.horizontal(|ui| {
            if ui.button("← 大厅").clicked() {
                self.screen = Screen::Lobby;
            }
            ui.separator();
            let remaining = self.game.board.remaining_mines();
            ui.label(format!("💣 {}", remaining.max(0)));
            ui.separator();
            let secs = self.game.elapsed.as_secs();
            ui.label(format!("⏱ {:02}:{:02}", secs / 60, secs % 60));
            ui.separator();
            if ui.button("重新开始").clicked() {
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
            self.draw_board(&painter, origin);
            self.draw_particles(&painter, origin);
            self.handle_input(&response, origin);
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
                    ui.colored_label(color, text);
                    ui.add_space(8.0);
                    if ui.button("再来一局").clicked() {
                        let d = self.game.difficulty;
                        self.game = GameState::new(d);
                    }
                    if ui.button("返回大厅").clicked() {
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

    fn draw_board(&self, painter: &egui::Painter, origin: Pos2) {
        let cs = self.game.cell_size;
        let closed = Color32::from_rgb(0x2a, 0x4a, 0x63);
        let closed_alt = Color32::from_rgb(0x24, 0x40, 0x57);
        let open = Color32::from_rgb(0xd7, 0xe6, 0xec);
        let open_alt = Color32::from_rgb(0xcf, 0xde, 0xe5);
        let reveal_flash = Color32::from_rgb(0xff, 0xf6, 0xd6);
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
                    let (bg, font_scale) = if let Some(&t) = self.game.reveal_anims.get(&idx) {
                        let age = t.elapsed().as_secs_f32();
                        if age < 0.25 {
                            let p = age / 0.25;
                            let base = if (r + c) % 2 == 0 { open } else { open_alt };
                            (Self::lerp_color(reveal_flash, base, p), 1.0 + (1.0 - p) * 0.35)
                        } else {
                            let base = if (r + c) % 2 == 0 { open } else { open_alt };
                            (base, 1.0)
                        }
                    } else {
                        let base = if (r + c) % 2 == 0 { open } else { open_alt };
                        (base, 1.0)
                    };
                    painter.rect_filled(rect, 0.0, bg);
                    let value = self.game.board.cells[idx];
                    if value == -1 {
                        painter.rect_filled(rect.shrink(2.0), 2.0, mine_bg);
                    } else if value > 0 {
                        painter.text(
                            rect.center(),
                            Align2::CENTER_CENTER,
                            value.to_string(),
                            FontId::proportional(cs * 0.55 * font_scale),
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
                    let bg = if (r + c) % 2 == 0 { closed } else { closed_alt };
                    painter.rect_filled(rect, 0.0, bg);
                    painter.rect_stroke(rect, 0.0, Stroke::new(1.0, Color32::from_rgb(0x5c, 0x7f, 0x96)), StrokeKind::Inside);
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

        if response.middle_clicked() || response.double_clicked() {
            if let Some(idx) = self.cell_at(response, origin) {
                let result = self.chord_with_anim(idx);
                self.apply_result(result);
            }
        }

        if response.clicked() {
            if let Some(idx) = self.cell_at(response, origin) {
                let before = self.game.board.revealed_count();
                let result = self.reveal_with_anim(idx);
                if self.game.board.revealed_count() > before {
                    sound::play_reveal();
                }
                self.apply_result(result);
            }
        }
    }

    fn reveal_with_anim(&mut self, idx: usize) -> RevealResult {
        self.game.prev_revealed = self.game.board.revealed.clone();
        let result = self.game.board.reveal(idx);
        self.record_new_reveals();
        result
    }

    fn chord_with_anim(&mut self, idx: usize) -> RevealResult {
        self.game.prev_revealed = self.game.board.revealed.clone();
        let result = self.game.board.chord(idx);
        self.record_new_reveals();
        result
    }

    fn record_new_reveals(&mut self) {
        let now = Instant::now();
        for i in 0..self.game.board.len() {
            if self.game.board.revealed[i] && !self.game.prev_revealed[i] {
                self.game.reveal_anims.insert(i, now);
            }
        }
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
    if let Ok(bytes) = std::fs::read("C:/Windows/Fonts/simhei.ttf") {
        fonts
            .font_data
            .insert("simhei".to_owned(), std::sync::Arc::new(egui::FontData::from_owned(bytes)));
        for family in [egui::FontFamily::Proportional, egui::FontFamily::Monospace] {
            fonts
                .families
                .entry(family)
                .or_default()
                .insert(0, "simhei".to_owned());
        }
    }
    ctx.set_fonts(fonts);
}

/// 深色赛博主题。
fn install_theme(ctx: &egui::Context) {
    let mut visuals = egui::Visuals::dark();
    visuals.panel_fill = Color32::from_rgb(0x10, 0x2a, 0x43);
    visuals.window_fill = Color32::from_rgb(0x17, 0x3b, 0x57);
    visuals.extreme_bg_color = Color32::from_rgb(0x0e, 0x22, 0x38);
    visuals.selection.bg_fill = Color32::from_rgb(0x55, 0xd8, 0xee);
    visuals.selection.stroke.color = Color32::from_rgb(0x55, 0xd8, 0xee);
    ctx.set_visuals(visuals);
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
            Ok(Box::new(App::new()))
        }),
    )
}
