import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Nama file CSV
FILE_NAME = "pembukuan_koperasi.csv"

# Cek file CSV, kalau belum ada buat
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=[
        "Tanggal", "Nama", "Pinjaman", "Angsuran",
        "Sisa Saldo", "Tempo", "Jenis Tempo", "Status"
    ])
    df.to_csv(FILE_NAME, index=False, encoding="utf-8")
else:
    df = pd.read_csv(FILE_NAME)

st.set_page_config(page_title="Pembukuan Koperasi", layout="wide")
st.title("📒 Aplikasi Pembukuan Koperasi Harian")

menu = st.sidebar.radio("Menu", ["Input Pinjaman", "Pembayaran Angsuran", "Data Pembukuan", "Hapus Data"])

# ----------------- Input Pinjaman -----------------
if menu == "Input Pinjaman":
    st.subheader("➕ Input Pinjaman")

    nama = st.text_input("Nama Anggota")
    pinjaman_awal = st.number_input("Jumlah Pinjaman (akan dihitung 120% / 150%)", min_value=0.0)

    jenis_tempo = st.selectbox("Pilih Jenis Tempo", ["Harian", "Mingguan", "Bulanan"])

    if jenis_tempo == "Harian":
        tempo = st.selectbox("Pilih Tempo Harian", [24, 30])
        pinjaman_total = pinjaman_awal * 1.2
    elif jenis_tempo == "Mingguan":
        tempo = st.selectbox("Pilih Tempo Mingguan", [6, 8, 10])
        pinjaman_total = pinjaman_awal * 1.2
    else:  # Bulanan
        tempo = st.selectbox("Pilih Tempo Bulanan", [1, 2, 3, 4, 5])
        pinjaman_total = pinjaman_awal * 1.5

    st.info(f"Total Pinjaman: Rp {pinjaman_total:,.0f}")

    if st.button("Simpan Pinjaman"):
        if nama and pinjaman_awal > 0:
            new_data = pd.DataFrame([{
                "Tanggal": datetime.today().strftime("%Y-%m-%d"),
                "Nama": nama,
                "Pinjaman": pinjaman_total,
                "Angsuran": 0,
                "Sisa Saldo": pinjaman_total,
                "Tempo": tempo,
                "Jenis Tempo": jenis_tempo,
                "Status": "Aktif"
            }])
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(FILE_NAME, index=False, encoding="utf-8")
            st.success("✅ Data pinjaman berhasil disimpan!")
        else:
            st.warning("Harap isi nama dan jumlah pinjaman!")

# ----------------- Pembayaran Angsuran -----------------
elif menu == "Pembayaran Angsuran":
    st.subheader("💰 Pembayaran Angsuran")

    if df.empty:
        st.warning("Belum ada data pinjaman.")
    else:
        nama_pilih = st.selectbox("Pilih Nama Nasabah", df["Nama"].unique())
        data_nasabah = df[df["Nama"] == nama_pilih].iloc[-1]

        st.write(f"**Sisa Saldo:** Rp {data_nasabah['Sisa Saldo']:,.0f}")
        st.write(f"**Tempo Tersisa:** {data_nasabah['Tempo']} {data_nasabah['Jenis Tempo']}")

        angsuran = st.number_input("Masukkan Jumlah Angsuran", min_value=0.0)

        if st.button("Bayar Angsuran"):
            idx = df[df["Nama"] == nama_pilih].index[-1]

            df.at[idx, "Angsuran"] = angsuran
            df.at[idx, "Sisa Saldo"] = max(0, df.at[idx, "Sisa Saldo"] - angsuran)

            # Kurangi tempo
            if df.at[idx, "Tempo"] > 0:
                df.at[idx, "Tempo"] -= 1

            # Update status
            if df.at[idx, "Sisa Saldo"] == 0:
                df.at[idx, "Status"] = "Lunas"
            elif df.at[idx, "Tempo"] == 0 and df.at[idx, "Sisa Saldo"] > 0:
                df.at[idx, "Status"] = "Jatuh Tempo"
            else:
                df.at[idx, "Status"] = "Aktif"

            df.to_csv(FILE_NAME, index=False, encoding="utf-8")
            st.success("✅ Angsuran berhasil dicatat!")

# ----------------- Data Pembukuan -----------------
elif menu == "Data Pembukuan":
    st.subheader("📊 Data Pembukuan")

    if df.empty:
        st.warning("Belum ada data.")
    else:
        # 🔔 Cek jatuh tempo
        jatuh_tempo = df[df["Status"] == "Jatuh Tempo"]
        if not jatuh_tempo.empty:
            st.error(f"⚠️ Ada {len(jatuh_tempo)} nasabah yang sudah Jatuh Tempo!")
            st.table(jatuh_tempo[["Tanggal", "Nama", "Sisa Saldo", "Tempo", "Jenis Tempo"]])

        # 🔍 Filter nama
        pilihan_nama = st.selectbox("Filter Nama Nasabah", ["Semua"] + list(df["Nama"].unique()))
        if pilihan_nama != "Semua":
            data_tampil = df[df["Nama"] == pilihan_nama]
        else:
            data_tampil = df

        # Warna status
        def warna_status(val):
            if val == "Lunas":
                return "background-color: lightgreen; color: black"
            elif val == "Jatuh Tempo":
                return "background-color: pink; color: red; font-weight: bold"
            else:
                return "background-color: lightblue; color: black"

        st.dataframe(data_tampil.style.applymap(warna_status, subset=["Status"]))

        total_pinjaman = data_tampil["Pinjaman"].sum()
        total_sisa = data_tampil["Sisa Saldo"].sum()

        st.metric("Total Pinjaman", f"Rp {total_pinjaman:,.0f}")
        st.metric("Total Sisa Saldo", f"Rp {total_sisa:,.0f}")

# ----------------- Hapus Data -----------------
elif menu == "Hapus Data":
    st.subheader("🗑️ Hapus Data Nasabah")

    if df.empty:
        st.warning("Belum ada data.")
    else:
        nama_hapus = st.selectbox("Pilih Nama Nasabah", df["Nama"].unique())

        if st.button("Hapus Data"):
            df = df[df["Nama"] != nama_hapus]
            df.to_csv(FILE_NAME, index=False, encoding="utf-8")
            st.success(f"✅ Data nasabah '{nama_hapus}' berhasil dihapus!")
