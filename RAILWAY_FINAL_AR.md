# نشر الشرماني سوشيال على Railway من Windows

## 1. ما تم تجهيزه
- Dockerfile لتثبيت اعتماديات Node الأصلية مثل better-sqlite3.
- railway.json مع فحص /health وإعادة التشغيل عند الفشل.
- DEPLOY_RAILWAY_WINDOWS.bat لتسجيل الدخول والربط وإرسال المشروع إلى Railway CLI.
- قاعدة SQLite وملفات الوسائط تحت DATA_DIR. يلزم Volume دائم قبل استخدام الموقع.

## 2. قبل النشر
1. ثبّت Node.js وRailway CLI بالأمر `npm install -g @railway/cli`.
2. افتح https://railway.com/new وأنشئ مشروعًا وخدمة Empty Service (أو اربط GitHub).
3. أضف Volume إلى الخدمة واجعل Mount Path = `/app/data`.
4. أضف Variables في Railway: `NODE_ENV=production` و`DATA_DIR=/app/data` و`JWT_SECRET` (قيمة عشوائية سرية لا تقل عن 32 حرفًا) و`ADMIN_EMAIL=aa73826635@gmail.com`.
5. شغّل `DEPLOY_RAILWAY_WINDOWS.bat` من مجلد المشروع، واختر المشروع والخدمة الصحيحة.
6. في Networking أنشئ Public Domain، ثم افتح `https://YOUR_DOMAIN/health` للتحقق.

## 3. تهيئة المدير على قاعدة بيانات Railway
بعد النشر، من Variables أضف مؤقتًا `ADMIN_INITIAL_PASSWORD` بكلمة مرور قوية وفريدة من 12 حرفًا على الأقل. من جهازك نفّذ:
`railway ssh -- npm run admin:setup`
يجب أن تكون الخدمة المرتبطة هي خدمة الموقع نفسها. بعد نجاح العملية احذف `ADMIN_INITIAL_PASSWORD` من Variables فورًا، وأعد نشر الخدمة إن لزم. لا تستخدم `railway run npm run admin:setup` لإنشاء المدير البعيد؛ فقد يعمل محليًا على قاعدة مختلفة.

## 4. تشغيل Windows
شغّل `RUN_WINDOWS_GUI.bat` للتحكم عبر واجهة البرنامج؛ ضع رابط Railway في إعدادات الاتصال. لتجميع البرنامج إلى EXE على Windows استخدم `BUILD_WINDOWS_EXE.bat`.

## 5. تكاملات لا تعمل دون حسابات مطور ومفاتيح
- Telegram: ضع `TELEGRAM_BOT_TOKEN` وأضف البوت مسؤولًا إلى القناة؛ اختبر الإرسال قبل فتح الخدمة للعملاء.
- Meta Instagram/Facebook، TikTok، YouTube، X، LinkedIn، Pinterest، Threads: تحتاج OAuth وتطبيقات مطورين وصلاحيات أو موافقات مناسبة. النسخة الحالية لا تنشر فعليًا إليها.
- الذكاء الاصطناعي: يتطلب `OPENAI_API_KEY` وفوترة API مستقلة.
- المدفوعات: طلبات الاشتراك والمراجعة اليدوية فقط؛ لم يتم ربط بوابة تحصيل حقيقية.

## 6. متطلبات الأمان قبل فتح التسجيل العام
استخدم نطاق HTTPS، احتفظ بنسخ احتياطية مشفرة لملف SQLite ومجلد uploads، لا ترفع `.env`، راجع حدود التخزين والتكاليف، واختبر الصلاحيات وحماية الحسابات والملفات. لا تعد العملاء بنشر مضمون في منصات غير مفعلة. Railway Volume ليس نسخة احتياطية تلقائية.
