import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set page config
st.set_page_config(page_title="Grit Blasting Visualizer", layout="centered")

st.title("🔩 Grit Blasting Visualizer")
st.markdown("Visualize how your turntable and rotating nozzle system covers parts.")

# User inputs
col1, col2 = st.columns(2)
with col1:
    turntable_rpm = st.slider("Turntable RPM", 1, 60, 10)
    table_radius_in = st.slider("Turntable Diameter (in)", 24, 60, 36) / 2
with col2:
    nozzle_rpm = st.slider("Nozzle Ring RPM", 1, 60, 20)
    num_nozzles = st.slider("Number of Nozzles", 1, 12, 6)

blast_duration = st.slider("Blast Duration (s)", 5, 60, 30)
nozzle_distance_in = table_radius_in / 2  # fixed at midpoint
nozzle_spot_radius = 1  # inches (2 inch diameter)

# Time simulation
fps = 20
t = np.linspace(0, blast_duration, blast_duration * fps)

# Precompute angles
turntable_angle = 2 * np.pi * (turntable_rpm / 60) * t
nozzle_angle = -2 * np.pi * (nozzle_rpm / 60) * t  # opposite direction

# Plot setup
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_aspect('equal')
ax.set_xlim(-table_radius_in-5, table_radius_in+5)
ax.set_ylim(-table_radius_in-5, table_radius_in+5)

# Draw turntable
turntable = patches.Circle((0, 0), table_radius_in, fill=False, linestyle='--', label="Turntable")
ax.add_patch(turntable)

# Animate nozzle paths
colors = plt.cm.viridis(np.linspace(0, 1, num_nozzles))
for i in range(num_nozzles):
    angle_offset = 2 * np.pi * i / num_nozzles
    x_path, y_path = [], []
    for j in range(len(t)):
        # Nozzle position on rotating ring
        nozzle_x = nozzle_distance_in * np.cos(nozzle_angle[j] + angle_offset)
        nozzle_y = nozzle_distance_in * np.sin(nozzle_angle[j] + angle_offset)

        # Rotate nozzle path by turntable
        rotated_x = nozzle_x * np.cos(turntable_angle[j]) - nozzle_y * np.sin(turntable_angle[j])
        rotated_y = nozzle_x * np.sin(turntable_angle[j]) + nozzle_y * np.cos(turntable_angle[j])

        x_path.append(rotated_x)
        y_path.append(rotated_y)

    ax.plot(x_path, y_path, color=colors[i], label=f"Nozzle {i+1}")
    ax.add_patch(patches.Circle((x_path[-1], y_path[-1]), nozzle_spot_radius, color=colors[i], alpha=0.3))

ax.legend(loc="upper right", fontsize="x-small")
st.pyplot(fig)

st.markdown("---")
st.caption("Developed with ❤️ for visualizing automated blasting systems.")
