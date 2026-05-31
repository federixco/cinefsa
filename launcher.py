"""launcher.py — Mini launcher para CineFSA."""

import tkinter as tk, subprocess, threading, webbrowser, socket, os, time, sys

DIR = os.path.dirname(os.path.abspath(__file__))
PY  = sys.executable
MYSQLD = r'c:\xampp\mysql\bin\mysqld.exe'
MYSQLADMIN = r'c:\xampp\mysql\bin\mysqladmin.exe'
MYSQL_INI = r'c:\xampp\mysql\bin\my.ini'

def port_ok(p):
    try:
        with socket.socket() as s:
            s.settimeout(0.5)
            return s.connect_ex(('127.0.0.1', p)) == 0
    except: return False


class App:
    def __init__(self):
        self.django_proc = None
        self.r = tk.Tk()
        self.r.title('CineFSA')
        self.r.configure(bg='#0f0f1a')
        self.r.geometry('400x380')
        self.r.resizable(False, False)

        # Header
        h = tk.Frame(self.r, bg='#0f0f1a')
        h.pack(pady=(20, 10))
        tk.Label(h, text='Cine', font=('Segoe UI', 24, 'bold'), fg='#fff', bg='#0f0f1a').pack(side='left')
        tk.Label(h, text='FSA', font=('Segoe UI', 24, 'bold'), fg='#e94560', bg='#0f0f1a').pack(side='left')

        # MySQL row
        self.mysql_dot, self.mysql_btn = self._row('🗃️ MySQL (3306)')
        # Django row
        self.django_dot, self.django_btn = self._row('⚙️ Django (8000)')

        # Browser button
        self.br_btn = tk.Button(self.r, text='🌐  Abrir en Navegador', font=('Segoe UI', 11, 'bold'),
            fg='#fff', bg='#448aff', activebackground='#5c9aff', relief='flat', bd=0, pady=8, padx=20,
            cursor='hand2', command=lambda: webbrowser.open('http://127.0.0.1:8000/'), state='disabled')
        self.br_btn.pack(pady=(15, 10))

        # Log
        self.log = tk.Text(self.r, height=6, bg='#0f0f1a', fg='#6a6a8a', font=('Consolas', 9),
            relief='flat', bd=0, wrap='word', state='disabled')
        self.log.pack(fill='both', expand=True, padx=25, pady=(5, 20))

        self._msg('Launcher listo.')
        self.r.protocol('WM_DELETE_WINDOW', self._close)
        self._tick()

    def _row(self, label):
        f = tk.Frame(self.r, bg='#1a1a2e', highlightthickness=1, highlightbackground='#2a2a4a')
        f.pack(fill='x', padx=25, pady=4)
        inner = tk.Frame(f, bg='#1a1a2e')
        inner.pack(fill='x', padx=12, pady=10)
        dot = tk.Label(inner, text='●', font=('Segoe UI', 14), fg='#ff1744', bg='#1a1a2e')
        dot.pack(side='left')
        tk.Label(inner, text=label, font=('Segoe UI', 11, 'bold'), fg='#e0e0f0', bg='#1a1a2e').pack(side='left', padx=8)
        btn = tk.Button(inner, text='Iniciar', font=('Segoe UI', 10, 'bold'), width=9,
            fg='#fff', bg='#00c853', activebackground='#00e676', relief='flat', bd=0, pady=5, cursor='hand2')
        btn.pack(side='right')
        return dot, btn

    def _msg(self, t):
        self.log.configure(state='normal')
        self.log.insert('end', f'[{time.strftime("%H:%M:%S")}] {t}\n')
        self.log.see('end')
        self.log.configure(state='disabled')

    def _tick(self):
        m, d = port_ok(3306), port_ok(8000)
        self.mysql_dot.config(fg='#00e676' if m else '#ff1744')
        self.django_dot.config(fg='#00e676' if d else '#ff1744')
        self.mysql_btn.config(text='Detener' if m else 'Iniciar', bg='#ff1744' if m else '#00c853',
            command=self._stop_mysql if m else self._start_mysql)
        self.django_btn.config(text='Detener' if d else 'Iniciar', bg='#ff1744' if d else '#00c853',
            command=self._stop_django if d else self._start_django)
        self.br_btn.config(state='normal' if d else 'disabled')
        self.r.after(2000, self._tick)

    def _bg(self, fn):
        threading.Thread(target=fn, daemon=True).start()

    def _start_mysql(self):
        def go():
            self._msg('Iniciando MySQL...')
            subprocess.Popen([MYSQLD, f'--defaults-file={MYSQL_INI}', '--standalone'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
            for _ in range(20):
                time.sleep(0.5)
                if port_ok(3306): self._msg('MySQL listo.'); return
            self._msg('MySQL no respondió.')
        self._bg(go)

    def _stop_mysql(self):
        def go():
            self._msg('Deteniendo MySQL...')
            subprocess.run([MYSQLADMIN, '-u', 'root', 'shutdown'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10, creationflags=0x08000000)
            self._msg('MySQL detenido.')
        self._bg(go)

    def _start_django(self):
        def go():
            if not port_ok(3306): self._msg('Iniciá MySQL primero.'); return
            self._msg('Iniciando Django...')
            self.django_proc = subprocess.Popen([PY, os.path.join(DIR, 'manage.py'), 'runserver', '--noreload'],
                cwd=DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
            for _ in range(20):
                time.sleep(0.5)
                if port_ok(8000): self._msg('Django listo → http://127.0.0.1:8000/'); return
            self._msg('Django no respondió.')
        self._bg(go)

    def _stop_django(self):
        if self.django_proc:
            self.django_proc.terminate()
            self.django_proc = None
            self._msg('Django detenido.')

    def _close(self):
        try:
            if self.django_proc: self.django_proc.terminate()
        except:
            pass
        self.r.destroy()
        import sys; sys.exit(0)


if __name__ == '__main__':
    try:
        App().r.mainloop()
    except KeyboardInterrupt:
        pass
