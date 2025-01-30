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

# =================== FIX: Preprocess ETA Vessel ===================
def preprocess_eta_column(df_vessel):
    df_vessel["ETA Vessel"] = pd.to_datetime(df_vessel["ETA Vessel"], format="%Y%m%d", errors="coerce")

    if df_vessel["ETA Vessel"].isna().all():
        df_vessel["ETA Vessel"] = pd.to_datetime("2025-01-01")

    min_eta = df_vessel["ETA Vessel"].min()
    df_vessel["ETA Vessel"].fillna(min_eta, inplace=True)

    df_vessel["ETA Vessel"] = df_vessel["ETA Vessel"].dt.strftime('%j').astype(int)

    return df_vessel

# =================== SLOT ALLOCATION FUNCTION ===================
def allocate_containers_with_updated_logic(df_vessel):
    allocation = []
    restricted_info = []
    yard_blocks = {
        "NP1": ["A01", "A02", "A03", "A04"],
        "NP2": ["B01", "B02", "B03", "B04"],
        "NP3": ["C01", "C02", "C03", "C04"]
    }
    all_blocks = ["A01", "A02", "A03", "A04", "B01", "B02", "B03", "B04", "C01", "C02", "C03", "C04"]
    yard_occupancy = {block: [] for block in all_blocks}

    df_vessel = preprocess_eta_column(df_vessel)

    for _, row in df_vessel.iterrows():
        vessel_name = row["Vessel Name"]
        total_containers = row["Total Containers"]
        cluster_need = row["Cluster Need"]
        eta_vessel = row["ETA Vessel"]
        berth_location = row["Berth Location"]

        if pd.isna(eta_vessel):
            continue

        restricted_blocks = []
        for alloc in allocation:
            if alloc["ETA Vessel"] >= eta_vessel - 5 and alloc["ETA Vessel"] <= eta_vessel:
                restricted_blocks.append(alloc["Block"])

        primary_blocks = yard_blocks.get(berth_location, all_blocks)  
        available_blocks = [block for block in primary_blocks if block not in restricted_blocks]
        alternative_blocks = [block for block in all_blocks if block not in restricted_blocks]

        if not available_blocks:
            available_blocks = alternative_blocks  

        if not available_blocks:
            restricted_info.append({"Vessel Name": vessel_name, "ETA Vessel": eta_vessel, "Message": "No alternative blocks available"})
            continue

        containers_per_cluster = total_containers // cluster_need
        slots_per_cluster = np.ceil(containers_per_cluster / 30).astype(int)

        for i in range(cluster_need):
            block = available_blocks[i % len(available_blocks)] if available_blocks else alternative_blocks[i % len(alternative_blocks)]

            slots_in_block = list(range(1, 38))
            occupied_slots = yard_occupancy[block]
            empty_slots = [s for s in slots_in_block if s not in occupied_slots]
            slots_to_use = empty_slots if empty_slots else occupied_slots

            if slots_to_use:
                for _ in range(slots_per_cluster):
                    if not slots_to_use:
                        break
                    slot = slots_to_use.pop(0)

                    allocation.append({"Vessel Name": vessel_name, "Block": block, "Slot": slot, "Containers Assigned": 30, "ETA Vessel": eta_vessel, "Berth Location": berth_location})
                    yard_occupancy[block].append(slot)

    return pd.DataFrame(allocation), pd.DataFrame(restricted_info)

# =================== STREAMLIT FILE UPLOADER ===================
st.title("Yard Slot Allocation with Plan A & B")

uploaded_file = st.file_uploader("Upload Excel file with vessel data", type=["xlsx"])

if uploaded_file is not None:
    df_vessel_real = pd.read_excel(uploaded_file)
    df_vessel_real = preprocess_eta_column(df_vessel_real)

    df_allocation_updated, df_restricted_blocks_updated = allocate_containers_with_updated_logic(df_vessel_real)

    # =================== VISUALIZATION FUNCTION ===================
    def visualize_yard(df_allocation, title):
        vessel_names = df_allocation["Vessel Name"].unique()
        colors = list(mcolors.TABLEAU_COLORS.values())[:len(vessel_names)]
        vessel_color_map = {vessel: colors[i % len(colors)] for i, vessel in enumerate(vessel_names)}

        fig, ax = plt.subplots(figsize=(total_columns_with_gaps * 0.2, total_height_with_larger_spacing * 0.8))

        for i, section in enumerate(sections):
            for j in range(rows_per_section):
                row_label = f"{section}{str(j+1).zfill(2)}"
                x_offset = i * (columns_per_section + gap_size)

                for k in range(columns_per_section):
                    allocated_slots = df_allocation[(df_allocation["Block"] == row_label) & (df_allocation["Slot"] == k + 1)]
                    color = vessel_color_map.get(allocated_slots.iloc[0]["Vessel Name"], "gray") if not allocated_slots.empty else "white"
                    rect = plt.Rectangle((x_offset + k, total_height_with_larger_spacing - j - 2 - dock_spacing_blocks), 1, 1, edgecolor='black', facecolor=color, linewidth=1)
                    ax.add_patch(rect)

                ax.text(x_offset - 0.5, total_height_with_larger_spacing - j - 1.5 - dock_spacing_blocks, row_label, va='center', ha='right', fontsize=10, fontweight='bold')

        ax.set_xlim(-1, total_columns_with_gaps)
        ax.set_ylim(-dock_height - 2, total_height_with_larger_spacing)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)

        legend_handles = [plt.Line2D([0], [0], color=vessel_color_map[v], lw=4, label=v) for v in vessel_names]
        ax.legend(handles=legend_handles, title="Vessel Assignments", loc="upper right")

        st.subheader(title)
        st.pyplot(fig)

    # =================== DISPLAY VISUALIZATION & DEBUGGING ===================
    st.subheader("Plan A - Initial Allocation")
    visualize_yard(df_allocation_updated, "Plan A - Initial Allocation")

    st.subheader("Plan B - Overlapping Allocation")
    visualize_yard(df_allocation_updated, "Plan B - Overlapping Allocation")

    st.subheader("Debugging Info: Restricted Blocks")
    st.dataframe(df_restricted_blocks_updated)

    st.subheader("Final Slot Allocation")
    st.dataframe(df_allocation_updated)

else:
    st.write("Please upload an Excel file to proceed.")