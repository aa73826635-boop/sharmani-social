import crypto from 'node:crypto';
import {db} from './db.js';
export const providers=['telegram','instagram','facebook','youtube','tiktok','x','linkedin','pinterest','threads'];
export const integrationStatus=()=>providers.map(provider=>({provider,mode:provider==='telegram'?'bot_api':'oauth_required',configured:provider==='telegram'?Boolean(process.env.TELEGRAM_BOT_TOKEN):false,automaticPublishing:provider==='telegram'&&Boolean(process.env.TELEGRAM_BOT_TOKEN)}));
db.exec(`CREATE TABLE IF NOT EXISTS billing_requests(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id),plan TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending',reference TEXT,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,reviewed_at TEXT);
CREATE TABLE IF NOT EXISTS audit_events(id INTEGER PRIMARY KEY,actor_id INTEGER,action TEXT NOT NULL,detail TEXT,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_billing_user ON billing_requests(user_id);`);
export function audit(actor,action,detail={}){db.prepare('INSERT INTO audit_events(actor_id,action,detail) VALUES(?,?,?)').run(actor,action,JSON.stringify(detail).slice(0,1500))}
export function attachV2(app,auth,adminOnly,plans){
 app.get('/api/v2/integrations',auth,(req,res)=>res.json(integrationStatus()));
 app.get('/api/v2/analytics',auth,(req,res)=>{
  const user=req.user.id;
  const summary=db.prepare(`SELECT COUNT(DISTINCT p.id) posts,COUNT(d.id) deliveries,SUM(CASE WHEN d.status='published' THEN 1 ELSE 0 END) published,SUM(CASE WHEN d.status='failed' THEN 1 ELSE 0 END) failed FROM posts p LEFT JOIN deliveries d ON d.post_id=p.id WHERE p.user_id=?`).get(user);
  const providers=db.prepare(`SELECT a.provider,COUNT(d.id) total,SUM(CASE WHEN d.status='published' THEN 1 ELSE 0 END) published,SUM(CASE WHEN d.status='failed' THEN 1 ELSE 0 END) failed FROM accounts a LEFT JOIN deliveries d ON d.account_id=a.id WHERE a.user_id=? GROUP BY a.provider`).all(user);
  res.json({summary,providers,note:'إحصاءات التسليم داخل المنصة فقط؛ المشاهدات والتفاعل تحتاج صلاحيات تحليلات رسمية'});
 });
 app.post('/api/v2/ai/caption',auth,async(req,res,next)=>{try{
  const topic=String(req.body?.topic||'').trim(),tone=String(req.body?.tone||'حماسي').slice(0,30);
  if(topic.length<3||topic.length>500)return res.status(400).json({error:'الموضوع مطلوب (3–500 حرف)'});
  if(!process.env.OPENAI_API_KEY)return res.status(503).json({error:'خدمة الذكاء الاصطناعي غير مفعلة؛ اضبط OPENAI_API_KEY على الخادم'});
  const response=await fetch('https://api.openai.com/v1/responses',{method:'POST',headers:{'Authorization':`Bearer ${process.env.OPENAI_API_KEY}`,'Content-Type':'application/json'},body:JSON.stringify({model:process.env.OPENAI_MODEL||'gpt-4.1-mini',input:`اكتب وصفًا عربيًا لمنشور شبكات اجتماعية عن: ${topic}. الأسلوب: ${tone}. أضف 4 وسوم مناسبة. لا تخترع حقائق عن المنتج. أجب بالنص فقط.`,max_output_tokens:350}),signal:AbortSignal.timeout(25000)});
  const payload=await response.json();if(!response.ok)return res.status(502).json({error:'فشل مزود الذكاء الاصطناعي',detail:payload.error?.message||'API error'});
  const caption=(payload.output||[]).flatMap(x=>x.content||[]).filter(x=>x.type==='output_text').map(x=>x.text).join('\n');
  audit(req.user.id,'ai.caption',{topic:topic.slice(0,80)});res.json({caption,model:process.env.OPENAI_MODEL||'gpt-4.1-mini'});
 }catch(e){next(e)}});
 app.post('/api/v2/billing/requests',auth,(req,res)=>{const plan=String(req.body?.plan||'');if(!plans[plan]||plan==='free')return res.status(400).json({error:'خطة غير صالحة'});const r=db.prepare('INSERT INTO billing_requests(user_id,plan) VALUES(?,?)').run(req.user.id,plan);audit(req.user.id,'billing.request',{plan});res.status(201).json({id:Number(r.lastInsertRowid),status:'pending',message:'طلب فقط، لا يوجد دفع أو تفعيل تلقائي'})});
 app.get('/api/v2/billing/requests',auth,(req,res)=>res.json(db.prepare('SELECT id,plan,status,reference,created_at FROM billing_requests WHERE user_id=? ORDER BY id DESC').all(req.user.id)));
 app.get('/api/v2/admin/billing',auth,adminOnly,(req,res)=>res.json(db.prepare('SELECT b.*,u.email FROM billing_requests b JOIN users u ON u.id=b.user_id ORDER BY b.id DESC LIMIT 200').all()));
 app.post('/api/v2/admin/billing/:id/review',auth,adminOnly,(req,res)=>{const status=String(req.body?.status||'');if(!['rejected','approved'].includes(status))return res.status(400).json({error:'حالة غير صالحة'});const r=db.prepare('SELECT * FROM billing_requests WHERE id=?').get(req.params.id);if(!r||r.status!=='pending')return res.status(404).json({error:'الطلب غير موجود أو تمت مراجعته'});if(status==='approved'&&req.body?.confirmedPayment!==true)return res.status(400).json({error:'يجب تأكيد التحقق اليدوي من الدفع خارج النظام قبل التفعيل'});db.transaction(()=>{db.prepare('UPDATE billing_requests SET status=?,reference=?,reviewed_at=CURRENT_TIMESTAMP WHERE id=?').run(status,String(req.body?.reference||'').slice(0,120),r.id);if(status==='approved')db.prepare("UPDATE subscriptions SET plan=?,status='active' WHERE user_id=?").run(r.plan,r.user_id)})();audit(req.user.id,'billing.review',{requestId:r.id,status});res.json({ok:true,status})});
 app.get('/api/v2/admin/audit',auth,adminOnly,(req,res)=>res.json(db.prepare('SELECT id,actor_id,action,detail,created_at FROM audit_events ORDER BY id DESC LIMIT 200').all()));
 app.get('/api/v2/security/session',auth,(req,res)=>res.json({userId:req.user.id,role:req.user.role,transport:'bearer',note:'فعّل HTTPS، ولا تشارك رمز الدخول'}));
 app.get('/api/v2/oauth/:provider/start',auth,(req,res)=>res.status(501).json({error:'OAuth غير مفعّل لهذه المنصة بعد؛ يحتاج Client ID/Secret والموافقة على الصلاحيات وربط callback والتحقق من state',provider:req.params.provider}));
}
