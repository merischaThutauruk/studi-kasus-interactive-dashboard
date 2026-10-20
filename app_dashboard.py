import datetime
try:
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.express as px
except ImportError as e:
    print(f"[ERROR] Pustaka visualisasi belum lengkap: {e}")
    print("[INFO] Jalankan terminal: pip install streamlit pandas numpy plotly")
    exit(1)

st.set_page_config(
    page_title="EcoVision: Advanced Deforestation Intelligence Dashboard",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .main-header { font-size: 28px; font-weight: 700; color: #1E3A8A; }
        .sub-text { font-size: 15px; color: #4B5563; }
        .metric-card { background-color: #F3F4F6; padding: 15px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🛰️ EcoVision: Sistem Pemantauan Hutan & Atribusi AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Menerapkan prinsip <b>Shneiderman’s Information Seeking Mantra</b>: Overview first, zoom and filter, details-on-demand.</p>', unsafe_allow_html=True)
st.divider()

@st.cache_data
def load_complex_dashboard_data():
    np.random.seed(42)
    n_records = 300
    
    provinces = ["Kalimantan Barat", "Kalimantan Timur", "Sumatera Selatan", "Papua Tengah", "Sulawesi Tengah"]
    drivers = ["Pertanian Skala Kecil", "Pertanian Industri", "Pertambangan", "Penebangan (Logging)", "Kebakaran Lahan"]
    
    start_date = datetime.date(2026, 1, 1)
    dates = [start_date + datetime.timedelta(days=int(np.random.randint(0, 90))) for _ in range(n_records)]
    
    df = pd.DataFrame({
        "Tanggal": pd.to_datetime(dates),
        "Provinsi": np.random.choice(provinces, n_records),
        "Faktor_Pemicu": np.random.choice(drivers, n_records, p=[0.35, 0.25, 0.15, 0.15, 0.10]),
        "Luas_Deforestasi_Ha": np.random.uniform(5.0, 150.0, n_records).round(2),
        "Tingkat_Keyakinan_AI": np.random.uniform(0.75, 0.99, n_records).round(3),
        "Latitude": -2.0 + np.random.uniform(-1.5, 1.5, n_records),
        "Longitude": 115.0 + np.random.uniform(-5.0, 5.0, n_records)
    })
    return df.sort_values(by="Tanggal").reset_index(drop=True)

df_raw = load_complex_dashboard_data()

st.sidebar.header("🎛️ Panel Kontrol & Filter Spasial")

selected_provinces = st.sidebar.multiselect(
    "Pilih Wilayah Provinsi:",
    options=df_raw["Provinsi"].unique(),
    default=df_raw["Provinsi"].unique()
)

selected_drivers = st.sidebar.multiselect(
    "Filter Faktor Pemicu (Drivers):",
    options=df_raw["Faktor_Pemicu"].unique(),
    default=df_raw["Faktor_Pemicu"].unique()
)

min_date = df_raw["Tanggal"].min().date()
max_date = df_raw["Tanggal"].max().date()
date_range = st.sidebar.date_input(
    "Rentang Waktu Pengamatan:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

df_filtered = df_raw[
    (df_raw["Provinsi"].isin(selected_provinces)) &
    (df_raw["Faktor_Pemicu"].isin(selected_drivers)) &
    (df_raw["Tanggal"].dt.date >= date_range[0]) &
    (df_raw["Tanggal"].dt.date <= date_range[1])
]

if df_filtered.empty:
    st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang dipilih. Harap sesuaikan kembali parameter di sidebar.")
    st.stop()

st.subheader("📊 Ringkasan Eksekutif (Overview)")
col1, col2, col3, col4 = st.columns(4)

total_luas = df_filtered["Luas_Deforestasi_Ha"].sum()
total_kejadian = len(df_filtered)
avg_confidence = df_filtered["Tingkat_Keyakinan_AI"].mean() * 100
max_luas_kejadian = df_filtered["Luas_Deforestasi_Ha"].max()

col1.metric("Total Kehilangan Hutan", f"{total_luas:,.1f} Ha")
col2.metric("Total Peringatan Terdeteksi", f"{total_kejadian:,} Kasus")
col3.metric("Rata-rata Keyakinan AI", f"{avg_confidence:.1f}%")
col4.metric("Kejadian Terbesar", f"{max_luas_kejadian:,.1f} Ha")

st.divider()

tab1, tab2, tab3 = st.tabs(["📈 Tren & Pemicu", "🗺️ Sebaran Geospasial", "🤖 Analisis AI & Keyakinan"])

with tab1:
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown("##### Tren Kerusakan Hutan Berdasarkan Waktu")
        trend_df = df_filtered.groupby("Tanggal")["Luas_Deforestasi_Ha"].sum().reset_index()
        fig_trend = px.line(
            trend_df, x="Tanggal", y="Luas_Deforestasi_Ha",
            labels={"Luas_Deforestasi_Ha": "Luas Area (Ha)", "Tanggal": "Tanggal"},
            template="plotly_white", markers=True
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with col_t2:
        st.markdown("##### Proporsi Faktor Pemicu Utama (Drivers)")
        driver_df = df_filtered.groupby("Faktor_Pemicu")["Luas_Deforestasi_Ha"].sum().reset_index()
        fig_driver = px.bar(
            driver_df, x="Faktor_Pemicu", y="Luas_Deforestasi_Ha", color="Faktor_Pemicu",
            labels={"Luas_Deforestasi_Ha": "Total Luas (Ha)", "Faktor_Pemicu": "Pemicu"},
            template="plotly_white"
        )
        st.plotly_chart(fig_driver, use_container_width=True)

with tab2:
    st.markdown("##### Sebaran Titik Koordinat Peringatan Deforestasi (Spatial Scatter)")
    fig_map = px.scatter(
        df_filtered, x="Longitude", y="Latitude", color="Provinsi",
        size="Luas_Deforestasi_Ha", hover_data=["Faktor_Pemicu", "Tingkat_Keyakinan_AI"],
        template="plotly_white", title="Peta Sebaran Titik Panas & Gangguan Hutan"
    )
    st.plotly_chart(fig_map, use_container_width=True)

with tab3:
    st.markdown("##### Distribusi Tingkat Keyakinan Model AI (*Confidence Score*)")
    fig_box = px.box(
        df_filtered, x="Faktor_Pemicu", y="Tingkat_Keyakinan_AI", color="Faktor_Pemicu",
        template="plotly_white", title="Tingkat Kepercayaan Model per Kategori Pemicu"
    )
    st.plotly_chart(fig_box, use_container_width=True)

st.divider()

with st.expander("📋 Klik untuk Membaca Rincian Data Mentah (Details-on-Demand)"):
    st.write(f"Menampilkan {len(df_filtered)} baris data sesuai dengan filter yang aktif:")
    
    search_query = st.text_input("🔍 Cari berdasarkan kata kunci Provinsi atau Pemicu:")
    if search_query:
        mask = df_filtered.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        df_display = df_filtered[mask]
    else:
        df_display = df_filtered
        
    st.dataframe(df_display.sort_values(by="Tanggal", ascending=False), use_container_width=True)
    
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Unduh Data Hasil Filter (.csv)",
        data=csv_data,
        file_name="laporan_deforestasi_filtered.csv",
        mime="text/csv"
    )