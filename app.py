"""Sharmani Social Windows control panel. Python 3.11+, PySide6."""
import json
import os
import secrets
import subprocess
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QFileDialog,
    QDateTimeEdit, QCheckBox, QGroupBox, QHeaderView)
from PySide6.QtCore import QDateTime

def project_root():
    candidates = [Path.cwd(), Path(sys.executable).resolve().parent, Path(__file__).resolve().parent.parent]
    for candidate in candidates:
        for folder in [candidate, *candidate.parents]:
            if (folder/'package.json').exists() and (folder/'src'/'server.js').exists():
                return folder
    return Path(__file__).resolve().parent.parent

ROOT = project_root()
ADMIN_EMAIL = 'aa73826635@gmail.com'

class Signals(QObject):
    done = Signal(str, object, str)

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('الشرماني سوشيال | إدارة Windows')
        self.resize(1050, 730)
        self.signals = Signals()
        self.signals.done.connect(self.on_done)
        self.token = ''
        self.local_process = None
        self.media_id = None
        self.accounts = []
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.build_connection()
        self.build_dashboard()
        self.build_users()
        self.build_posts()
        self.build_local()
        self.build_v2()
        self.statusBar().showMessage('غير متصل. اختر عنوان Railway أو الخادم المحلي ثم سجل الدخول.')
        self.setStyleSheet('QWidget {font-size: 13px;} QPushButton {padding: 7px;} QLineEdit {padding: 5px;}')

    def build_v2(self):
        w=QWidget();v=QVBoxLayout(w)
        self.v2_output=QTextEdit();self.v2_output.setReadOnly(True)
        for title,endpoint in [('التحليلات','/api/v2/analytics'),('حالة ربط المنصات','/api/v2/integrations'),('طلبات الدفع','/api/v2/admin/billing'),('سجل الإدارة','/api/v2/admin/audit')]:
            b=QPushButton(title)
            b.clicked.connect(lambda checked=False,ep=endpoint:self.request('v2', 'GET',ep))
            v.addWidget(b)
        v.addWidget(self.v2_output)
        self.tabs.addTab(w,'الإصدار الثاني')

    def build_connection(self):
        w=QWidget(); v=QVBoxLayout(w)
        form=QFormLayout()
        self.url=QLineEdit('http://127.0.0.1:3000'); self.url.setPlaceholderText('https://your-app.up.railway.app')
        self.email=QLineEdit(ADMIN_EMAIL)
        self.password=QLineEdit(); self.password.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow('رابط الخادم:', self.url); form.addRow('بريد المدير:',self.email); form.addRow('كلمة المرور:',self.password)
        v.addLayout(form)
        r=QHBoxLayout(); self.login_btn=QPushButton('تسجيل الدخول'); self.login_btn.clicked.connect(self.login)
        health=QPushButton('فحص اتصال الخادم'); health.clicked.connect(lambda:self.request('health','GET','/health',auth=False))
        r.addWidget(self.login_btn);r.addWidget(health);v.addLayout(r)
        self.connection_info=QLabel('الاتصال يتم عبر HTTPS عند استخدام Railway. لا تحفظ كلمة المرور في ملفات البرنامج.')
        self.connection_info.setWordWrap(True);v.addWidget(self.connection_info);v.addStretch()
        self.tabs.addTab(w,'الاتصال')

    def build_dashboard(self):
        w=QWidget();v=QVBoxLayout(w)
        b=QPushButton('تحديث إحصائيات المنصة');b.clicked.connect(lambda:self.request('overview','GET','/api/admin/overview'))
        self.overview=QTextEdit();self.overview.setReadOnly(True)
        v.addWidget(b);v.addWidget(self.overview);self.tabs.addTab(w,'لوحة المدير')

    def build_users(self):
        w=QWidget();v=QVBoxLayout(w)
        b=QPushButton('تحميل قائمة العملاء');b.clicked.connect(lambda:self.request('users','GET','/api/admin/users'))
        self.users=QTableWidget(0,7);self.users.setHorizontalHeaderLabels(['ID','الاسم','البريد','الدور','الخطة','الحالة','تاريخ الإنشاء'])
        self.users.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        v.addWidget(b);v.addWidget(self.users);self.tabs.addTab(w,'العملاء')

    def build_posts(self):
        w=QWidget();v=QVBoxLayout(w)
        self.post_text=QTextEdit();self.post_text.setPlaceholderText('اكتب نص المنشور هنا...')
        self.media_label=QLabel('لا يوجد ملف مرفوع')
        up=QPushButton('رفع صورة / فيديو');up.clicked.connect(self.upload_media)
        refresh=QPushButton('تحديث حساباتي');refresh.clicked.connect(lambda:self.request('accounts','GET','/api/accounts'))
        self.targets=QComboBox();self.targets.setMinimumWidth(300)
        self.publish_now=QCheckBox('نشر الآن (يدخل قائمة انتظار الخادم)');self.publish_now.setChecked(True)
        self.scheduled=QDateTimeEdit(QDateTime.currentDateTime().addSecs(3600));self.scheduled.setCalendarPopup(True)
        publish=QPushButton('إرسال مهمة النشر');publish.clicked.connect(self.create_post)
        recent=QPushButton('عرض منشوراتي');recent.clicked.connect(lambda:self.request('posts','GET','/api/posts'))
        self.posts=QTextEdit();self.posts.setReadOnly(True)
        v.addWidget(QLabel('نص المنشور'));v.addWidget(self.post_text)
        r=QHBoxLayout();r.addWidget(up);r.addWidget(self.media_label);v.addLayout(r)
        r=QHBoxLayout();r.addWidget(refresh);r.addWidget(self.targets);v.addLayout(r)
        v.addWidget(self.publish_now);v.addWidget(self.scheduled);v.addWidget(publish);v.addWidget(recent);v.addWidget(self.posts)
        v.addWidget(QLabel('النشر الفعلي مدعوم حاليًا لقنوات Telegram المهيأة؛ بقية المنصات تحتاج تكامل OAuth/API.'))
        self.tabs.addTab(w,'المنشورات')

    def build_local(self):
        w=QWidget();v=QVBoxLayout(w)
        v.addWidget(QLabel('لتشغيل الخادم محليًا، يلزم Node.js وتثبيت حزم npm أولًا.'))
        self.secret=QLineEdit();self.secret.setPlaceholderText('JWT_SECRET محلي، اتركه فارغًا لتوليده')
        self.secret.setEchoMode(QLineEdit.EchoMode.Password)
        v.addWidget(self.secret)
        start=QPushButton('تشغيل الخادم المحلي');start.clicked.connect(self.start_local)
        stop=QPushButton('إيقاف الخادم المحلي');stop.clicked.connect(self.stop_local)
        admin=QPushButton('إنشاء / تحديث مدير قاعدة البيانات المحلية');admin.clicked.connect(self.setup_local_admin)
        v.addWidget(start);v.addWidget(stop);v.addWidget(admin)
        self.local_log=QTextEdit();self.local_log.setReadOnly(True);v.addWidget(self.local_log)
        v.addWidget(QLabel('إعداد المدير المحلي لا يغير حساب المدير على Railway. لا تضع بيانات Railway السرية هنا.'))
        self.tabs.addTab(w,'الخادم المحلي')

    def endpoint(self, path):
        base=self.url.text().strip().rstrip('/')
        parsed=urllib.parse.urlsplit(base)
        if parsed.scheme not in ('http','https') or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError('أدخل رابط خادم صحيحًا http(s)')
        if parsed.scheme=='http' and parsed.hostname not in ('localhost','127.0.0.1','::1'):
            raise ValueError('يجب استخدام HTTPS للخوادم البعيدة')
        return base+path

    def request(self, kind, method, path, data=None, auth=True, media=None):
        try:
            url=self.endpoint(path)
        except ValueError as e:
            QMessageBox.warning(self,'خطأ',str(e));return
        token=self.token
        if auth and not token:
            QMessageBox.warning(self,'تسجيل الدخول','سجل الدخول أولًا.');return
        def job():
            try:
                headers={'Accept':'application/json'}
                if auth: headers['Authorization']='Bearer '+token
                if media is not None:
                    boundary='----Sharmani'+secrets.token_hex(12)
                    filename, payload, mimetype=media
                    safe_name=filename.replace('"','_').replace('\r','').replace('\n','')
                    body=(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{safe_name}"\r\nContent-Type: {mimetype}\r\n\r\n').encode()+payload+(f'\r\n--{boundary}--\r\n').encode()
                    headers['Content-Type']='multipart/form-data; boundary='+boundary
                elif data is not None:
                    body=json.dumps(data).encode('utf-8');headers['Content-Type']='application/json'
                else: body=None
                req=urllib.request.Request(url,data=body,headers=headers,method=method)
                with urllib.request.urlopen(req,timeout=65 if media else 15) as resp:
                    result=json.loads(resp.read().decode('utf-8'))
                self.signals.done.emit(kind,result,'')
            except urllib.error.HTTPError as e:
                try: msg=json.loads(e.read().decode()).get('error',str(e))
                except Exception: msg=str(e)
                self.signals.done.emit(kind,None,f'HTTP {e.code}: {msg}')
            except Exception as e:self.signals.done.emit(kind,None,str(e))
        threading.Thread(target=job,daemon=True).start()

    def login(self):
        self.token=''
        self.request('login','POST','/api/auth/login',{'email':self.email.text().strip(),'password':self.password.text()},auth=False)

    def on_done(self,kind,result,error):
        if error:
            self.statusBar().showMessage('خطأ: '+error)
            QMessageBox.warning(self,'تعذر تنفيذ العملية',error);return
        if kind=='login':
            if result.get('user',{}).get('role')!='admin':
                self.token='';QMessageBox.warning(self,'الصلاحيات','هذا الحساب ليس مديرًا.');return
            self.token=result['token'];self.password.clear()
            self.statusBar().showMessage('تم تسجيل الدخول: '+result['user']['email'])
            self.request('overview','GET','/api/admin/overview')
        elif kind=='v2':self.v2_output.setPlainText(json.dumps(result,ensure_ascii=False,indent=2))
        elif kind=='health':self.connection_info.setText('الخادم متاح: '+json.dumps(result,ensure_ascii=False))
        elif kind=='overview':self.overview.setPlainText(json.dumps(result,ensure_ascii=False,indent=2))
        elif kind=='users':
            self.users.setRowCount(len(result))
            for i,u in enumerate(result):
                for j,key in enumerate(['id','name','email','role','plan','status','created_at']):
                    self.users.setItem(i,j,QTableWidgetItem(str(u.get(key,''))))
        elif kind=='accounts':
            self.accounts=result;self.targets.clear()
            for a in result:self.targets.addItem(f"{a['label']} ({a['provider']} - {a['status']})",a['id'])
        elif kind=='upload':
            self.media_id=result['id'];self.media_label.setText(f"تم الرفع: {result['name']} (#{self.media_id})")
        elif kind=='create_post':
            QMessageBox.information(self,'مهمة النشر','تم إنشاء المهمة؛ تحقق من سجل التسليم في الموقع.')
            self.request('posts','GET','/api/posts')
        elif kind=='posts':self.posts.setPlainText(json.dumps(result,ensure_ascii=False,indent=2))

    def upload_media(self):
        filename,_=QFileDialog.getOpenFileName(self,'اختر صورة أو فيديو','','Media (*.jpg *.jpeg *.png *.webp *.mp4 *.mov)')
        if not filename:return
        p=Path(filename)
        if p.stat().st_size>100*1024*1024:
            QMessageBox.warning(self,'حجم الملف','الحد الأقصى 100 ميجابايت');return
        import mimetypes
        self.request('upload','POST','/api/media',media=(p.name,p.read_bytes(),mimetypes.guess_type(p.name)[0] or 'application/octet-stream'))

    def create_post(self):
        account_id=self.targets.currentData()
        if account_id is None:
            QMessageBox.warning(self,'الحسابات','اختر حساب نشر مرتبطًا من الموقع أولًا.');return
        data={'text':self.post_text.toPlainText(),'mediaId':self.media_id,'accountIds':[account_id],
              'publishNow':self.publish_now.isChecked(),
              'scheduledAt':self.scheduled.dateTime().toUTC().toString('yyyy-MM-ddTHH:mm:ssZ')}
        self.request('create_post','POST','/api/posts',data)

    def local_env(self):
        env=os.environ.copy();env['NODE_ENV']='development';env['PORT']='3000'
        env['DATA_DIR']=str(ROOT/'data')
        env['JWT_SECRET']=self.secret.text().strip() or self.read_or_create_local_secret()
        env['ADMIN_EMAIL']=ADMIN_EMAIL
        return env

    def read_or_create_local_secret(self):
        p=ROOT/'data'/'.windows-local-secret';p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists():return p.read_text(encoding='utf-8').strip()
        value=secrets.token_urlsafe(48)
        p.write_text(value,encoding='utf-8');return value

    def start_local(self):
        if self.local_process and self.local_process.poll() is None:
            self.local_log.append('الخادم يعمل بالفعل.');return
        if not (ROOT/'node_modules').exists():
            QMessageBox.warning(self,'اعتماديات ناقصة','افتح مجلد المشروع وشغّل npm install أولًا.');return
        try:
            flags=getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0)
            self.local_process=subprocess.Popen(['node','src/server.js'],cwd=str(ROOT),env=self.local_env(),
                stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT,creationflags=flags)
            self.url.setText('http://127.0.0.1:3000')
            self.token=''
            self.local_log.append(f'بدأ الخادم المحلي، PID={self.local_process.pid}. افتح http://127.0.0.1:3000')
        except Exception as e:QMessageBox.warning(self,'فشل التشغيل',str(e))

    def stop_local(self):
        if self.local_process and self.local_process.poll() is None:
            self.local_process.terminate()
            try:self.local_process.wait(timeout=5)
            except subprocess.TimeoutExpired:self.local_process.kill()
            self.local_log.append('تم إيقاف الخادم المحلي.')
        else:self.local_log.append('لا يوجد خادم محلي بدأه هذا البرنامج.')

    def setup_local_admin(self):
        from PySide6.QtWidgets import QInputDialog
        password,ok=QInputDialog.getText(self,'كلمة مرور المدير المحلي','أدخل كلمة مرور قوية (12 حرفًا على الأقل):',QLineEdit.EchoMode.Password)
        if not ok:return
        if len(password)<12:
            QMessageBox.warning(self,'كلمة المرور','يجب أن تكون 12 حرفًا على الأقل.');return
        if not (ROOT/'node_modules').exists():
            QMessageBox.warning(self,'اعتماديات ناقصة','شغّل npm install أولًا.');return
        env=self.local_env();env['ADMIN_INITIAL_PASSWORD']=password
        try:
            result=subprocess.run(['node','src/admin-setup.js'],cwd=str(ROOT),env=env,capture_output=True,text=True,timeout=40)
            if result.returncode:raise RuntimeError(result.stderr or result.stdout)
            self.local_log.append('تم إنشاء أو تحديث مدير قاعدة البيانات المحلية.')
        except Exception as e:QMessageBox.warning(self,'خطأ إعداد المدير',str(e))
        finally:env.pop('ADMIN_INITIAL_PASSWORD',None)

    def closeEvent(self,event):
        if self.local_process and self.local_process.poll() is None:
            self.stop_local()
        event.accept()

if __name__=='__main__':
    app=QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    window=Window();window.show()
    sys.exit(app.exec())
