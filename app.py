import streamlit as st
import matplotlib.pyplot as plt

# Parameter grid
sections = ['A', 'B', 'C']
rows_per_section = 4
columns_per_section = 37
gap_size = 3  # Jumlah kolom kosong sebagai pemisah
dock_labels = ["NP1", "NP2", "NP3"]
dock_height = 1  # Tinggi dermaga di bawah grid
total_columns_with_gaps = (columns_per_section + gap_size) * len(sections) - gap_size
total_height = rows_per_section + dock_height

# Membuat figure untuk plot dengan dermaga
fig, ax = plt.subplots(figsize=(total_columns_with_gaps * 0.2, total_height * 0.8))

# Membuat grid dan label untuk Yard Blocks
for i, section in enumerate(sections):
    for j in range(rows_per_section):
        row_label = f"{section}{str(j+1).zfill(2)}"
        x_offset = i * (columns_per_section + gap_size)  # Offset per section dengan gap

        # Menggambar slot di dalam section
        for k in range(columns_per_section):
            rect = plt.Rectangle((x_offset + k, total_height - j - 2), 1, 1,
                                 edgecolor='black', facecolor='white', linewidth=1)
            ax.add_patch(rect)

        # Menampilkan label di awal setiap baris
        ax.text(x_offset - 0.5, total_height - j - 1.5, row_label,
                va='center', ha='right', fontsize=10, fontweight='bold')

# Menambahkan visualisasi dermaga di bawah Yard Blocks
for i, dock_label in enumerate(dock_labels):
    x_offset = i * (columns_per_section + gap_size)  # Offset per dock

    # Gambar dermaga sebagai blok tebal
    rect = plt.Rectangle((x_offset, 0), columns_per_section, dock_height,
                         edgecolor='black', facecolor='lightgray', linewidth=2)
    ax.add_patch(rect)

    # Menambahkan label dermaga di tengahnya
    ax.text(x_offset + columns_per_section / 2, dock_height / 2, dock_label,
            va='center', ha='center', fontsize=12, fontweight='bold')

# Set batas plot
ax.set_xlim(-1, total_columns_with_gaps)
ax.set_ylim(0, total_height)

# Hilangkan axis
ax.set_xticks([])
ax.set_yticks([])
ax.set_frame_on(False)

# Streamlit UI
st.title("Yard Grid with Dock Visualization")
st.write("Visualisasi yard grid dengan dermaga untuk kapal sandar.")

# Menampilkan gambar di Streamlit
st.pyplot(fig)