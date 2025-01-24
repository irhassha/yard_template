import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
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
yard_blocks = [f"{letter}{str(num).zfill(2)}" for letter in "CBA" for num in range(1, 6)]
slots_per_block = 37
containers_per_slot = 30

# Allocate yard function
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
            # Find an available block
            available_blocks = [block for block in yard_blocks if block not in used_blocks]
            chosen_block = random.choice(available_blocks)
            
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

# Visualization function
def visualize_yard(allocation, yard_blocks):
    fig, ax = plt.subplots(figsize=(12, 6))

    # Yard layout: rows and columns
    rows = ["C", "B", "A"]
    cols = [1, 2, 3, 4, 5]
    block_positions = {block: (cols.index(int(block[1:])), rows.index(block[0])) for block in yard_blocks}

    # Draw grid
    for row in range(len(rows)):
        for col in range(len(cols)):
            x, y = col, row
            ax.add_patch(plt.Rectangle((x, y), 1, 1, edgecolor='black', facecolor='lightgray'))
            block_name = f"{rows[row]}{cols[col]}"
            ax.text(x + 0.5, y + 0.5, block_name, ha='center', va='center', fontsize=8)

    # Assign colors for each kapal
    kapal_colors = {nama: f'#{random.randint(0, 0xFFFFFF):06x}' for nama in allocation["Nama Kapal"].unique()}

    # Fill blocks with clusters
    for _, row in allocation.iterrows():
        block = row["Block"]
        x, y = block_positions[block]
        color = kapal_colors[row["Nama Kapal"]]
        ax.add_patch(plt.Rectangle((x, y), 1, 1, edgecolor='black', facecolor=color))
        ax.text(x + 0.5, y + 0.5, f"{row['Nama Kapal']}\n{row['Jumlah Container']}", 
                ha='center', va='center', fontsize=7, color='white')

    # Legend
    legend_patches = [mpatches.Patch(color=color, label=nama) for nama, color in kapal_colors.items()]
    ax.legend(handles=legend_patches, loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=5, fontsize=8)

    ax.axis('off')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    return fig

# Alokasi dan visualisasi
kapal_df = pd.DataFrame(kapal_data)
yard_allocation = allocate_yard(kapal_df, yard_blocks, slots_per_block, containers_per_slot)
fig = visualize_yard(yard_allocation, yard_blocks)

# Show plot
plt.show()
