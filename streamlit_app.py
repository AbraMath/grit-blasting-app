import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

# Must be first
st.set_page_config(page_title="Grit Blasting Visualizer with Arrows", layout="centered")

st.title("🌀 Grit Blasting Nozzle Path Visualization (Fixed Ring Center + Arrows)")

# --- Parameters ---
turntable_radius = 18  # inches (36" diameter / 2)
nozzle_ring_radius = turntable_radius / 4  # ring of nozzles is smaller
nozzle_ring_offset = turntable_radius / 2  # offset from center (9 inches)
num_nozzles = 6

turntable_rpm = st.slider("Turntable RPM", 1, 60, 20)
nozzle_rpm = st.slider("Nozzle Ring RPM", 1, 60, 20)
trail_length = st.slider("Trail Length (frames)", 1, 150, 20)

st.markdown("Press ▶️ to see how the nozzles move with direction arrows.")

if st.button("▶️ Play Animation"):
    frame_placeholder = st.empty()

    nozzle_angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)
    trail_history = []

    for frame in range(100):  # simulate ~3 seconds at 30 FPS
        t = frame / 30
        turntable_angle = 2 * np.pi * (turntable_rpm / 60) * t
        nozzle_angle = -2 * np.pi * (nozzle_rpm / 60) * t

        # --- Fixed nozzle ring center ---
        center_offset_x = nozzle_ring_offset
        center_offset_y = 0

        # --- Compute nozzle positions around fixed center ---
        x = []
        y = []
        for angle_offset in nozzle_angles:
            angle = nozzle_angle + angle_offset
            x.append(center_offset_x + nozzle_ring_radius * np.cos(angle))
            y.append(center_offset_y + nozzle_ring_radius * np.sin(angle))
        x = np.array(x)
        y = np.array(y)

        # --- Rotate by turntable ---
        rotated_x = x * np.cos(turntable_angle) - y * np.sin(turntable_angle)
        rotated_y = x * np.sin(turntable_angle) + y * np.cos(turntable_angle)

        # Save trail
        trail_history.append((rotated_x.copy(), rotated_y.copy()))
        if len(trail_history) > trail_length:
            trail_history.pop(0)

        # --- Plotting ---
        fig, ax = plt.subplots()
        ax.set_xlim(-turntable_radius - 5, turntable_radius + 5)
        ax.set_ylim(-turntable_radius - 5, turntable_radius + 5)
        ax.set_aspect('equal')
        ax.set_title(f"Frame {frame + 1}/100")

        # Draw turntable circle
        turntable_circle = plt.Circle((0, 0), turntable_radius, fill=False, linestyle='--', linewidth=1)
        ax.add_patch(turntable_circle)

        # ➤ Draw turntable rotation arrow
        arrow_length = 3
        theta = np.radians(45)  # position for arrow
        tx = (turntable_radius - 2) * np.cos(theta)
        ty = (turntable_radius - 2) * np.sin(theta)
        dx = -arrow_length * np.sin(theta)
        dy = arrow_length * np.cos(theta)
        ax.arrow(tx, ty, dx, dy, head_width=1, head_length=1.5, fc='gray', ec='gray', label='Turntable Rotation')

        # ➤ Draw nozzle ring rotation arrow (around fixed ring center)
        theta_ring = nozzle_angle
        nx = center_offset_x + nozzle_ring_radius * np.cos(theta_ring)
        ny = center_offset_y + nozzle_ring_radius * np.sin(theta_ring)
        tangent_angle = theta_ring + np.pi / 2  # perpendicular to nozzle path
        dx_ring = 2 * np.cos(tangent_angle)
        dy_ring = 2 * np.sin(tangent_angle)
        # Rotate ring arrow with turntable
        nx_rot = nx * np.cos(turntable_angle) - ny * np.sin(turntable_angle)
        ny_rot = nx * np.sin(turntable_angle) + ny * np.cos(turntable_angle)
        dx_rot = dx_ring * np.cos(turntable_angle) - dy_ring * np.sin(turntable_angle)
        dy_rot = dx_ring * np.sin(turntable_angle) + dy_ring * np.cos(turntable_angle)
        ax.arrow(nx_rot, ny_rot, dx_rot, dy_rot, head_width=1, head_length=1.5, fc='blue', ec='blue', label='Nozzle Rotation')

        # Draw trails
        for i, (txs, tys) in enumerate(trail_history):
            alpha = (i + 1) / len(trail_history)
            ax.scatter(txs, tys, color='skyblue', s=200, alpha=alpha)

        # Draw current nozzles
        ax.scatter(rotated_x, rotated_y, c='blue', s=200, label='Current Nozzles')
        ax.legend(loc='upper right')

        # Show frame
        frame_placeholder.pyplot(fig)
        time.sleep(0.005)
