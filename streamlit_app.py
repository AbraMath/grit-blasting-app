import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

# Must be first
st.set_page_config(page_title="Grit Blasting Visualizer with Fixed Ring Center", layout="centered")

st.title("🌀 Grit Blasting Nozzle Path Visualization (Fixed Ring Center)")

# --- Parameters ---
turntable_radius = 18  # inches (36" diameter / 2)
nozzle_ring_radius = turntable_radius / 4  # ring of nozzles is smaller
nozzle_ring_offset = turntable_radius / 2  # offset from center (9 inches)
num_nozzles = 6

turntable_rpm = st.slider("Turntable RPM", 1, 60, 20)
nozzle_rpm = st.slider("Nozzle Ring RPM", 1, 60, 20)
trail_length = st.slider("Trail Length (frames)", 1, 150, 20)

st.markdown("Press ▶️ to see how the fixed-center nozzles move across the turntable.")

if st.button("▶️ Play Animation"):
    frame_placeholder = st.empty()

    nozzle_angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)
    trail_history = []

    for frame in range(100):  # simulate ~3 seconds at 30 FPS
        t = frame / 30
        turntable_angle = 2 * np.pi * (turntable_rpm / 60) * t
        nozzle_angle = -2 * np.pi * (nozzle_rpm / 60) * t

        # --- Fixed nozzle ring center (x = 9", y = 0") ---
        center_offset_x = nozzle_ring_offset
        center_offset_y = 0

        # --- Compute nozzle positions revolving around fixed ring center ---
        x = []
        y = []
        for angle_offset in nozzle_angles:
            angle = nozzle_angle + angle_offset
            x.append(center_offset_x + nozzle_ring_radius * np.cos(angle))
            y.append(center_offset_y + nozzle_ring_radius * np.sin(angle))
        x = np.array(x)
        y = np.array(y)

        # --- Rotate entire system by turntable angle ---
        rotated_x = x * np.cos(turntable_angle) - y * np.sin(turntable_angle)
        rotated_y = x * np.sin(turntable_angle) + y * np.cos(turntable_angle)

        # --- Save current nozzle positions for trail effect ---
        trail_history.append((rotated_x.copy(), rotated_y.copy()))
        if len(trail_history) > trail_length:
            trail_history.pop(0)

        # --- Plotting ---
        fig, ax = plt.subplots()
        ax.set_xlim(-turntable_radius - 5, turntable_radius + 5)
        ax.set_ylim(-turntable_radius - 5, turntable_radius + 5)
        ax.set_aspect('equal')
        ax.set_title(f"Frame {frame + 1}/100")

        # Draw turntable outline
        turntable_circle = plt.Circle((0, 0), turntable_radius, fill=False, linestyle='--', linewidth=1)
        ax.add_patch(turntable_circle)

        # Draw trails (older = lighter)
        for i, (tx, ty) in enumerate(trail_history):
            alpha = (i + 1) / len(trail_history)
            ax.scatter(tx, ty, color='skyblue', s=200, alpha=alpha)

        # Draw current nozzle positions
        ax.scatter(rotated_x, rotated_y, c='blue', s=200, label='Current Nozzles')
        ax.legend()

        # Update frame
        frame_placeholder.pyplot(fig)
        time.sleep(0.005)
