import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

# Load the dataset
assemble = pd.read_csv("./dashboard/assemble.csv")

if 'time' in assemble.columns:
    assemble['time'] = pd.to_datetime(assemble['time'])

st.title("Proyek Analisis Data Kualitas Ud...")

# Membuat variabel global
year_range = None
selected_options = None

# Fungsi untuk menampilkan dan menutup dialog
@st.dialog("Popup Dialog")
def my_dialog():
    st.write(
        "PM2.5: PM2.5 concentration (ug/m^3), "
        "PM10: PM10 concentration (ug/m^3), "
        "SO2: SO2 concentration (ug/m^3), "
        "NO2: NO2 concentration (ug/m^3), "
        "CO: CO concentration (ug/m^3), "
        "O3: O3 concentration (ug/m^3), "
        "TEMP: temperature (degree Celsius), "
        "PRES: pressure (hPa), "
        "DEWP: dew point temperature (degree Celsius), "
        "RAIN: precipitation (mm), "
        "wd: wind direction, "
        "WSPM: wind speed (m/s), "
        "station: name of the air-quality monitoring site"
    )

# Tombol untuk membuka dialog
if st.button("Keterangan"):
    my_dialog()

# Slide untuk memilih interval tahun
if 'time' in assemble.columns:
    min_year = assemble['time'].dt.year.min()
    max_year = assemble['time'].dt.year.max()

    year_range = st.slider(
        "Pilih rentang tahun:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )
else:
    st.write("Kolom 'time' tidak ditemukan dalam dataset.")

# Multiselect dropdown untuk pemiliham lokasi stasiun
if "station" in assemble.columns:
    unique_values = assemble["station"].unique().tolist()

    selected_options = st.multiselect(
        'Pilih stasiun:',
        unique_values,
        default=unique_values[:2] if len(unique_values) >= 2 else unique_values
    )
else:
    st.write("Kolom 'station' tidak ditemukan dalam dataset.")

# Filter data berdasarkan rentang tahun dan stasiun yang dipilih
if year_range and selected_options:
    filtered_data = assemble[
        (assemble['time'].dt.year >= year_range[0]) &
        (assemble['time'].dt.year <= year_range[1]) &
        (assemble["station"].isin(selected_options))
    ]

    st.dataframe(filtered_data)
else:
    filtered_data = pd.DataFrame()  # Kosongkan jika tidak ada filter

# Tabs for different visualizations
tab1, tab2, tab3 = st.tabs(["AQI Year by Year", "Meteorological correlation with AQI", "Average air quality per hour"])
plt.style.use('dark_background')

with tab1:
    st.header("Perubahan Rata-Rata AQI Bulanan")

    if not filtered_data.empty:
        # Hitung rata-rata AQI berdasarkan kombinasi tahun-bulan pada kolom 'time'
        monthly_avg = filtered_data.groupby(filtered_data['time'].dt.to_period('M')).median(numeric_only=True)

        # Reset index agar lebih mudah diakses
        monthly_avg.reset_index(inplace=True)

        # Ubah index dari period ke timestamp untuk visualisasi
        monthly_avg['time'] = monthly_avg['time'].dt.to_timestamp()

        # Visualisasi rata-rata line chart menggunakan Matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(monthly_avg['time'], monthly_avg['AQI'], marker='o', color='w', linestyle='-')
        ax.set_title("Perubahan Rata-Rata Bulanan AQI", fontsize=16)
        ax.set_xlabel('Waktu (Tahun - Bulan)', fontsize=12)
        ax.set_ylabel('Rata-Rata AQI', fontsize=12)
        ax.grid(alpha=0.5)
        plt.xticks(rotation=45)  # Memiringkan label x-axis agar mudah dibaca

        # Tampilkan plot di Streamlit menggunakan st.pyplot()
        st.pyplot(fig)

        st.subheader("Insight")
        st.write("**Pertanyaan 1:** Bagaimana kualitas udara di kedua lokasi dari waktu ke waktu?")
        st.write(
            "Visualisasi ini menunjukan downtrend di kedua lokasi terjadi lower high dan lower low, "
            "menunjukan terdapat langkah yang baik bagi masyarakat disekatar stasiun tersebut "
            "meskipun bisa dibilang nilai all time low 2014 masih terbilang nilai AQI yang sedang, "
            "gak baik baik banget dan gak buruk buruk banget. All time high menunjukkan angka "
            "disekitar 180 pada tahun 2016 ini cukup tinggi. Saat saya serching buruknya nilai AQI "
            "di tahun 2014 dan baiknya AQI pada tahun 2016 di beijing ini cukup masuk akal karena info "
            "yang saya dapat benar bahwa 2014 cukup parah nilai AQI nya dan 2016 nya juga tercatat "
            "memang benar memang terkenal rendah. Dari info info ini bisa disimpulkan bahwa masyarat di "
            "tahun 2014 mendapatkan dampak dari AQI yang tinggi ini mulai kapok hingga pada tahun "
            "2016 terjadi langkah langkah yang baik bagi penurunan AQI."
        )
    else:
        st.write("Tidak ada data yang sesuai dengan filter.")

with tab2:
    st.header("Korelasi Meteorologi dengan AQI")

    METEOROLOGIES = ["TEMP", "PRES", "DEWP", "RAIN", "WSPM", "AQI"]  # AQI tidak termasuk

    if not filtered_data.empty:
        # Menghitung korelasi antara variabel target (AQI) dan semua variabel lainnya
        corr_matrix = filtered_data[METEOROLOGIES].corr()
        target_corr = corr_matrix['AQI'].drop('AQI')

        # Membuat plot bar menggunakan Matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        target_corr.plot(kind='bar', ax=ax, color='w', edgecolor='black')
        ax.set_title('Korelasi dengan AQI', fontsize=16)
        ax.set_xlabel('Variabel', fontsize=12)
        ax.set_ylabel('Koefisien Korelasi', fontsize=12)
        ax.grid(axis='y', alpha=0.5)

        # Tampilkan plot di Streamlit
        st.pyplot(fig)

        st.subheader("Insight")
        st.write("**Pertanyaan 2:** Apakah meteorologi berpengaruh terhadap buruknya kualitas udara?")
        st.write(
            "Diantara kelimat tersebut WSPM adalah fitur meteorologi dengan korelasi tertinggi menunjukan "
            "angka disekitaran -0.15. Ini cukup masuk akal karena WSPM merepresentasikan kecepatan udara "
            "dapat menyebarluaskan udara kotor yang terfokus ke satu lokasi saja menyebar ke beberapa "
            "lokasi menyebabkan nilai AQI menurun seiring naiknya nilai WSPM. Fitur dengan nilai korelasi "
            "kedua tertinggi adalah DEWP lagi lagi ini cukup masuk akal karena DEWP atau titik embun "
            "jika nilainya naik dapat mengurangi radiasi matahari yang diperlukan untuk reaksi fotokimia pembentukan ozon"
            "Untuk fitur meteorologi seperti rain menunjukan korelasi negatif, press korelasi negatif "
            "dan temp berkorelasi negatif, masuk akal."
        )
    else:
        st.write("Tidak ada data yang sesuai dengan filter.")


with tab3:
    st.header("Rata-Rata AQI Berdasarkan Jam")

    if not filtered_data.empty:
        # Ekstrak jam dari kolom waktu
        filtered_data["hour"] = filtered_data['time'].dt.hour

        # Hitung rata-rata AQI berdasarkan jam
        hour_avg = filtered_data.groupby('hour')['AQI'].median().reset_index()

        # Visualisasi rata-rata AQI per jam menggunakan Matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(hour_avg['hour'], hour_avg['AQI'], marker='o', color='w', linestyle='-')
        ax.set_title('Rata-Rata AQI Berdasarkan Jam', fontsize=16)
        ax.set_xlabel('Jam (0-23)', fontsize=12)
        ax.set_ylabel('Rata-Rata AQI', fontsize=12)
        ax.grid(alpha=0.5)
        plt.xticks(range(0, 24))  # Pastikan sumbu x mencakup semua jam (0-23)

        # Tampilkan plot di Streamlit
        st.pyplot(fig)

        # Hapus kolom 'hour' untuk menjaga kebersihan data
        filtered_data.drop(columns='hour', inplace=True)

        st.subheader("Insight")
        st.write(""
            "**Pertanyaan 3:** - Apakah aktivitas manusia berpengaruh terhadap buruk atau baiknya kualitas "
            "udara (8am - 9pm (src: Sistem 896 di perusahaan China))?"
        )
        st.write(
            "Titik terendah AQI menunjukan angka disekitar 70 pada jam 06:00 sebelum nilainya naik. "
            "Titik tertinggi AQI menunjukan angka disekitar 100 pada jam 19:00 sebelum nilainya turun. "
            "Ini menunjukkan bahwa aktivitas manusia berpengaruh terhadap tinggi atau rendahnya"
            "nilai AQI. Dikarenakan aktivitas manusia diluar ruangan secara umum dimulai pada pagi hari "
            "dan pulang ke rumah pada malam hari didukung dengan metode 896 di China yang menurut sistem "
            "tersebut beberapa perusahaan mengharuskan pekerja memulai pekerjaan pada jam 08:00 hingga "
            "hingga jam 19:00. Seperti yang anda lihat pada jam 06:00 nilai AQI mulai naik menunjukkan aktivitas "
            "manusia dimulai seperti transportasi bensin, udara pabrik, dsb. Dan terus naik pada jam 19:00 "
            "kemungkinan mayoritas manusia sedang dalam perjalanan pulang sebelum jam 19:00 hingga pada "
            "19:00 kemungkinan mayoritas manusia sudah istirahat. Kesimpulannya bahwa aktivitas manusia "
            "berpengaruh."
        )

    else:
        st.write("Tidak ada data yang sesuai dengan filter.")


st.sidebar.title("Akun")

st.sidebar.text_input("Nama:", value="Mochamad Dendra Dwi Pratama Putra", disabled=True)

st.sidebar.text_input("Password:", value="jangan_liat_kocak", type="password", disabled=True)

st.sidebar.text_input("ID Dicoding:", value="@crbsdndr", disabled=True)

st.sidebar.text_input("Kelas:", value="MS-05", disabled=True)





















