# الشرماني سوشيال V2 — تشغيل ونشر

## تشغيل Windows
1. ثبت Node.js 20+ وPython 3.11+.
2. فك الضغط في مجلد لا يحتوي مسافات معقدة، ثم انسخ `.env.example` إلى `.env`.
3. محليًا استخدم `DATA_DIR=./data`، واختر `JWT_SECRET` عشوائيًا طويلًا، ولا تشارك ملف `.env`.
4. نفذ `npm install` ثم `npm test` ثم `npm start`، وافتح `http://localhost:3000`.
5. لإنشاء حساب المدير المحلي نفذ `npm run admin:setup` وأدخل البريد `aa73826635@gmail.com` وكلمة مرور قوية.
6. لتشغيل برنامج سطح المكتب شغل `RUN_WINDOWS_GUI.bat`. ولتجميع EXE على Windows شغل `BUILD_WINDOWS_EXE.bat`.

## نشر Railway
1. أنشئ مستودع GitHub خاصًا وارفع ملفات المشروع دون `.env` أو مجلد `data`.
2. في Railway: New Project > Deploy from GitHub repo.
3. أضف Volume مربوطًا بـ `/app/data`، وأضف `DATA_DIR=/app/data` و`NODE_ENV=production` و`JWT_SECRET` سريًا طويلًا.
4. استخرج نطاقًا عامًا عبر Settings > Networking > Generate Domain، وتأكد من `https://.../health`.
5. إنشاء المدير في قاعدة بيانات Railway يجب أن يتم بأمر `npm run admin:setup` في بيئة خدمة Railway نفسها، وليس على حاسوبك. استخدم جلسة أو مهمة آمنة تتوفر لها متغيرات الخدمة والـVolume؛ لا تضف كلمة مرور المدير إلى GitHub.
6. افتح برنامج Windows، أدخل عنوان HTTPS وسجل دخول المدير.

## الميزات المضافة في V2 (واجهات API)
- `GET /api/v2/integrations` يبين وضع الربط الحقيقي لكل منصة.
- `GET /api/v2/analytics` إحصائيات النشر الداخلية للعميل، وليس مشاهدات المنصات الخارجية.
- `POST /api/v2/ai/caption` مع `{ "topic":"...", "tone":"..." }`، يتطلب `OPENAI_API_KEY`.
- `POST /api/v2/billing/requests` مع `{ "plan":"pro" }` لإنشاء طلب مراجعة، دون تحصيل مالي.
- `GET /api/v2/billing/requests` طلبات العميل.
- `GET /api/v2/admin/billing` طلبات جميع العملاء للمدير.
- `POST /api/v2/admin/billing/:id/review` مع `{ "status":"approved", "confirmedPayment":true, "reference":"..." }` بعد التحقق من الدفع يدويًا.
- `GET /api/v2/admin/audit` سجل عمليات إدارية.
- `GET /api/v2/security/session` معلومات الجلسة.
- `GET /api/v2/oauth/:provider/start` يرد 501 بوضوح إلى أن يكتمل OAuth الرسمي.

## ما لم يكتمل
- TikTok/Instagram/Facebook/YouTube/X/LinkedIn/Pinterest/Threads: يحتاج كل منها موافقات وصلاحيات تطبيق مطور، Client ID/Secret، إعادة توجيه OAuth، وتخزين رموز مشفر وآلية تحديثها. لا تضع كلمات مرور العملاء في الموقع.
- الدفع: بوابة مثل Stripe أو مزود سعودي مرخص تتطلب حساب تاجر ومفاتيح وتوقيع Webhook والتحقق من عمليات الدفع. الموافقة اليدوية ليست بوابة دفع.
- AI: مفتاح OpenAI API مدفوع منفصل عن اشتراك ChatGPT. الخدمة تعيد 503 إذا لم يوجد مفتاح.
- قبل الإطلاق العام: يلزم مراجعة أمنية شاملة، صلاحيات دقيقة، نسخ احتياطية، سياسات خصوصية، إدارة ملفات وسائط كبيرة، حدود استخدام AI، وإضافة اختبارات تكامل كاملة.

## الاختبارات
`npm test` لتشغيل اختبارات البنية الأساسية وV2. اختبارات النشر الفعلي تتطلب حسابات اختبار ومفاتيح حقيقية ولا تعمل تلقائيًا.
