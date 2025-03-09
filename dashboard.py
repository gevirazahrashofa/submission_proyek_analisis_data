import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
hour_df = pd.read_csv("hour.csv")
day_df = pd.read_csv("day.csv")

# Data cleaning
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
day_df["dteday"] = pd.to_datetime(day_df["dteday"])

# Streamlit app
st.title("Analisis Data Bike Sharing Dataset")

# Pertanyaan 1: Pola penggunaan sepeda berdasarkan musim
st.header("Pola Penggunaan Sepeda Berdasarkan Musim")
season_usage = day_df.groupby("season")["cnt"].mean()
fig1, ax1 = plt.subplots(figsize=(8, 5))
season_usage.plot(kind='bar', color=['blue', 'green', 'orange', 'red'], ax=ax1)
ax1.set_title("Rata-rata Penggunaan Sepeda Berdasarkan Musim")
ax1.set_xlabel("Musim (1: Semi, 2: Panas, 3: Gugur, 4: Dingin)")
ax1.set_ylabel("Rata-rata Jumlah Peminjaman")
ax1.tick_params(axis='x', rotation=0)
st.pyplot(fig1)
st.write("Penggunaan sepeda bervariasi tergantung musim. Peminjaman tertinggi terjadi pada musim gugur, diikuti oleh musim panas dan dingin, sementara musim semi memiliki tingkat peminjaman terendah.")

# Pertanyaan 2: Tingkat penyewaan sepeda tertinggi dan terendah berdasarkan jam
st.header("Tingkat Penyewaan Sepeda Berdasarkan Jam")
hourly_rentals = hour_df.groupby("hr")["cnt"].mean()
peak_hour = hourly_rentals.idxmax()
lowest_hour = hourly_rentals.idxmin()
fig2, ax2 = plt.subplots(figsize=(10, 5))
hourly_rentals.plot(kind='line', marker='o', color='b', linestyle='-', ax=ax2)
ax2.axvline(peak_hour, color='r', linestyle='--', label=f'Puncak ({peak_hour}:00)')
ax2.axvline(lowest_hour, color='g', linestyle='--', label=f'Terendah ({lowest_hour}:00)')
ax2.set_title("Pola Penyewaan Sepeda Berdasarkan Jam")
ax2.set_xlabel("Jam")
ax2.set_ylabel("Rata-rata Jumlah Peminjaman")
ax2.set_xticks(range(0, 24))
ax2.legend()
ax2.grid(alpha=0.5)
st.pyplot(fig2)
st.write(f"Penyewaan sepeda mencapai puncaknya pada pukul {peak_hour}:00, sementara peminjaman terendah terjadi pada pukul {lowest_hour}:00.")

# Pertanyaan 3: Pengaruh kondisi cuaca terhadap jumlah peminjaman sepeda
st.header("Pengaruh Kondisi Cuaca terhadap Peminjaman Sepeda")
weather_rentals = hour_df.groupby("weathersit")["cnt"].mean()
fig3, ax3 = plt.subplots(figsize=(8, 5))
sns.barplot(x=weather_rentals.index, y=weather_rentals.values, palette="Blues", ax=ax3)
ax3.set_xlabel("Kondisi Cuaca")
ax3.set_ylabel("Rata-rata Jumlah Peminjaman")
ax3.set_title("Pengaruh Kondisi Cuaca terhadap Peminjaman Sepeda")
ax3.set_xticks(ticks=[0, 1, 2, 3], labels=["Cerah", "Mendung", "Hujan Ringan", "Hujan Lebat"])
ax3.grid(alpha=0.5)
st.pyplot(fig3)
st.write("Cuaca sangat memengaruhi jumlah peminjaman sepeda. Saat cuaca cerah, peminjaman tertinggi, tetapi semakin menurun saat mendung, hujan ringan, dan mencapai titik terendah saat hujan lebat.")

# Kesimpulan
st.header("Kesimpulan")
st.write("""
* Penggunaan sepeda bervariasi tergantung musim. Peminjaman tertinggi terjadi pada musim gugur, diikuti oleh musim panas dan dingin, sementara musim semi memiliki tingkat peminjaman terendah.
* Penyewaan sepeda mencapai puncaknya pada pukul 17:00 (jam sibuk sore), sementara peminjaman terendah terjadi pada pukul 04:00 dini hari.
* Cuaca sangat memengaruhi jumlah peminjaman sepeda. Saat cuaca cerah, peminjaman tertinggi, tetapi semakin menurun saat mendung, hujan ringan, dan mencapai titik terendah saat hujan lebat.
""")