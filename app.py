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

    for _, row in df_vessel.iterrows():
        vessel_name = row["Vessel Name"]
        total_containers = row["Total Containers"]
        cluster_need = row["Cluster Need"]
        eta_vessel = row["ETA Vessel"]  # ETA Vessel sekarang dalam Day-of-Year (angka)
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
st.title("Yard Slot Allocation with Fixed ETA (Day-of-Year) & Flexible Blocks")

uploaded_file = st.file_uploader("Upload Excel file with vessel data (ETA in Day-of-Year format)", type=["xlsx"])

if uploaded_file is not None:
    df_vessel_real = pd.read_excel(uploaded_file)

    # Pastikan ETA Vessel sudah dalam format Day-of-Year di Excel
    if not pd.api.types.is_numeric_dtype(df_vessel_real["ETA Vessel"]):
        st.error("Error: Pastikan kolom ETA Vessel di Excel sudah dalam format angka (Day-of-Year).")
    else:
        df_allocation_updated, df_restricted_blocks_updated = allocate_containers_with_updated_logic(df_vessel_real)

        # =================== DISPLAY DEBUGGING INFO ===================
        st.subheader("Debugging Info: Restricted Blocks")
        st.dataframe(df_restricted_blocks_updated)

        st.subheader("Final Slot Allocation")
        st.dataframe(df_allocation_updated)

else:
    st.write("Please upload an Excel file to proceed.")