import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

# Set Streamlit config
st.set_page_config(page_title="Grit Blasting Visualizer", layout="centered")

st.title("🌀 Grit Blasting Nozzle Path Visualization")

# --- Parameters ---
turntable_radius = 18  # inches (36" diameter / 2)
nozzle_ring_radius = turntable_radius / 4  # radius of the nozzle ring
nozzle_ring_offset = turntable_radius / 2  # distance from turntable center
num_nozzles = 6

# UI Controls
turntable_rpm = st.slider("Turntable RPM", 1, 60, 20)
nozzle_rpm = st.slider("Nozzle Ring RPM", 1, 60, 20)
trail_length = st.slider("Trail Length (frames)", 1, 150, 20)

st.markdown("Press ▶️ to visualize nozzle movement around a stationary center and their impact on a spinning turntable.")

if st.button("▶️ Play Animation"):
    frame_placeholder = st.empty()

    nozzle_angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)
    trail_history = []

   for frame in range(100):
    t = frame / 30  # time in seconds (assuming 30 FPS)
    turntable_angle = 2 * np.pi * (turntable_rpm / 60) * t
    nozzle_angle = -2 * np.pi * (nozzle_rpm / 60) * t

    # Calculate nozzle positions (relative to nozzle ring center)
    local_x = nozzle_ring_radius * np.cos(nozzle_angles + nozzle_angle)
    local_y = nozzle_ring_radius * np.sin(nozzle_angles + nozzle_angle)

    # Fixed nozzle ring center
    center_x = nozzle_ring_offset
    center_y = 0

    nozzle_x = local_x + center_x
    nozzle_y = local_y + center_y

    # Rotate impact points with turntable
    impact_x = nozzle_x * np.cos(turntable_angle) - nozzle_y * np.sin(turntable_angle)
    impact_y = nozzle_x * np.sin(turntable_angle) + nozzle_y * np.cos(turntable_angle)

    # Store trail
    trail_history.append((impact_x.copy(), impact_y.copy()))
    if len(trail_history) > trail_length:
        trail_history.pop(0)

    # Plot
    fig, ax = plt.subplots()
    ax.set_xlim(-turntable_radius - 5, turntable_radius + 5)
    ax.set_ylim(-turntable_radius - 5, turntable_radius + 5)
    ax.set_aspect('equal')
    ax.set_title(f"Frame {frame + 1}/100")

    # Draw turntable
    turntable_circle = plt.Circle((0, 0), turntable_radius, fill=False, linestyle='--', linewidth=1)
    ax.add_patch(turntable_circle)

    # Draw nozzle ring center
    ax.scatter(center_x, center_y, c='red', s=100, label="Nozzle Ring Center")

    # Arrows to show direction
    arrow_length = 4

    # Nozzle ring arrow (red)
    arrow_dx = -arrow_length * np.sin(nozzle_angle)
    arrow_dy = arrow_length * np.cos(nozzle_angle)
    ax.arrow(center_x, center_y, arrow_dx, arrow_dy, color='red', width=0.3, head_width=1)

    # Turntable arrow (gray)
    t_dx = -arrow_length * np.sin(turntable_angle)
    t_dy = arrow_length * np.cos(turntable_angle)
    ax.arrow(0, 0, t_dx, t_dy, color='gray', width=0.3, head_width=1)

    # Trails (older = lighter)
    for i, (tx, ty) in enumerate(trail_history):
        alpha = (i + 1) / len(trail_history)
        ax.scatter(tx, ty, color='skyblue', s=200, alpha=alpha)

    # Current nozzle position (dark blue)
    ax.scatter(nozzle_x, nozzle_y, c='blue', s=200, label='Nozzle Tips')

    ax.legend(loc='upper right')
    frame_placeholder.pyplot(fig)
    time.sleep(0.01)
