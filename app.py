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

# Dummy yard blocks
yard_blocks = [f"{letter}{str(num).zfill(2)}" for letter in "ABC" for num in range(1, 9)]
slots_per_block = 37
containers_per_slot = 30

# Function: Allocate yard
def allocate_yard(kapal_df, yard_blocks, slots_per_block, containers_per_slot):
    allocation = []
    used_blocks = set()
    
    for _, row in kapal_df.iterrows():
        nama_kapal = row["Nama Kapal"]
        total_container = row["Jumlah Container"]
        eta = row["ETA"]
        
        # Calculate clusters needed
        cluster_size = slots_per_block * containers_per_slot
        num_clusters = -(-total_container // cluster_size)  # Ceiling division
        containers_left = total_container
        
        for cluster in range(num_clusters):
            # Find an available block (not adjacent and not already used for same ETA)
            available_blocks = [block for block in yard_blocks if block not in used_blocks]
            chosen_block = random.choice(available_blocks)  # Random block allocation
            
            # Allocate containers to this cluster
            containers_in_cluster = min(containers_left, cluster_size)
            allocation.append({
                "Nama Kapal": nama_kapal,
                "Block": chosen_block,
                "Cluster": cluster + 1,
                "Jumlah Container": containers_in_cluster,
                "ETA": eta
            })
            containers_left -= containers_in_cluster
            used_blocks.add(chosen_block)
    
    return pd.DataFrame(allocation)

# Function: Visualize yard
def visualize_yard(allocation, yard_blocks):
    block_rows = {"A": 0, "B": 1, "C": 2}  # Row positions for blocks
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.set_xlim(0, 8)
    ax.set_ylim(-1, 3)

    # Block layout
    for block in yard_blocks:
        block_letter = block[0]
        block_number = int(block[1:])
        row = block_rows[block_letter]
        col = block_number - 1
        ax.add_patch(plt.Rectangle((col, row), 1, 1, edgecolor='black', facecolor='none'))
        ax.text(col + 0.5, row + 0.5, block, ha='center', va='center', fontsize=8, weight='bold')

    # Assign colors for each kapal
    kapal_colors = {nama: f'#{random.randint(0, 0xFFFFFF):06x}' for nama in allocation["Nama Kapal"].unique()}

    # Fill blocks with clusters
    for _, row in allocation.iterrows():
        block = row["Block"]
        block_letter = block[0]
        block_number = int(block[1:])
        block_row = block_rows[block_letter]
        block_col = block_number - 1
        color = kapal_colors[row["Nama Kapal"]]
        ax.add_patch(plt.Rectangle((block_col, block_row), 1, 1, edgecolor='black', facecolor=color))
        ax.text(block_col + 0.5, block_row + 0.5, f"{row['Nama Kapal']}\n{row['Jumlah Container']} Cont.", 
                ha='center', va='center', fontsize=7, color='white')

    # Legend
    legend_patches = [mpatches.Patch(color=color, label=nama) for nama, color in kapal_colors.items()]
    ax.legend(handles=legend_patches, loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=5, fontsize=8)

    ax.axis('off')
    plt.tight_layout()
    return fig

# Streamlit App
st.title("Container Yard Allocation")

# Input kapal data
st.subheader("Input Kapal Data")
kapal_df = pd.DataFrame(kapal_data)
st.write(kapal_df)

# Alokasi otomatis
yard_allocation = allocate_yard(kapal_df, yard_blocks, slots_per_block, containers_per_slot)
st.subheader("Hasil Alokasi")
st.write(yard_allocation)

# Visualisasi yard
st.subheader("Visualisasi Yard")
fig = visualize_yard(yard_allocation, yard_blocks)
st.pyplot(fig)
