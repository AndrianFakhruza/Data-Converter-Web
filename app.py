from flask import Flask, render_template, request, redirect, url_for, send_file, flash, get_flashed_messages
import os
import pandas as pd
import matplotlib.pyplot as plt
import calendar

app = Flask(__name__)
app.secret_key = 'supersecretkey'

desa_list = sorted([
    "SIDO MULYO", "CEMPEDAK", "BAYU", "BL. TALON", "BUKET", "COT MERBO",
    "COT RHEU", "LHOKJOK", "MEUNASAH DAYAH", "PULO BARAT", "MEUNASAH KUMBANG",
    "Panton Rayek 1", "KR. SEPENG", "BL. GURAH", "CEMECET", "KR. MANYANG",
    "SEUNEBOK DRIEN", "BL. ADO", "BL. ARA", "COT SEUTUI", "ALU RAMBE",
    "MULING MEUCAT", "KRESEK", "PULO RAYEUK", "LANGKUTA", "BL. RIEK",
    "FASKES LAIN", "BABAH LUENG", "GUHA ULHEU", "KR. SENONG", "MC. BAHAGIA",
    "MEUNASAH KULAM", "KD. KRUENG", "COT SEMIYONG", "PULO IBOH", "KEUDE BLANG ARA",
    "MEURIYA", "P. RAYEUK 2", "MULING MANYANG", "SAWEUK"
])

pemeriksaan_list = sorted([
    "CHOLESTEROL", "KADAR GULA DARAH", "TBC", "SIPILIS", "HIV", "HBSAG", "WIDAL",
    "ASAM URAT", "DARAH RUTIN", "URINALISA", "GOLONGAN DARAH", "CAMPAK", "MALARIA",
    "TRIGLISERIDA", "DBD", "SGOT", "SGPT", "T.PROTEIN", "R.FAKTOR", "CREATININT",
    "UREA", "ALBUMIN", "BIL.DIRECT"
])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/isi_desa', methods=['GET', 'POST'])
def isi_jumlah_desa():
    if request.method == 'POST':
        bulan = request.form['bulan'].zfill(2)
        tahun = request.form['tahun']
        return render_template('form_input_desa.html', bulan=bulan, tahun=tahun, desa_list=desa_list)
    return render_template('isi_desa.html')

@app.route('/isi_pemeriksaan', methods=['GET', 'POST'])
def isi_jumlah_pemeriksaan():
    if request.method == 'POST':
        bulan = request.form['bulan'].zfill(2)
        tahun = request.form['tahun']
        return render_template('form_input_pemeriksaan.html', bulan=bulan, tahun=tahun, pemeriksaan_list=pemeriksaan_list)
    return render_template('isi_pemeriksaan.html')

@app.route('/input_desa', methods=['POST'])
def input_desa():
    bulan = request.form.get('bulan').zfill(2)
    tahun = request.form.get('tahun')
    data = {'nama_desa': [], 'jumlah': []}

    for nama in desa_list:
        jumlah = request.form.get(nama)
        jumlah = int(jumlah) if jumlah and jumlah.isdigit() else 0
        data['nama_desa'].append(nama)
        data['jumlah'].append(jumlah)

    df = pd.DataFrame(data)
    os.makedirs('data', exist_ok=True)
    df.to_csv(f"data/jumlah_desa_{tahun}_{bulan}.csv", index=False)

    # render ulang form dengan success message
    return render_template(
        'form_input_desa.html',
        bulan=bulan,
        tahun=tahun,
        desa_list=desa_list,
        success=True
    )

@app.route('/input_pemeriksaan', methods=['POST'])
def input_pemeriksaan():
    bulan = request.form.get('bulan').zfill(2)
    tahun = request.form.get('tahun')
    data = {'nama_pemeriksaan': [], 'jumlah': []}

    for nama in pemeriksaan_list:
        jumlah = request.form.get(nama)
        jumlah = int(jumlah) if jumlah and jumlah.isdigit() else 0
        data['nama_pemeriksaan'].append(nama)
        data['jumlah'].append(jumlah)

    df = pd.DataFrame(data)
    os.makedirs('data', exist_ok=True)
    df.to_csv(f"data/jumlah_pemeriksaan_{tahun}_{bulan}.csv", index=False)

    return render_template(
        'form_input_pemeriksaan.html',
        bulan=bulan,
        tahun=tahun,
        pemeriksaan_list=pemeriksaan_list,
        success=True
    )

@app.route('/sukses')
def sukses():
    messages = get_flashed_messages()
    return render_template('sukses.html', messages=messages)

@app.route('/generate', methods=['GET', 'POST'])
def generate_grafik():
    if request.method == 'POST':
        bulan = request.form['bulan'].zfill(2)
        tahun = request.form['tahun']
        nama_bulan = calendar.month_name[int(bulan)]

        os.makedirs('static/grafik', exist_ok=True)

        path_desa = f"data/jumlah_desa_{tahun}_{bulan}.csv"
        path_periksa = f"data/jumlah_pemeriksaan_{tahun}_{bulan}.csv"

        if not os.path.exists(path_desa) and not os.path.exists(path_periksa):
            flash(f"Data untuk bulan {int(bulan)}/{tahun} belum tersedia.")
            return redirect(url_for('sukses'))

        grafik_desa = None
        grafik_pemeriksaan = None

        if os.path.exists(path_desa):
            df_desa = pd.read_csv(path_desa).sort_values(by="jumlah", ascending=False)
            plt.figure(figsize=(11.7, 8.3))
            bars = plt.bar(df_desa['nama_desa'], df_desa['jumlah'])
            plt.xticks(rotation=90)
            plt.title(f"DATA JUMLAH PEMERIKSAAN LABORATORIUM PERDESA\nBULAN {nama_bulan.upper()} {tahun}")
            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval + 1, int(yval), ha='center', fontsize=8)
            plt.tight_layout()
            path_gambar_desa = f"static/grafik/desa_{tahun}_{bulan}.png"
            plt.savefig(path_gambar_desa)
            plt.close()
            grafik_desa = path_gambar_desa.replace("static/", "")

        if os.path.exists(path_periksa):
            df_periksa = pd.read_csv(path_periksa).sort_values(by="jumlah", ascending=False)
            plt.figure(figsize=(11.7, 8.3))
            bars = plt.bar(df_periksa['nama_pemeriksaan'], df_periksa['jumlah'], color='orange')
            plt.xticks(rotation=90)
            plt.title(f"GRAFIK JUMLAH PEMERIKSAAN LAB BULAN {nama_bulan.upper()} {tahun}")
            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval + 1, int(yval), ha='center', fontsize=8)
            plt.tight_layout()
            path_gambar_periksa = f"static/grafik/pemeriksaan_{tahun}_{bulan}.png"
            plt.savefig(path_gambar_periksa)
            plt.close()
            grafik_pemeriksaan = path_gambar_periksa.replace("static/", "")

        return render_template(
            'grafik.html',
            bulan=bulan,
            tahun=tahun,
            grafik_desa=grafik_desa,
            grafik_pemeriksaan=grafik_pemeriksaan
        )

    return render_template('generate.html')
