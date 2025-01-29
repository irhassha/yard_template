import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# =================== PARAMETER GRID ===================
sections = ['A', 'B', 'C']
rows_per_section = 4
columns_per_section = 37
gap_size = 3  # Jumlah kolom kosong sebagai pemisah antar block
dock_labels = ["NP1", "NP2", "NP3"]
dock_height = 1  # Tinggi dermaga di bawah grid
dock_spacing_blocks = 3  # Jarak antara Yard Blocks dan Dermaga
total_columns_with_gaps = (columns_per_section + gap_size) * len(sections) - gap_size
total_height_with_larger_spacing = rows_per_section + dock_height + dock_spacing_blocks

# =================== GENERATE DUMMY VESSEL DATA ===================
num_vessels = 10  # Jumlah kapal
berth_locations = ["NP1", "NP2", "NP3"]
yard_blocks = {
    "NP1": ["A01", "A02", "A03", "A04"],
    "NP2": ["B01", "B02", "B03", "B04"],
    "NP3": ["C01", "C02", "C03", "C04"]
}
eta_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

vessel_data = []
for i in range(num_vessels):
    vessel_name = f"Vessel_{i+1}"
    total_containers = np.random.randint(300, 1000)  # Random number of containers
    cluster_need = np.random.randint(2, 5)  # Random cluster need (spread across blocks/slots)
    eta_vessel = np.random.choice(eta_days)  # Random ETA day
    berth_location = np.random.choice(berth_locations)  # Random berth location
    
    vessel_data.append([vessel_name, total_containers, cluster_need, eta_vessel, berth_location])

df_vessel_dummy = pd.DataFrame(vessel_data, columns=["Vessel Name", "Total Containers", "Cluster Need", "ETA Vessel", "Berth Location"])

# =================== SLOT ALLOCATION FUNCTION ===================
def allocate_containers(df_vessel):
    allocation = []
    yard_occupancy = {block: [] for blocks in yard_blocks.values() for block in blocks}

    for _, row in df_vessel.iterrows():
        vessel_name = row["Vessel Name"]
        total_containers = row["Total Containers"]
        cluster_need = row["Cluster Need"]
        eta_vessel = row["ETA Vessel"]
        berth_location = row["Berth Location"]

        # Get priority blocks based on berth location
        available_blocks = yard_blocks[berth_location].copy()

        # Avoid Yard Clash
        occupied_blocks_today = [alloc["Block"] for alloc in allocation if alloc["ETA Vessel"] == eta_vessel]
        free_blocks = [block for block in available_blocks if block not in occupied_blocks_today]

        if free_blocks:
            available_blocks = free_blocks  # Prioritize avoiding yard clash

        # Distribute containers evenly
        containers_per_cluster = total_containers // cluster_need
        remaining_containers = total_containers % cluster_need

        for i in range(cluster_need):
            block = available_blocks[i % len(available_blocks)]
            slots_in_block = list(range(1, 38))

            # Ensure spacing if in the same block
            if block in yard_occupancy:
                occupied_slots = yard_occupancy[block]
                slots_in_block = [s for s in slots_in_block if all(abs(s - oc) >= 5 for oc in occupied_slots)]

            if slots_in_block:
                slot = slots_in_block[0]  # Pick the first available slot

                allocation.append({
                    "Vessel Name": vessel_name,
                    "Block": block,
                    "Slot": slot,
                    "Containers Assigned": containers_per_cluster + (1 if i < remaining_containers else 0),
                    "ETA Vessel": eta_vessel,
                    "Berth Location": berth_location
                })

                yard_occupancy[block].append(slot)

    return pd.DataFrame(allocation)

df_allocation = allocate_containers(df_vessel_dummy)

# =================== VISUALIZATION ===================
st.title("Yard Grid with Slot Allocation Visualization")
st.write("Visualisasi yard grid dengan slot yang dialokasikan berdasarkan aturan prioritas dan yard clash.")

# Assign colors to vessels
vessel_names = df_allocation["Vessel Name"].unique()
colors = list(mcolors.TABLEAU_COLORS.values())[:len(vessel_names)]
vessel_color_map = {vessel: colors[i % len(colors)] for i, vessel in enumerate(vessel_names)}

fig, ax = plt.subplots(figsize=(total_columns_with_gaps * 0.2, total_height_with_larger_spacing * 0.8))

# Draw the yard template with allocated slots
for i, section in enumerate(sections):
    for j in range(rows_per_section):
        row_label = f"{section}{str(j+1).zfill(2)}"
        x_offset = i * (columns_per_section + gap_size)

        for k in range(columns_per_section):
            allocated = df_allocation[(df_allocation["Block"] == row_label) & (df_allocation["Slot"] == k + 1)]
            if not allocated.empty:
                vessel_name = allocated.iloc[0]["Vessel Name"]
                color = vessel_color_map[vessel_name]
                rect = plt.Rectangle((x_offset + k, total_height_with_larger_spacing - j - 2 - dock_spacing_blocks), 1, 1,
                                     edgecolor='black', facecolor=color, linewidth=1)
            else:
                rect = plt.Rectangle((x_offset + k, total_height_with_larger_spacing - j - 2 - dock_spacing_blocks), 1, 1,
                                     edgecolor='black', facecolor='white', linewidth=1)
            ax.add_patch(rect)

        ax.text(x_offset - 0.5, total_height_with_larger_spacing - j - 1.5 - dock_spacing_blocks, row_label,
                va='center', ha='right', fontsize=10, fontweight='bold')

# Add blank space between yard blocks and docks
for i in range(dock_spacing_blocks):
    for section_idx in range(len(sections)):
        x_offset = section_idx * (columns_per_section + gap_size)
        for k in range(columns_per_section):
            rect = plt.Rectangle((x_offset + k, i), 1, 1,
                                 edgecolor='black', facecolor='white', linewidth=1, linestyle='dotted')
            ax.add_patch(rect)

# Add dock labels
for i, dock_label in enumerate(dock_labels):
    x_offset = i * (columns_per_section + gap_size)
    rect = plt.Rectangle((x_offset, -dock_height - 1), columns_per_section, dock_height,
                         edgecolor='black', facecolor='lightgray', linewidth=2)
    ax.add_patch(rect)
    ax.text(x_offset + columns_per_section / 2, -dock_height - 0.5, dock_label,
            va='center', ha='center', fontsize=12, fontweight='bold')

ax.set_xlim(-1, total_columns_with_gaps)
ax.set_ylim(-dock_height - 2, total_height_with_larger_spacing)
ax.set_xticks([])
ax.set_yticks([])
ax.set_frame_on(False)

legend_handles = [plt.Line2D([0], [0], color=vessel_color_map[v], lw=4, label=v) for v in vessel_names]
ax.legend(handles=legend_handles, title="Vessel Assignments", loc="upper right")

st.pyplot(fig)