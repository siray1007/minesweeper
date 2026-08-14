//! 数据持久化：账号、战绩、排行榜，存 JSON 文件。

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::path::PathBuf;

#[derive(Serialize, Deserialize, Clone)]
pub struct User {
    pub username: String,
    pub password_hash: String,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct Record {
    pub username: String,
    pub difficulty: String,
    pub time_seconds: u32,
    pub won: bool,
    pub completed_at: u64,
}

#[derive(Serialize, Deserialize, Default)]
pub struct Store {
    pub users: Vec<User>,
    pub records: Vec<Record>,
}

fn data_dir() -> PathBuf {
    let base = std::env::var("LOCALAPPDATA")
        .or_else(|_| std::env::var("APPDATA"))
        .unwrap_or_else(|_| ".".to_string());
    PathBuf::from(base).join("MinesweeperRust")
}

fn store_path() -> PathBuf {
    data_dir().join("store.json")
}

pub fn hash_password(password: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(password.as_bytes());
    hasher.finalize().iter().map(|b| format!("{:02x}", b)).collect()
}

pub fn load() -> Store {
    std::fs::read_to_string(store_path())
        .ok()
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or_default()
}

pub fn save(store: &Store) {
    if let Some(dir) = store_path().parent() {
        let _ = std::fs::create_dir_all(dir);
    }
    if let Ok(json) = serde_json::to_string_pretty(store) {
        let _ = std::fs::write(store_path(), json);
    }
}

pub fn register(username: &str, password: &str) -> Result<(), String> {
    let username = username.trim();
    let mut store = load();
    if username.chars().count() < 2 {
        return Err("用户名至少 2 个字符".to_string());
    }
    if password.len() < 4 {
        return Err("密码至少 4 个字符".to_string());
    }
    if store.users.iter().any(|u| u.username == username) {
        return Err("用户名已存在".to_string());
    }
    store.users.push(User {
        username: username.to_string(),
        password_hash: hash_password(password),
    });
    save(&store);
    Ok(())
}

pub fn login(username: &str, password: &str) -> Result<(), String> {
    let store = load();
    let hash = hash_password(password);
    if let Some(user) = store.users.iter().find(|u| u.username == username) {
        if user.password_hash == hash {
            return Ok(());
        }
        return Err("密码不正确".to_string());
    }
    Err("账号不存在".to_string())
}

pub fn add_record(username: &str, difficulty: &str, time_seconds: u32, won: bool) {
    let mut store = load();
    let completed_at = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0);
    store.records.push(Record {
        username: username.to_string(),
        difficulty: difficulty.to_string(),
        time_seconds,
        won,
        completed_at,
    });
    save(&store);
}

/// 返回指定难度的排行榜（按用时升序，取前 n 名）。
pub fn leaderboard(difficulty: &str, limit: usize) -> Vec<Record> {
    let store = load();
    let mut records: Vec<Record> = store
        .records
        .into_iter()
        .filter(|r| r.difficulty == difficulty && r.won)
        .collect();
    records.sort_by_key(|r| r.time_seconds);
    records.truncate(limit);
    records
}

/// 返回某用户在某难度的最佳用时。
pub fn best_time(username: &str, difficulty: &str) -> Option<u32> {
    let store = load();
    store
        .records
        .into_iter()
        .filter(|r| r.username == username && r.difficulty == difficulty && r.won)
        .map(|r| r.time_seconds)
        .min()
}
