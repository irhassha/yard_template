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
    fig, ax = plt.subplots(figsize=(len(yard_blocks) * 2, slots_per_block // 4))

    # Get unique blocks and their positions
    block_positions = {block: idx for idx, block in enumerate(yard_blocks)}

    # Draw grid for each block and slot
    for block, idx in block_positions.items():
        for slot in range(slots_per_block):
            x = idx
            y = slots_per_block - slot - 1  # Invert y-axis for slot numbering
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
        x = block_positions[block]
        y = slots_per_block - slot - 1
        ax.add_patch(plt.Rectangle((x, y), 1, 1, edgecolor='black', facecolor=color))
        ax.text(x + 0.5, y + 0.5, f"{jumlah_container}", ha='center', va='center', fontsize=6, color='white')

    # Format plot
    ax.set_xlim(-0.5, len(yard_blocks) - 0.5)
    ax.set_ylim(-0.5, slots_per_block)
    ax.set_xticks(range(len(yard_blocks)))
    ax.set_xticklabels(yard_blocks, fontsize=8, rotation=90)
    ax.set_yticks(range(slots_per_block))
    ax.set_yticklabels(range(1, slots_per_block + 1), fontsize=8)
    ax.invert_yaxis()
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
