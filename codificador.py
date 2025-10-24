#!/usr/bin/env python3
import tkinter as tk
from tkinter import font, filedialog, messagebox
import os
import sys
import subprocess

try:
    import qrcode
    from PIL import Image, ImageTk
    QR_AVAILABLE = True
except Exception:
    QR_AVAILABLE = False

def texto_para_bitstream(texto):
    b = texto.encode('utf-8')
    bits = []
    for byte in b:
        bits.append('{:08b}'.format(byte))
    return ''.join(bits)

def bits_para_documento(bits, um_char='█', zero_char=' '):
    m = ''.join(um_char if ch == '1' else zero_char for ch in bits)
    parts = [m[i:i+64] for i in range(0, len(m), 64)]
    return '>' + '\n'.join(parts) + '.'

def atualizar_preview(event=None):
    texto = entrada.get("1.0", "end-1c")
    bits = texto_para_bitstream(texto) if texto else ''
    doc = bits_para_documento(bits) if bits else '>.'
    preview.config(state='normal')
    preview.delete("1.0", "end")
    preview.insert("1.0", doc)
    preview.config(state='disabled')
    atualizar_estatisticas(bits)
    atualizar_qr_preview(texto)

def atualizar_estatisticas(bits):
    n_bits = len(bits)
    aprox_bytes = n_bits // 8
    stats_var.set(f"Bits: {n_bits}   Bytes aproximados: {aprox_bytes}")

def salvar():
    texto = entrada.get("1.0", "end-1c")
    if not texto:
        messagebox.showinfo("Aviso", "Digite uma mensagem antes de salvar.")
        return
    bits = texto_para_bitstream(texto)
    doc = bits_para_documento(bits)
    path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files","*.txt"),("All files","*.*")])
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(doc)
        status_var.set(f"Arquivo salvo: {path}")
        last_saved_path.set(path)
        abrir_pasta(path)
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def abrir_pasta(path=None):
    if not path:
        path = last_saved_path.get()
    if not path:
        messagebox.showinfo("Info", "Nenhum arquivo salvo para abrir a pasta.")
        return
    folder = os.path.dirname(os.path.abspath(path))
    try:
        if sys.platform.startswith('win'):
            os.startfile(folder)
        elif sys.platform.startswith('darwin'):
            subprocess.run(['open', folder])
        else:
            subprocess.run(['xdg-open', folder])
    except Exception:
        pass

def limpar():
    entrada.delete("1.0","end")
    atualizar_preview()

def copiar_clipboard():
    texto = entrada.get("1.0", "end-1c")
    if not texto:
        messagebox.showinfo("Aviso", "Nada para copiar.")
        return
    bits = texto_para_bitstream(texto)
    doc = bits_para_documento(bits)
    janela.clipboard_clear()
    janela.clipboard_append(doc)
    status_var.set("Documento codificado copiado para a área de transferência")

def gerar_qr():
    if not QR_AVAILABLE:
        messagebox.showinfo("Info", "Bibliotecas qrcode/Pillow não disponíveis.")
        return
    texto = entrada.get("1.0", "end-1c")
    if not texto:
        messagebox.showinfo("Aviso", "Digite uma mensagem para gerar QR.")
        return
    img = qrcode.make(texto)
    img = img.resize((220,220))
    photo = ImageTk.PhotoImage(img)
    qr_label.config(image=photo, text='')
    qr_label.image = photo
    status_var.set("QR Code gerado")

def atualizar_qr_preview(texto):
    if not QR_AVAILABLE:
        qr_btn.config(state='disabled')
        qr_label.config(image='', text='QR não disponível', fg='#aaaaaa', bg=colors['bg'])
        return
    qr_btn.config(state='normal')
    if not texto:
        qr_label.config(image='', text='QR preview vazio', fg=colors['fg_subtle'], bg=colors['bg'])
        qr_label.image = None
        return
    try:
        img = qrcode.make(texto)
        img = img.resize((120,120))
        photo = ImageTk.PhotoImage(img)
        qr_label.config(image=photo, text='')
        qr_label.image = photo
    except Exception:
        qr_label.config(image='', text='Erro QR', fg='#ff8888', bg=colors['bg'])
        qr_label.image = None

colors = {
    'bg': '#121213',
    'fg': '#e6e6e6',
    'fg_subtle': '#9a9aa0',
    'btn_bg': '#1f1f1f',
    'btn_fg': '#e6e6e6',
    'btn_active': '#2a2a2a',
    'input_bg': '#0f0f10',
    'accent': '#6bd6ff'
}

janela = tk.Tk()
janela.title("Codificador de Mensagem")
janela.geometry("900x700")
janela.configure(bg=colors['bg'])

mono = font.Font(family="Courier", size=12)
mono_small = font.Font(family="Courier", size=10)
mono_big = font.Font(family="Courier", size=14, weight='bold')

container = tk.Frame(janela, bg=colors['bg'])
container.pack(fill="both", expand=True, padx=12, pady=12)

left = tk.Frame(container, bg=colors['bg'])
left.pack(side="left", fill="both", expand=True, padx=(0,8))
right = tk.Frame(container, width=260, bg=colors['bg'])
right.pack(side="right", fill="y")

lbl = tk.Label(left, text="Digite sua mensagem:", bg=colors['bg'], fg=colors['fg'], font=mono_big)
lbl.pack(anchor="w", pady=(0,6))

entrada = tk.Text(left, height=8, font=mono, wrap="word", bg=colors['input_bg'], fg=colors['fg'], insertbackground=colors['fg'], relief='flat', bd=0)
entrada.pack(fill="x")
entrada.bind("<KeyRelease>", atualizar_preview)

btn_frame = tk.Frame(left, bg=colors['bg'])
btn_frame.pack(fill="x", pady=8)

btn_style = {'bg': colors['btn_bg'], 'fg': colors['btn_fg'], 'activebackground': colors['btn_active'], 'activeforeground': colors['btn_fg'], 'relief': 'flat', 'bd': 1, 'padx':6, 'pady':6}
btn_salvar = tk.Button(btn_frame, text="Salvar arquivo codificado", command=salvar, **btn_style)
btn_salvar.pack(side="left", padx=(0,6))
btn_copiar = tk.Button(btn_frame, text="Copiar codificado", command=copiar_clipboard, **btn_style)
btn_copiar.pack(side="left", padx=(0,6))
btn_limpar = tk.Button(btn_frame, text="Limpar", command=limpar, **btn_style)
btn_limpar.pack(side="left")

stats_frame = tk.Frame(left, bg=colors['bg'])
stats_frame.pack(fill="x", pady=(6,0))
stats_var = tk.StringVar()
stats_var.set("Bits: 0   Bytes aproximados: 0")
lbl_stats = tk.Label(stats_frame, textvariable=stats_var, bg=colors['bg'], fg=colors['fg_subtle'], font=mono_small)
lbl_stats.pack(anchor="w")

preview_label = tk.Label(left, text="Preview do arquivo codificado (█ = 1, espaço = 0). Início: '>'  Fim: '.'", bg=colors['bg'], fg=colors['fg_subtle'], font=mono_small)
preview_label.pack(anchor="w", pady=(8,0))

preview = tk.Text(left, height=14, font=mono, wrap="char", state="disabled", bg=colors['input_bg'], fg=colors['fg'], relief='flat', bd=0)
preview.pack(fill="both", expand=True, pady=(6,0))

status_var = tk.StringVar()
status_var.set("Pronto")
status_bar = tk.Label(janela, textvariable=status_var, bg=colors['bg'], fg=colors['fg_subtle'], anchor="w")
status_bar.pack(fill="x", side="bottom")

qr_title = tk.Label(right, text="QR Code", bg=colors['bg'], fg=colors['fg'], font=mono_big)
qr_title.pack(pady=(6,0))

file_actions = tk.Frame(right, bg=colors['bg'])
file_actions.pack(fill="x", padx=8, pady=(6,0))
open_folder_btn = tk.Button(file_actions, text="Abrir pasta do último salvo", command=lambda: abrir_pasta(None), **btn_style)
open_folder_btn.pack(fill="x")
last_saved_path = tk.StringVar()
last_saved_path.set("")

qr_btn = tk.Button(right, text="Gerar QR (mensagem)", command=gerar_qr, **btn_style)
qr_btn.pack(fill="x", padx=8, pady=(6,0))
if not QR_AVAILABLE:
    qr_btn.config(state='disabled')

qr_label = tk.Label(right, text="Preview QR", bg=colors['bg'], fg=colors['fg_subtle'], width=20, height=10)
qr_label.pack(pady=(12,8))

help_label = tk.Label(right, text="Tema: Escuro\nCaractere 1: █   Caractere 0: espaço\nLinhas de 64 cols", bg=colors['bg'], fg=colors['fg_subtle'], justify="left", font=mono_small)
help_label.pack(fill="x", padx=8, pady=(6,0))

atualizar_preview()
janela.mainloop()
