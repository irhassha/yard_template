import streamlit as st
import matplotlib.pyplot as plt

# Parameter grid
sections = ['A', 'B', 'C']
rows_per_section = 4
columns_per_section = 37
gap_size = 3  # Jumlah kolom kosong sebagai pemisah antar block
dock_labels = ["NP1", "NP2", "NP3"]
dock_height = 1  # Tinggi dermaga di bawah grid
dock_spacing = 2  # Jarak antara Yard Blocks dan Dermaga
total_columns_with_gaps = (columns_per_section + gap_size) * len(sections) - gap_size
total_height_with_spacing = rows_per_section + dock_height + dock_spacing

# Membuat figure untuk plot dengan spasi antara Yard Blocks dan Dermaga
fig, ax = plt.subplots(figsize=(total_columns_with_gaps * 0.2, total_height_with_spacing * 0.8))

# Membuat grid dan label untuk Yard Blocks
for i, section in enumerate(sections):
    for j in range(rows_per_section):
        row_label = f"{section}{str(j+1).zfill(2)}"
        x_offset = i * (columns_per_section + gap_size)  # Offset per section dengan gap

        # Menggambar slot di dalam section
        for k in range(columns_per_section):
            rect = plt.Rectangle((x_offset + k, total_height_with_spacing - j - 2 - dock_spacing), 1, 1,
                                 edgecolor='black', facecolor='white', linewidth=1)
            ax.add_patch(rect)

        # Menampilkan label di awal setiap baris
        ax.text(x_offset - 0.5, total_height_with_spacing - j - 1.5 - dock_spacing, row_label,
                va='center', ha='right', fontsize=10, fontweight='bold')

# Menambahkan visualisasi dermaga di bawah **Yard Block pertama (A01, B01, C01) dengan spasi**
for i, dock_label in enumerate(dock_labels):
    x_offset = i * (columns_per_section + gap_size)  # Offset per dock

    # Gambar dermaga sebagai blok tebal dengan jarak dari Yard Blocks
    rect = plt.Rectangle((x_offset, -dock_height), columns_per_section, dock_height,
                         edgecolor='black', facecolor='lightgray', linewidth=2)
    ax.add_patch(rect)

    # Menambahkan label dermaga di tengahnya
    ax.text(x_offset + columns_per_section / 2, -dock_height / 2, dock_label,
            va='center', ha='center', fontsize=12, fontweight='bold')

# Set batas plot
ax.set_xlim(-1, total_columns_with_gaps)
ax.set_ylim(-dock_height - 1, total_height_with_spacing)

# Hilangkan axis
ax.set_xticks([])
ax.set_yticks([])
ax.set_frame_on(False)

# Streamlit UI
st.title("Yard Grid with Spaced Dock Visualization")
st.write("Visualisasi yard grid dengan jarak antara Yard Blocks dan Dermaga untuk tampilan lebih jelas.")

# Menampilkan gambar di Streamlit
st.pyplot(fig)