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

# =================== SLOT ALLOCATION FUNCTION ===================
def allocate_containers_corrected(df_vessel):
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

        occupied_blocks_today = [alloc["Block"] for alloc in allocation if alloc["ETA Vessel"] == eta_vessel]
        free_blocks = [block for block in available_blocks if block not in occupied_blocks_today]

        if free_blocks:
            available_blocks = free_blocks

        containers_per_cluster = total_containers // cluster_need
        slots_per_cluster = np.ceil(containers_per_cluster / 30).astype(int)

        for i in range(cluster_need):
            block = available_blocks[i % len(available_blocks)]
            slots_in_block = list(range(1, 38))

            if block in yard_occupancy:
                occupied_slots = yard_occupancy[block]
                slots_in_block = [s for s in slots_in_block if all(abs(s - oc) >= 5 for oc in occupied_slots)]

            if slots_in_block:
                for _ in range(slots_per_cluster):
                    if not slots_in_block:
                        break
                    slot = slots_in_block.pop(0)

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
    
    # Debugging: Check vessels that were not allocated and total slots used per block
def debug_allocation(df_vessel, df_allocation):
    allocated_vessels = set(df_allocation["Vessel Name"].unique())
    all_vessels = set(df_vessel["Vessel Name"].unique())

    # Find vessels that were not allocated
    unallocated_vessels = all_vessels - allocated_vessels

    # Count total slots allocated per block
    slots_used_per_block = df_allocation.groupby("Block")["Slot"].count().reset_index()

    return list(unallocated_vessels), slots_used_per_block

# Run the debug function
unallocated_vessels, slots_used_per_block = debug_allocation(df_vessel_real, df_allocation_real)

# Display debug information in Streamlit
st.subheader("🔍 Debugging Info: Unallocated Vessels")
if unallocated_vessels:
    st.write("These vessels were **not allocated** due to yard constraints:")
    st.write(unallocated_vessels)
else:
    st.write("✅ All vessels were successfully allocated.")

st.subheader("📊 Debugging Info: Slots Used Per Block")
st.dataframe(slots_used_per_block)

# =================== STREAMLIT FILE UPLOADER ===================
st.title("Yard Slot Allocation with Real Vessel Data")

uploaded_file = st.file_uploader("Upload Excel file with vessel data", type=["xlsx"])

if uploaded_file is not None:
    df_vessel_real = pd.read_excel(uploaded_file)

    # Display uploaded vessel data
    st.subheader("Uploaded Vessel Data")
    st.dataframe(df_vessel_real)

    # Automatically allocate slots
    df_allocation_real = allocate_containers_corrected(df_vessel_real)

    # Display the slot allocation results
    st.subheader("Slot Allocation Results")
    st.dataframe(df_allocation_real)

    # =================== VISUALIZATION ===================
    vessel_names = df_allocation_real["Vessel Name"].unique()
    colors = list(mcolors.TABLEAU_COLORS.values())[:len(vessel_names)]
    vessel_color_map = {vessel: colors[i % len(colors)] for i, vessel in enumerate(vessel_names)}

    fig, ax = plt.subplots(figsize=(total_columns_with_gaps * 0.2, total_height_with_larger_spacing * 0.8))

    for i, section in enumerate(sections):
        for j in range(rows_per_section):
            row_label = f"{section}{str(j+1).zfill(2)}"
            x_offset = i * (columns_per_section + gap_size)

            for k in range(columns_per_section):
                allocated_slots = df_allocation_real[
                    (df_allocation_real["Block"] == row_label) & (df_allocation_real["Slot"] == k + 1)
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