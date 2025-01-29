import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# =================== PARAMETER GRID ===================
sections = ['A', 'B', 'C']
rows_per_section = 4
columns_per_section = 37
gap_size = 3
dock_labels = ["NP1", "NP2", "NP3"]
dock_height = 1
dock_spacing_blocks = 3
total_columns_with_gaps = (columns_per_section + gap_size) * len(sections) - gap_size
total_height_with_larger_spacing = rows_per_section + dock_height + dock_spacing_blocks

# =================== SLOT ALLOCATION FUNCTION (Balanced) ===================
def allocate_containers_balanced(df_vessel):
    allocation = []
    yard_blocks = {
        "NP1": ["A01", "A02", "A03", "A04"],
        "NP2": ["B01", "B02", "B03", "B04"],
        "NP3": ["C01", "C02", "C03", "C04"]
    }
    yard_occupancy = {block: [] for blocks in yard_blocks.values() for block in blocks}

    for _, row in df_vessel.iterrows():
        vessel_name = row["Vessel Name"]
        total_containers = row["Total Containers"]
        cluster_need = row["Cluster Need"]
        eta_vessel = row["ETA Vessel"]
        berth_location = row["Berth Location"]

        available_blocks = yard_blocks[berth_location].copy()

        # Avoid Yard Clash by checking occupied blocks today
        occupied_blocks_today = [alloc["Block"] for alloc in allocation if alloc["ETA Vessel"] == eta_vessel]
        free_blocks = [block for block in available_blocks if block not in occupied_blocks_today]

        if free_blocks:
            available_blocks = free_blocks

        # Calculate required slots per cluster
        containers_per_cluster = total_containers // cluster_need
        slots_per_cluster = np.ceil(containers_per_cluster / 30).astype(int)

        for i in range(cluster_need):
            block = available_blocks[i % len(available_blocks)]
            slots_in_block = list(range(1, 38))

            # Prioritize filling empty slots before sharing with different ETA
            occupied_slots = yard_occupancy[block]
            empty_slots = [s for s in slots_in_block if s not in occupied_slots]
            shared_slots = [s for s in slots_in_block if s in occupied_slots and 
                            any(alloc["ETA Vessel"] != eta_vessel for alloc in allocation if alloc["Block"] == block and alloc["Slot"] == s)]

            slots_to_use = empty_slots if empty_slots else shared_slots  # Prioritize empty slots first

            if slots_to_use:
                for _ in range(slots_per_cluster):
                    if not slots_to_use:
                        break
                    slot = slots_to_use.pop(0)

                    allocation.append({
                        "Vessel Name": vessel_name,
                        "Block": block,
                        "Slot": slot,
                        "Containers Assigned": 30,
                        "ETA Vessel": eta_vessel,
                        "Berth Location": berth_location
                    })

                    yard_occupancy[block].append(slot)

    return pd.DataFrame(allocation)

# =================== STREAMLIT FILE UPLOADER ===================
st.title("Yard Slot Allocation (Balanced & Optimized)")

uploaded_file = st.file_uploader("Upload Excel file with vessel data", type=["xlsx"])

if uploaded_file is not None:
    df_vessel_real = pd.read_excel(uploaded_file)

    # Display uploaded vessel data
    st.subheader("Uploaded Vessel Data")
    st.dataframe(df_vessel_real)

    # Allocate slots based on uploaded data (Balanced version)
    df_allocation_balanced = allocate_containers_balanced(df_vessel_real)

    # Display the slot allocation results
    st.subheader("Balanced Slot Allocation Results")
    st.dataframe(df_allocation_balanced)

    # =================== VISUALIZATION ===================
    vessel_names = df_allocation_balanced["Vessel Name"].unique()
    colors = list(mcolors.TABLEAU_COLORS.values())[:len(vessel_names)]
    vessel_color_map = {vessel: colors[i % len(colors)] for i, vessel in enumerate(vessel_names)}

    fig, ax = plt.subplots(figsize=(total_columns_with_gaps * 0.2, total_height_with_larger_spacing * 0.8))

    for i, section in enumerate(sections):
        for j in range(rows_per_section):
            row_label = f"{section}{str(j+1).zfill(2)}"
            x_offset = i * (columns_per_section + gap_size)

            for k in range(columns_per_section):
                allocated_slots = df_allocation_balanced[
                    (df_allocation_balanced["Block"] == row_label) & (df_allocation_balanced["Slot"] == k + 1)
                ]
                if not allocated_slots.empty:
                    vessel_name = allocated_slots.iloc[0]["Vessel Name"]
                    color = vessel_color_map.get(vessel_name, "gray")
                    rect = plt.Rectangle((x_offset + k, total_height_with_larger_spacing - j - 2 - dock_spacing_blocks), 1, 1,
                                         edgecolor='black', facecolor=color, linewidth=1)
                else:
                    rect = plt.Rectangle((x_offset + k, total_height_with_larger_spacing - j - 2 - dock_spacing_blocks), 1, 1,
                                         edgecolor='black', facecolor='white', linewidth=1)
                ax.add_patch(rect)

            ax.text(x_offset - 0.5, total_height_with_larger_spacing - j - 1.5 - dock_spacing_blocks, row_label,
                    va='center', ha='right', fontsize=10, fontweight='bold')

    # **Menambahkan kembali visualisasi NP1, NP2, NP3**
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

else:
    st.write("Please upload an Excel file to proceed.")