import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import random

# Dummy data kapal
kapal_data = [
    {"Nama Kapal": "Kapal A", "Jumlah Container": 900, "ETA": "2025-01-25"},
    {"Nama Kapal": "Kapal B", "Jumlah Container": 600, "ETA": "2025-01-25"},
    {"Nama Kapal": "Kapal C", "Jumlah Container": 1200, "ETA": "2025-01-26"},
    {"Nama Kapal": "Kapal D", "Jumlah Container": 300, "ETA": "2025-01-26"},
    {"Nama Kapal": "Kapal E", "Jumlah Container": 1500, "ETA": "2025-01-27"}
]

# Dummy yard blocks (rows: C, B, A; columns: 1 to 5)
yard_blocks = [f"{letter}{num}" for letter in "CBA" for num in range(1, 6)]
slots_per_block = 37  # Total slots per block
containers_per_slot = 30  # Max containers per slot

# Allocate yard function
def allocate_yard(kapal_df, yard_blocks, slots_per_block, containers_per_slot):
    allocation = []
    used_slots = {block: [False] * slots_per_block for block in yard_blocks}
    
    for _, row in kapal_df.iterrows():
        nama_kapal = row["Nama Kapal"]
        total_container = row["Jumlah Container"]
        eta = row["ETA"]
        
        containers_left = total_container
        for block in yard_blocks:
            for slot in range(slots_per_block):
                if not used_slots[block][slot] and containers_left > 0:
                    containers_in_slot = min(containers_left, containers_per_slot)
                    allocation.append({
                        "Nama Kapal": nama_kapal,
                        "Block": block,
                        "Slot": slot + 1,
                        "Jumlah Container": containers_in_slot,
                        "ETA": eta
                    })
                    used_slots[block][slot] = True
                    containers_left -= containers_in_slot
                if containers_left <= 0:
                    break
            if containers_left <= 0:
                break
    return pd.DataFrame(allocation)

# Visualization function
def visualize_yard(allocation, yard_blocks, slots_per_block):
    fig, ax = plt.subplots(figsize=(20, 10))

    # Block positions grouped by rows (A, B, C)
    rows = {"A": 2, "B": 1, "C": 0}  # Define rows for each block group
    blocks_per_row = len(set([block[1:] for block in yard_blocks]))  # Number of blocks per row
    block_positions = {block: (int(block[1:]) - 1, rows[block[0]]) for block in yard_blocks}

    # Draw grid for each block and slot
    for block, (col, row) in block_positions.items():
        for slot in range(slots_per_block):
            x = col * (slots_per_block + 2) + slot
            y = row * 3  # Add spacing between rows
            ax.add_patch(plt.Rectangle((x, y), 1, 1, edgecolor='black', facecolor='white'))
            ax.text(x + 0.5, y + 0.5, str(slot + 1), ha='center', va='center', fontsize=6, color='black')

    # Assign colors for each kapal
    kapal_colors = {nama: f'#{random.randint(0, 0xFFFFFF):06x}' for nama in allocation["Nama Kapal"].unique()}

    # Fill slots with allocation data
    for _, row in allocation.iterrows():
        block = row["Block"]
        slot = row["Slot"] - 1
        jumlah_container = row["Jumlah Container"]
        nama_kapal = row["Nama Kapal"]
        color = kapal_colors[nama_kapal]
        col, r = block_positions[block]
        x = col * (slots_per_block + 2) + slot
        y = r * 3
        ax.add_patch(plt.Rectangle((x, y), 1, 1, edgecolor='black', facecolor=color))
        ax.text(x + 0.5, y + 0.5, f"{jumlah_container}", ha='center', va='center', fontsize=6, color='white')

    # Format plot
    ax.set_xlim(-1, blocks_per_row * (slots_per_block + 2))
    ax.set_ylim(-1, len(rows) * 3)
    ax.axis('off')

    # Add legend
    legend_patches = [mpatches.Patch(color=color, label=nama) for nama, color in kapal_colors.items()]
    ax.legend(handles=legend_patches, loc='upper right', bbox_to_anchor=(1.2, 1), fontsize=8)
    return fig

# Streamlit App
st.set_page_config(layout="wide")
st.title("Detailed Container Yard Allocation")

# Input data kapal
st.subheader("Input Kapal Data")
kapal_df = pd.DataFrame(kapal_data)
st.write(kapal_df)

# Alokasi otomatis
st.subheader("Hasil Alokasi")
yard_allocation = allocate_yard(kapal_df, yard_blocks, slots_per_block, containers_per_slot)
st.write(yard_allocation)

# Visualisasi Yard
st.subheader("Visualisasi Yard")
fig = visualize_yard(yard_allocation, yard_blocks, slots_per_block)
st.pyplot(fig)

# Fitur Zoom dengan Streamlit Interactive
st.write("Gunakan tombol zoom di atas visualisasi untuk memperbesar/memperkecil tampilan.")
