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
    """ Convert ETA Vessel column from YYYYMMDD format to integer days and handle NaN values safely. """
    df_vessel["ETA Vessel"] = pd.to_datetime(df_vessel["ETA Vessel"], format="%Y%m%d", errors="coerce")

    # If all values are NaN, set a default ETA (e.g., first day of the year)
    if df_vessel["ETA Vessel"].isna().all():
        df_vessel["ETA Vessel"] = pd.to_datetime("2025-01-01")

    # Fill NaN values with the minimum valid ETA to avoid conversion errors
    min_eta = df_vessel["ETA Vessel"].min()
    df_vessel["ETA Vessel"].fillna(min_eta, inplace=True)

    # Convert to integer format (day of the year)
    df_vessel["ETA Vessel"] = df_vessel["ETA Vessel"].dt.strftime('%j').astype(int)

    return df_vessel

# =================== SLOT ALLOCATION FUNCTION ===================
def allocate_containers_with_fixed_eta(df_vessel):
    allocation = []
    restricted_info = []  # Store restricted blocks for debugging
    yard_blocks = {
        "NP1": ["A01", "A02", "A03", "A04"],
        "NP2": ["B01", "B02", "B03", "B04"],
        "NP3": ["C01", "C02", "C03", "C04"]
    }
    yard_occupancy = {block: [] for blocks in yard_blocks.values() for block in blocks}

    df_vessel = preprocess_eta_column(df_vessel)  # Convert ETA properly

    for _, row in df_vessel.iterrows():
        vessel_name = row["Vessel Name"]
        total_containers = row["Total Containers"]
        cluster_need = row["Cluster Need"]
        eta_vessel = row["ETA Vessel"]
        berth_location = row["Berth Location"]

        if pd.isna(eta_vessel):
            continue

        # Determine restricted blocks during the 5-day pre-ETA period
        restricted_blocks = []
        for alloc in allocation:
            if alloc["ETA Vessel"] is not None and (alloc["ETA Vessel"] >= eta_vessel - 5) and (alloc["ETA Vessel"] <= eta_vessel):
                restricted_blocks.append(alloc["Block"])

        available_blocks = [block for block in yard_blocks[berth_location] if block not in restricted_blocks]

        # Store debugging info if no available blocks
        if not available_blocks:
            restricted_info.append({
                "Vessel Name": vessel_name,
                "ETA Vessel": eta_vessel,
                "Restricted Blocks": restricted_blocks
            })
            continue  # Skip this vessel to prevent errors

        # Ensure alternative cluster if allocation in a restricted block
        must_have_alternative = len(available_blocks) < cluster_need
        alternative_blocks = [block for block in yard_blocks[berth_location] if block not in restricted_blocks] if must_have_alternative else available_blocks

        # If no alternative blocks available, skip this vessel to avoid errors
        if not alternative_blocks:
            restricted_info.append({
                "Vessel Name": vessel_name,
                "ETA Vessel": eta_vessel,
                "Message": "No alternative blocks available"
            })
            continue

        containers_per_cluster = total_containers // cluster_need
        slots_per_cluster = np.ceil(containers_per_cluster / 30).astype(int)

        for i in range(cluster_need):
            if i < len(available_blocks):
                block = available_blocks[i]
            else:
                block = alternative_blocks[i % len(alternative_blocks)]

            slots_in_block = list(range(1, 38))

            # Prioritize filling empty slots before reusing occupied slots
            occupied_slots = yard_occupancy[block]
            empty_slots = [s for s in slots_in_block if s not in occupied_slots]
            shared_slots = [s for s in slots_in_block if s in occupied_slots and 
                            any(alloc["ETA Vessel"] != eta_vessel for alloc in allocation if alloc["Block"] == block and alloc["Slot"] == s)]
            slots_to_use = empty_slots if empty_slots else shared_slots  

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

    return pd.DataFrame(allocation, columns=["Vessel Name", "Block", "Slot", "Containers Assigned", "ETA Vessel", "Berth Location"]), pd.DataFrame(restricted_info)

# =================== STREAMLIT FILE UPLOADER ===================
st.title("Yard Slot Allocation with Fixed ETA Handling")

uploaded_file = st.file_uploader("Upload Excel file with vessel data", type=["xlsx"])

if uploaded_file is not None:
    df_vessel_real = pd.read_excel(uploaded_file)

    # Run preprocessing on vessel data
    df_vessel_real = preprocess_eta_column(df_vessel_real)

    # Run allocation function again with fixed ETA handling
    df_allocation_fixed_eta, df_restricted_blocks_fixed = allocate_containers_with_fixed_eta(df_vessel_real)

    # =================== DISPLAY DEBUGGING INFO ===================
    st.subheader("Debugging Info: Restricted Blocks")
    st.dataframe(df_restricted_blocks_fixed)

    st.subheader("Final Slot Allocation")
    st.dataframe(df_allocation_fixed_eta)

else:
    st.write("Please upload an Excel file to proceed.")