import streamlit as st
import pandas as pd
import numpy as np

# Membuat template dengan format vertikal sesuai gambar
sections = ['A', 'B', 'C']
rows_per_section = 4
columns_per_section = 37

# Membuat grid kosong
yard_matrix = np.empty((rows_per_section, columns_per_section * len(sections)), dtype=object)

# Mengisi dengan label sesuai format vertikal
for i, section in enumerate(sections):
    for j in range(rows_per_section):
        yard_matrix[j, i * columns_per_section] = f"{section}{str(j+1).zfill(2)}"

# Membuat DataFrame
df_yard_vertical = pd.DataFrame(yard_matrix)

# Streamlit UI
st.title("Yard Template Viewer")
st.write("Template dengan format vertikal untuk yard management.")

# Menampilkan DataFrame di Streamlit
st.dataframe(df_yard_vertical, use_container_width=True)