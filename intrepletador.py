#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox, font
import os
import wave
import tempfile
import threading
import subprocess
import shutil
import time
import sys
import qrcode
from PIL import Image, ImageTk

def extrair_conteudo(texto):
    start = texto.find('>')
    end = texto.rfind('.')
    if start == -1 or end == -1 or end <= start:
        return None
    return texto[start+1:end]

def documento_para_bits(doc, one_char='█', zero_char=' '):
    bits = []
    for ch in doc:
        if ch == one_char:
            bits.append('1')
        elif ch == zero_char:
            bits.append('0')
        else:
            continue
    return ''.join(bits)

def bits_para_texto(bits):
    if not bits:
        return ''
    n = (len(bits) // 8) * 8
    bits = bits[:n]
    out = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        out.append(int(byte, 2))
    try:
        return bytes(out).decode('utf-8', errors='replace')
    except Exception:
        return ''.join(chr(x) for x in out)

def carregar_arquivo(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            conteúdo = f.read()
    except Exception as e:
        messagebox.showerror("Erro", str(e))
        return
    doc = extrair_conteudo(conteúdo)
    if doc is None:
        messagebox.showerror("Erro", "Arquivo não está no formato esperado.")
        return
    bits = documento_para_bits(doc)
    texto = bits_para_texto(bits)
    entrada_text.config(state='normal')
    entrada_text.delete("1.0", "end")
    entrada_text.insert("1.0", texto)
    entrada_text.config(state='disabled')
    info_var.set(f"Arquivo: {os.path.basename(path)}  Bits: {len(bits)}  Bytes aprox.: {len(bits)//8}")
    render_bits_view(bits)
    gerar_qrcode(bits_para_texto(bits))
    global current_bits
    current_bits = bits

def abrir_arquivo():
    path = filedialog.askopenfilename(filetypes=[("Text files","*.txt"),("All files","*.*")])
    if not path:
        return
    carregar_arquivo(path)

def render_bits_view(bits):
    for widget in bits_inner.winfo_children():
        widget.destroy()
    if not bits:
        return
    lbl_font = small_mono
    for i, b in enumerate(bits[:500]): # Limita a 500 para performance
        ch = '█' if b == '1' else ' '
        lbl = tk.Label(bits_inner, text=ch, font=big_mono, width=2, bg=colors['bg'], fg=colors['bit_1'] if b == '1' else colors['bit_0'], relief="solid", borderwidth=1, bd=0)
        lbl.grid(row=0, column=i, padx=0, pady=0)
        num = f"{(i+1):03d}"
        lbln = tk.Label(bits_inner, text=num, font=lbl_font, width=2, bg=colors['bg'], fg=colors['fg_subtle'])
        lbln.grid(row=1, column=i, padx=0, pady=0)

    bits_canvas.update_idletasks()
    bits_canvas.config(scrollregion=bits_canvas.bbox("all"))

def make_8bit_tone_for_bits(bits, sr=22050, dur=0.18, freq=880, vol=0.8):
    samples_per_bit = int(dur * sr)
    buf = bytearray()
    for bit in bits:
        if bit == '1':
            period = sr / freq
            half = int(period / 2) if period > 2 else 1
            for i in range(samples_per_bit):
                t = i % int(period)
                v = 1.0 if t < half else -1.0
                s = int((v * 0.5 * vol + 0.5) * 255)
                buf.append(max(0, min(255, s)))
        else:
            buf.extend(b'\x80' * samples_per_bit)
    return bytes(buf)

def write_wav(path, data, sr=22050):
    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(1)
    wf.setframerate(sr)
    wf.writeframes(data)
    wf.close()

def play_bits(bits, bit_duration, freq):
    if not bits:
        return
    sr = 22050
    data = make_8bit_tone_for_bits(bits, sr=sr, dur=bit_duration, freq=freq, vol=0.8)
    path = os.path.join(tempfile.gettempdir(), "interpretador_bits.wav")
    write_wav(path, data, sr=sr)
    stop_playback.clear()
    def highlight_loop():
        for i in range(len(bits)):
            if stop_playback.is_set():
                break
            highlight_bit(i)
            time.sleep(bit_duration)
        clear_highlight()
    threading.Thread(target=highlight_loop, daemon=True).start()
    if sys.platform.startswith('win'):
        import winsound
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        while not stop_playback.is_set():
            time.sleep(0.1)
        winsound.PlaySound(None, winsound.SND_PURGE)
    else:
        player_cmd = None
        if shutil.which('afplay'):
            player_cmd = ['afplay', path]
        elif shutil.which('aplay'):
            player_cmd = ['aplay', path]
        elif shutil.which('ffplay'):
            player_cmd = ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', path]
        if player_cmd:
            p = subprocess.Popen(player_cmd)
            while p.poll() is None and not stop_playback.is_set():
                time.sleep(0.1)
            if p.poll() is None:
                p.terminate()
        else:
            for _ in bits:
                if stop_playback.is_set():
                    break
                time.sleep(bit_duration)
    stop_playback.set()
    btn_play.config(state='normal')
    btn_stop.config(state='disabled')

def highlight_bit(index):
    children = bits_inner.grid_slaves(row=0)
    for w in children:
        w.config(bg=colors['bg'])
    try:
        lbl = bits_inner.grid_slaves(row=0, column=index)[0]
        lbl.config(bg=colors['highlight'])
        bits_canvas.xview_moveto(max(0, (index-10)/max(1, len(current_bits))))
    except:
        pass

def clear_highlight():
    children = bits_inner.grid_slaves(row=0)
    for w in children:
        w.config(bg=colors['bg'])

def iniciar_play():
    bits = current_bits
    if not bits:
        messagebox.showinfo("Info", "Carregue um arquivo codificado antes de tocar.")
        return
    try:
        bit_duration = float(entry_duration.get())
    except:
        bit_duration = 0.18
    try:
        freq = int(entry_freq.get())
    except:
        freq = 880
    btn_play.config(state='disabled')
    btn_stop.config(state='normal')
    stop_playback.clear()
    threading.Thread(target=play_bits, args=(bits, bit_duration, freq), daemon=True).start()

def parar_play():
    stop_playback.set()
    btn_play.config(state='normal')
    btn_stop.config(state='disabled')
    clear_highlight()

def gerar_qrcode(texto):
    img = qrcode.make(texto)
    img = img.resize((200,200))
    photo = ImageTk.PhotoImage(img)
    qr_label.config(image=photo)
    qr_label.image = photo

colors = {
    'bg': '#2b2b2b',
    'bg_right': '#3c3c3c',
    'fg': '#dcdcdc',
    'fg_subtle': '#888888',
    'highlight': '#005f5f',
    'bit_1': '#dcdcdc',
    'bit_0': '#4a4a4a',
    'btn_bg': '#4a4a4a',
    'btn_fg': '#dcdcdc',
    'btn_active': '#5a5a5a',
}

root = tk.Tk()
root.title("Interpretador Aprimorado")
root.geometry("1200x600")
root.configure(bg=colors['bg'])

big_mono = font.Font(family="Courier", size=16)
small_mono = font.Font(family="Courier", size=9)

frame = tk.Frame(root, bg=colors['bg'])
frame.pack(fill="both", expand=True)

left = tk.Frame(frame, width=700, bg=colors['bg'])
left.pack(side="left", fill="both", expand=True)
right = tk.Frame(frame, width=480, bg=colors['bg_right'])
right.pack(side="right", fill="both")

top_controls = tk.Frame(left, bg=colors['bg'])
top_controls.pack(fill="x", pady=6)

btn_style = {'bg': colors['btn_bg'], 'fg': colors['btn_fg'], 'activebackground': colors['btn_active'], 'activeforeground': colors['btn_fg'], 'relief': 'flat', 'bd': 2}
btn_open = tk.Button(top_controls, text="Abrir arquivo", command=abrir_arquivo, **btn_style)
btn_open.pack(side="left", padx=6)
btn_play = tk.Button(top_controls, text="Tocar código", command=iniciar_play, **btn_style)
btn_play.pack(side="left", padx=6)
btn_stop = tk.Button(top_controls, text="Parar", command=parar_play, state='disabled', **btn_style)
btn_stop.pack(side="left", padx=6)

tk.Label(top_controls, text="Duração por bit (s):", bg=colors['bg'], fg=colors['fg']).pack(side="left", padx=(12,0))
entry_duration = tk.Entry(top_controls, width=6, bg=colors['btn_bg'], fg=colors['fg'], insertbackground=colors['fg'], relief='flat')
entry_duration.insert(0, "0.18")
entry_duration.pack(side="left", padx=4)
tk.Label(top_controls, text="Freq (Hz):", bg=colors['bg'], fg=colors['fg']).pack(side="left", padx=(8,0))
entry_freq = tk.Entry(top_controls, width=6, bg=colors['btn_bg'], fg=colors['fg'], insertbackground=colors['fg'], relief='flat')
entry_freq.insert(0, "880")
entry_freq.pack(side="left", padx=4)

bits_container = tk.Frame(left, bg=colors['bg'])
bits_container.pack(fill="both", expand=True, padx=6, pady=6)
bits_canvas = tk.Canvas(bits_container, height=180, bg=colors['bg'], highlightthickness=0)
h_scroll = tk.Scrollbar(bits_container, orient='horizontal', command=bits_canvas.xview)
bits_canvas.configure(xscrollcommand=h_scroll.set)
h_scroll.pack(side="bottom", fill="x")
bits_canvas.pack(side="top", fill="both", expand=True)
bits_inner = tk.Frame(bits_canvas, bg=colors['bg'])
bits_canvas.create_window((0,0), window=bits_inner, anchor="nw")

info_var = tk.StringVar()
info_var.set("Nenhum arquivo carregado")
lbl_info = tk.Label(left, textvariable=info_var, bg=colors['bg'], fg=colors['fg_subtle'])
lbl_info.pack(pady=6)

entrada_text = tk.Text(right, wrap="word", font=("Helvetica", 12), bg=colors['bg_right'], fg=colors['fg'], relief='flat', bd=0)
entrada_text.pack(fill="both", expand=True, padx=8, pady=8)
entrada_text.config(state='disabled')
qr_label = tk.Label(right, bg=colors['bg_right'])
qr_label.pack(pady=6)

stop_playback = threading.Event()
current_bits = ''
root.mainloop()
