import time
import os
import sys
import threading
import tkinter as tk
from tkinter import scrolledtext
import re
import sqlparse

LOG_FILE = 'sql_queries.log'

class SQLMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor SQL en Tiempo Real - CineFSA")
        self.root.geometry("900x700")
        self.root.configure(bg="#1e1e1e")

        # Marco superior para controles
        self.control_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.control_frame.pack(fill='x', padx=10, pady=(10, 0))

        # Botón para limpiar
        self.btn_clear = tk.Button(
            self.control_frame, text="🗑️ Limpiar Consultas", 
            command=self.clear_text, bg="#d32f2f", fg="white", 
            font=("Arial", 10, "bold"), relief=tk.FLAT, padx=10, pady=5
        )
        self.btn_clear.pack(side=tk.RIGHT)

        # Configurar área de texto
        self.text_area = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, bg="#1e1e1e", fg="#d4d4d4",
            font=("Consolas", 11)
        )
        self.text_area.pack(expand=True, fill='both', padx=10, pady=10)

        # Definir etiquetas de colores para sintaxis
        self.text_area.tag_config('info', foreground='#888888')
        self.text_area.tag_config('insert', foreground='#4CAF50', font=("Consolas", 11, "bold"))
        self.text_area.tag_config('select', foreground='#00BCD4')
        self.text_area.tag_config('update', foreground='#FFC107', font=("Consolas", 11, "bold"))
        self.text_area.tag_config('transaction', foreground='#E040FB', font=("Consolas", 11, "bold"))
        self.text_area.tag_config('args', foreground='#FF9800', font=("Consolas", 10, "italic"))

        self.insert_text("============================================================\n", 'info')
        self.insert_text(" 🚀 MONITOR SQL CON INTERFAZ GRÁFICA - CineFSA 🚀\n", 'transaction')
        self.insert_text("============================================================\n", 'info')
        self.insert_text("Esperando consultas en la base de datos...\n\n", 'info')

        self.running = True
        self.thread = threading.Thread(target=self.tail_file)
        self.thread.daemon = True
        self.thread.start()

    def insert_text(self, text, tag):
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, text, tag)
        self.text_area.configure(state='disabled')
        self.text_area.yview(tk.END)

    def clear_text(self):
        self.text_area.configure(state='normal')
        self.text_area.delete('1.0', tk.END)
        self.text_area.configure(state='disabled')
        self.insert_text("============================================================\n", 'info')
        self.insert_text(" 🚀 MONITOR SQL CON INTERFAZ GRÁFICA - CineFSA 🚀\n", 'transaction')
        self.insert_text("============================================================\n", 'info')
        self.insert_text("Pantalla limpia. Esperando nuevas consultas...\n\n", 'info')

    def tail_file(self):
        if not os.path.exists(LOG_FILE):
            open(LOG_FILE, 'w').close()

        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            # Ir al final del archivo para leer en vivo
            f.seek(0, 2)
            while self.running:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                
                # Expresión regular para separar el tiempo, la query pura y los argumentos
                match = re.search(r'(\[.*?\] \(\d+\.\d+\)) (.*?)(?:; args=(.*?); alias=default|; args=None; alias=default)?$', line.strip())
                
                if match:
                    prefix = match.group(1)
                    raw_sql = match.group(2)
                    args = match.group(3) if match.group(3) else "Ninguno"
                    
                    # MAGIA: Usar sqlparse para identar y darle formato legible al SQL crudo
                    try:
                        formatted_sql = sqlparse.format(raw_sql, reindent=True, keyword_case='upper')
                    except Exception:
                        formatted_sql = raw_sql

                    # Colorear según la operación
                    tag = 'info'
                    sql_upper = raw_sql.upper()
                    if sql_upper.startswith('INSERT'): tag = 'insert'
                    elif sql_upper.startswith('SELECT'): tag = 'select'
                    elif sql_upper.startswith('UPDATE') or sql_upper.startswith('DELETE'): tag = 'update'
                    elif sql_upper.startswith('BEGIN') or sql_upper.startswith('COMMIT') or sql_upper.startswith('SET'): tag = 'transaction'
                    
                    self.insert_text(f"{prefix}\n", 'info')
                    self.insert_text(f"{formatted_sql}\n", tag)
                    if args != "Ninguno":
                        self.insert_text(f"  → Parámetros: {args}\n", 'args')
                    self.insert_text("-" * 70 + "\n", 'info')
                else:
                    self.insert_text(line, 'info')

    def on_closing(self):
        self.running = False
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = SQLMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
