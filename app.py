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
def allocate_containers_with_gradual_arrival(df_vessel):
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
        
        # Determine restricted blocks during the 5-day pre-ETA period
        restricted_blocks = []
        for alloc in allocation:
            if (alloc["ETA Vessel"] >= eta_vessel - 5) and (alloc["ETA Vessel"] <= eta_vessel):
                restricted_blocks.append(alloc["Block"])

        available_blocks = [block for block in yard_blocks[berth_location] if block not in restricted_blocks]

        # Ensure alternative cluster if allocation in a restricted block
        must_have_alternative = len(available_blocks) < cluster_need
        if must_have_alternative:
            alternative_blocks = [block for block in yard_blocks[berth_location] if block not in restricted_blocks]
        else:
            alternative_blocks = available_blocks

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

    return pd.DataFrame(allocation)

# =================== STREAMLIT FILE UPLOADER ===================
st.title("Yard Slot Allocation with Gradual Arrival & Plan A/B")

uploaded_file = st.file_uploader("Upload Excel file with vessel data", type=["xlsx"])

if uploaded_file is not None:
    df_vessel_real = pd.read_excel(uploaded_file)

    # Allocate slots based on uploaded data
    df_allocation_gradual = allocate_containers_with_gradual_arrival(df_vessel_real)

    # =================== DEBUGGING SECTION ===================
    def debug_allocation(df_vessel, df_allocation):
        allocated_vessels = set(df_allocation["Vessel Name"].unique())
        all_vessels = set(df_vessel["Vessel Name"].unique())

        # Find vessels that were not allocated
        unallocated_vessels = all_vessels - allocated_vessels

        # Count total slots allocated per block
        slots_used_per_block = df_allocation.groupby("Block")["Slot"].count().reset_index()

        return list(unallocated_vessels), slots_used_per_block

    # Run debugging checks
    unallocated_vessels, slots_used_per_block = debug_allocation(df_vessel_real, df_allocation_gradual)

    # Show debugging results
    st.subheader("🔍 Debugging Info: Unallocated Vessels")
    if unallocated_vessels:
        st.write("These vessels were **not allocated** due to yard constraints:")
        st.write(unallocated_vessels)
    else:
        st.write("✅ All vessels were successfully allocated.")

    st.subheader("📊 Debugging Info: Slots Used Per Block")
    st.dataframe(slots_used_per_block)

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
                    allocated_slots = df_allocation[
                        (df_allocation["Block"] == row_label) & (df_allocation["Slot"] == k + 1)
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

        ax.set_xlim(-1, total_columns_with_gaps)
        ax.set_ylim(-dock_height - 2, total_height_with_larger_spacing)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)

        legend_handles = [plt.Line2D([0], [0], color=vessel_color_map[v], lw=4, label=v) for v in vessel_names]
        ax.legend(handles=legend_handles, title="Vessel Assignments", loc="upper right")

        st.subheader(title)
        st.pyplot(fig)

    # Display visualizations
    visualize_yard(df_allocation_gradual, "Plan A - Initial Allocation")

else:
    st.write("Please upload an Excel file to proceed.")