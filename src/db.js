import Database from 'better-sqlite3';
import fs from 'node:fs';
import path from 'node:path';
const dataDir=path.resolve(process.env.DATA_DIR||'./data');
fs.mkdirSync(dataDir,{recursive:true});
export const db=new Database(path.join(dataDir,'sharmani.db'));
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');
db.exec(`
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'customer', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS subscriptions(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL UNIQUE REFERENCES users(id), plan TEXT NOT NULL DEFAULT 'free', status TEXT NOT NULL DEFAULT 'trial', renews_at TEXT);
CREATE TABLE IF NOT EXISTS accounts(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), provider TEXT NOT NULL, label TEXT NOT NULL, credential TEXT, external_id TEXT, status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS media(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), filename TEXT NOT NULL, original_name TEXT NOT NULL, mime TEXT NOT NULL, size INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), text TEXT NOT NULL DEFAULT '', media_id INTEGER REFERENCES media(id), scheduled_at TEXT, status TEXT NOT NULL DEFAULT 'draft', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS deliveries(id INTEGER PRIMARY KEY, post_id INTEGER NOT NULL REFERENCES posts(id), account_id INTEGER NOT NULL REFERENCES accounts(id), status TEXT NOT NULL DEFAULT 'queued', attempts INTEGER NOT NULL DEFAULT 0, external_id TEXT, error TEXT, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(post_id,account_id));
CREATE INDEX IF NOT EXISTS idx_posts_schedule ON posts(status,scheduled_at);
CREATE INDEX IF NOT EXISTS idx_deliveries_status ON deliveries(status);
`);
