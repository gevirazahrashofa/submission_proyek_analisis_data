import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Konfigurasi halaman
st.set_page_config(
    page_title="Analisis Bike Sharing",
    page_icon="🚲",
    layout="wide"
)

hour_df = pd.read_csv('hour.csv')
day_df = pd.read_csv('day.csv')

if hour_df is not None and day_df is not None:
    # Membersihkan data
    hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
    day_df["dteday"] = pd.to_datetime(day_df["dteday"])
    
    # Judul dashboard dengan gaya
    st.title("🚲 Analisis Data Bike Sharing")
    st.markdown("### Proyek oleh: Gevira Zahra Shofa")
    
    # Filter di sidebar
    st.sidebar.header("Filter Data")
    
    start_date = st.sidebar.date_input("Tanggal Mulai", day_df["dteday"].min().date())
    end_date = st.sidebar.date_input("Tanggal Akhir", day_df["dteday"].max().date())
    
    # Pemetaan musim dan cuaca dari notebook
    season_mapping = {1: "Semi", 2: "Panas", 3: "Gugur", 4: "Dingin"}
    weather_mapping = {1: "Cerah", 2: "Mendung", 3: "Hujan Ringan", 4: "Hujan Lebat"}
    
    selected_season = st.sidebar.multiselect("Pilih Musim", options=list(season_mapping.values()), default=list(season_mapping.values()))
    selected_hours = st.sidebar.slider("Pilih Rentang Jam", 0, 23, (0, 23))
    selected_weather = st.sidebar.multiselect("Pilih Kondisi Cuaca", options=list(weather_mapping.values()), default=list(weather_mapping.values()))
    
    # Membuat pemetaan terbalik untuk filtering
    reverse_season_mapping = {v: k for k, v in season_mapping.items()}
    reverse_weather_mapping = {v: k for k, v in weather_mapping.items()}
    
    # Mengatasi kasus ketika tidak ada musim atau cuaca yang dipilih
    if not selected_season:
        st.warning("Silakan pilih minimal satu musim untuk melihat data")
        season_ids = []
    else:
        season_ids = [reverse_season_mapping[s] for s in selected_season]
        
    if not selected_weather:
        st.warning("Silakan pilih minimal satu kondisi cuaca untuk melihat data")
        weather_ids = []
    else:
        weather_ids = [reverse_weather_mapping[w] for w in selected_weather]
    
    # Filter data
    if season_ids and weather_ids:
        day_filtered = day_df[
            (day_df["dteday"] >= pd.Timestamp(start_date)) & 
            (day_df["dteday"] <= pd.Timestamp(end_date)) &
            (day_df["season"].isin(season_ids))
        ]
        
        hour_filtered = hour_df[
            (hour_df["dteday"] >= pd.Timestamp(start_date)) &
            (hour_df["dteday"] <= pd.Timestamp(end_date)) &
            (hour_df["hr"] >= selected_hours[0]) &
            (hour_df["hr"] <= selected_hours[1]) &
            (hour_df["weathersit"].isin(weather_ids))
        ]
        
        # Menampilkan metrik data
        st.markdown("## Ringkasan Data")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Hari", f"{day_filtered.shape[0]}")
        
        with col2:
            st.metric("Total Peminjaman", f"{day_filtered['cnt'].sum():,}")
        
        with col3:
            st.metric("Rata-rata Peminjaman/Hari", f"{day_filtered['cnt'].mean():.1f}")
        
        # Menampilkan jawaban untuk pertanyaan bisnis
        tab1, tab2, tab3 = st.tabs(["Pola Berdasarkan Musim", "Pola Berdasarkan Jam", "Pengaruh Cuaca"])
        
        # Tab 1: Pola penggunaan sepeda berdasarkan musim
        with tab1:
            st.header("Bagaimana pola penggunaan sepeda berdasarkan musim?")
            
            if selected_season:  # Hanya tampilkan grafik jika ada musim yang dipilih
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Perhitungan rata-rata penggunaan berdasarkan musim
                    valid_seasons = [s for s in range(1, 5) if s in season_ids]
                    if valid_seasons:
                        season_usage = day_filtered.groupby("season")["cnt"].mean().reindex(valid_seasons)
                        
                        if not season_usage.empty:
                            # Visualisasi dari notebook
                            colors = ['#ADD8E6' if cnt < max(season_usage) else '#1E90FF' for cnt in season_usage]
                            
                            fig, ax = plt.subplots(figsize=(10, 6))
                            season_usage.plot(kind='bar', color=colors, ax=ax)
                            ax.set_title("Rata-rata Penggunaan Sepeda Berdasarkan Musim", fontsize=14)
                            ax.set_xlabel("Musim", fontsize=12)
                            ax.set_ylabel("Rata-rata Jumlah Peminjaman", fontsize=12)
                            ax.set_xticklabels([season_mapping[s] for s in season_usage.index], rotation=0)
                            ax.grid(axis="y", linestyle="--", alpha=0.7)
                            
                            for i, v in enumerate(season_usage):
                                ax.text(i, v + 50, f"{v:.1f}", ha='center', fontweight='bold')
                                
                            st.pyplot(fig)
                
                with col2:
                    st.info("""
                    **Insight:**
                    - Penggunaan sepeda tertinggi pada musim **Gugur**
                    - Musim **Panas** juga memiliki peminjaman tinggi
                    - Peminjaman terendah terjadi pada musim **Semi**
                    - Pengaruh musim menunjukkan preferensi pengguna terhadap cuaca yang lebih hangat namun tidak terlalu panas
                    """)
            else:
                st.info("Pilih minimal satu musim untuk melihat visualisasi")
        
        # Tab 2: Pola penyewaan berdasarkan jam
        with tab2:
            st.header("Pada jam berapa tingkat penyewaan sepeda mencapai puncaknya dan kapan terendah?")
            
            if not hour_filtered.empty:  # Hanya tampilkan jika ada data
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Visualisasi peminjaman per jam
                    try:
                        hourly_rentals = hour_filtered.groupby("hr")["cnt"].mean()
                        
                        # Mencari jam puncak dan terendah
                        if not hourly_rentals.empty:
                            peak_hour = hourly_rentals.idxmax()
                            lowest_hour = hourly_rentals.idxmin()
                            
                            fig, ax = plt.subplots(figsize=(12, 6))
                            hourly_rentals.plot(kind='line', marker='o', color='b', linestyle='-', ax=ax)
                            
                            # Tambahkan garis vertikal untuk jam puncak dan terendah
                            ax.axvline(peak_hour, color='r', linestyle='--', label=f'Puncak ({peak_hour}:00)')
                            ax.axvline(lowest_hour, color='g', linestyle='--', label=f'Terendah ({lowest_hour}:00)')
                            
                            ax.set_title("Pola Penyewaan Sepeda Berdasarkan Jam", fontsize=14)
                            ax.set_xlabel("Jam", fontsize=12)
                            ax.set_ylabel("Rata-rata Jumlah Peminjaman", fontsize=12)
                            ax.set_xticks(range(0, 24))
                            ax.legend()
                            ax.grid(alpha=0.5)
                            
                            # Tambahkan label nilai untuk titik puncak dan terendah
                            ax.text(peak_hour, hourly_rentals[peak_hour] + 10, 
                                    f"{hourly_rentals[peak_hour]:.1f}", 
                                    ha='center', color='red', fontweight='bold')
                            ax.text(lowest_hour, hourly_rentals[lowest_hour] + 10, 
                                    f"{hourly_rentals[lowest_hour]:.1f}", 
                                    ha='center', color='green', fontweight='bold')
                            
                            st.pyplot(fig)
                    except:
                        st.warning("Tidak bisa menghasilkan grafik dengan filter yang dipilih. Coba ubah filter.")
                
                with col2:
                    if not hourly_rentals.empty:
                        st.info(f"""
                        **Insight:**
                        - **Jam puncak**: {peak_hour}:00 dengan rata-rata {hourly_rentals[peak_hour]:.1f} peminjaman
                        - **Jam terendah**: {lowest_hour}:00 dengan rata-rata {hourly_rentals[lowest_hour]:.1f} peminjaman
                        - Lonjakan pagi terjadi sekitar pukul 7-8 (jam berangkat kerja/sekolah)
                        - Lonjakan sore terjadi sekitar pukul 17-18 (jam pulang kerja)
                        - Peminjaman paling sedikit terjadi pada dini hari
                        """)
            else:
                st.info("Tidak ada data untuk rentang jam atau filter yang dipilih")
        
        # Tab 3: Pengaruh cuaca terhadap peminjaman sepeda
        with tab3:
            st.header("Bagaimana pengaruh kondisi cuaca terhadap jumlah peminjaman sepeda?")
            
            if selected_weather and not hour_filtered.empty:  # Hanya tampilkan jika ada cuaca dipilih
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    try:
                        # Visualisasi pengaruh cuaca
                        weather_rentals = hour_filtered.groupby("weathersit")["cnt"].mean()
                        
                        if not weather_rentals.empty:
                            # Tentukan warna
                            colors = ['#ADD8E6' if cnt < max(weather_rentals) else '#1E90FF' for cnt in weather_rentals]
                            
                            fig, ax = plt.subplots(figsize=(12, 8))
                            sns.barplot(x=weather_rentals.index, y=weather_rentals.values, palette=colors, ax=ax)
                            ax.set_title("Pengaruh Kondisi Cuaca terhadap Peminjaman Sepeda", fontsize=14)
                            ax.set_xlabel("Kondisi Cuaca", fontsize=12)
                            ax.set_ylabel("Rata-rata Jumlah Peminjaman", fontsize=12)
                            
                            # Set label untuk kondisi cuaca
                            weather_labels = ["Cerah", "Mendung", "Hujan Ringan", "Hujan Lebat"]
                            ax.set_xticks(range(len(weather_rentals)))
                            ax.set_xticklabels([weather_labels[i-1] for i in weather_rentals.index])
                            ax.grid(axis="y", linestyle="--", alpha=0.7)
                            
                            # Tambahkan label nilai
                            for i, v in enumerate(weather_rentals):
                                ax.text(i, v + 5, f"{v:.1f}", ha='center', fontweight='bold')
                            
                            st.pyplot(fig)
                            
                            # Tambahkan analisis clustering/binning seperti di notebook
                            st.subheader("Kategori Peminjaman Berdasarkan Kondisi Cuaca")
                            
                            # Fungsi untuk mengkategorikan peminjaman
                            def kategorikan_peminjaman(nilai):
                                if nilai > 180:
                                    return "Tinggi"
                                elif 120 < nilai <= 180:
                                    return "Sedang"
                                else:
                                    return "Rendah"
                            
                            # Buat DataFrame untuk kategori
                            weather_categories = pd.DataFrame({
                                'Kondisi Cuaca': [weather_labels[i-1] for i in weather_rentals.index],
                                'Rata-rata Peminjaman': weather_rentals.values,
                                'Kategori': [kategorikan_peminjaman(v) for v in weather_rentals.values]
                            })
                            
                            # Tampilkan sebagai tabel dengan gaya
                            st.dataframe(
                                weather_categories.style.apply(
                                    lambda x: ['background-color: #1E90FF; color: black' if v == 'Tinggi' 
                                            else 'background-color: #ADD8E6; color: black' if v == 'Sedang' 
                                            else 'background-color: #F8F9FA; color: black' 
                                            for v in x],
                                    subset=['Kategori']
                                ),
                                hide_index=True
                            )
                    except:
                        st.warning("Tidak bisa menghasilkan grafik dengan filter yang dipilih. Coba ubah filter.")
                
                with col2:
                    st.info("""
                    **Insight:**
                    - Jumlah peminjaman **tertinggi** terjadi saat cuaca **cerah**
                    - Terjadi penurunan peminjaman seiring memburuknya kondisi cuaca
                    - Peminjaman **terendah** terjadi saat **hujan lebat**
                    - Cuaca mendung masih cukup diminati, tidak jauh berbeda dari cuaca cerah
                    - Cuaca buruk, terutama hujan, menyebabkan penurunan signifikan pada peminjaman sepeda
                """)
    
    # Conclusions section
    st.header("Kesimpulan")
    st.markdown("""
    1. **Pola penggunaan sepeda berdasarkan musim**
       - Penggunaan sepeda menunjukkan perbedaan signifikan di setiap musim
       - Musim gugur memiliki tingkat peminjaman tertinggi, diikuti musim panas
       - Musim semi memiliki peminjaman terendah, kemungkinan karena cuaca yang kurang mendukung
    
    2. **Pola peminjaman berdasarkan jam**
       - Peminjaman mencapai puncak pada jam sibuk (pagi dan sore hari)
       - Peminjaman terendah terjadi pada dini hari (03:00-05:00)
       - Pola ini menunjukkan sepeda banyak digunakan sebagai transportasi harian
    
    3. **Pengaruh cuaca terhadap peminjaman**
       - Cuaca cerah mendorong peminjaman tertinggi
       - Hujan menyebabkan penurunan signifikan dalam peminjaman
       - Kondisi cuaca sangat memengaruhi keputusan pengguna untuk bersepeda
    
    **Rekomendasi Bisnis:**
    - Menyediakan lebih banyak sepeda pada musim gugur dan panas serta pada jam sibuk
    - Mengadakan promosi khusus saat musim dingin dan semi untuk meningkatkan peminjaman
    - Menyediakan perlengkapan tambahan (jas hujan) saat cuaca buruk untuk mempertahankan pengguna
    """)
else:
    st.error("Tidak dapat memuat data. Pastikan file data tersedia di lokasi yang benar.")
