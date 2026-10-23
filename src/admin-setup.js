import 'dotenv/config';
import bcrypt from 'bcryptjs';
import {db} from './db.js';
const email=(process.env.ADMIN_EMAIL||'aa73826635@gmail.com').trim().toLowerCase();
const password=process.env.ADMIN_INITIAL_PASSWORD;
if(!password||password.length<12){console.error('ADMIN_INITIAL_PASSWORD must contain at least 12 characters. Set it temporarily, run npm run admin:setup, then remove it.');process.exit(1)}
const existing=db.prepare('SELECT id,role FROM users WHERE email=?').get(email);
if(existing && existing.role!=='admin'){console.error('A customer already owns this email. Admin setup stopped; review the database manually.');process.exit(1)}
const hash=await bcrypt.hash(password,12);
if(existing){db.prepare('UPDATE users SET password_hash=? WHERE id=?').run(hash,existing.id);console.log('Admin password updated for '+email)}
else {const r=db.prepare("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,'admin')").run('مدير الشرماني سوشيال',email,hash);db.prepare("INSERT INTO subscriptions(user_id,plan,status) VALUES(?,'agency','active')").run(r.lastInsertRowid);console.log('Admin account created: '+email)}
