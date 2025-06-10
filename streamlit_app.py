import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

# Must be first
st.set_page_config(page_title="Grit Blasting Visualizer with Trails", layout="centered")

st.title("🌀 Grit Blasting Nozzle Path Visualization with Trails")

# --- Parameters ---
radius = 18  # inches (36" diameter / 2)
nozzle_radius = radius / 2  # 18" / 2
num_nozzles = 6

turntable_rpm = st.slider("Turntable RPM", 1, 60, 20)
nozzle_rpm = st.slider("Nozzle Assembly RPM", 1, 60, 20)
trail_length = st.slider("Trail Length (frames)", 1, 60, 20)

st.markdown("Press ▶️ to see how the nozzles sweep and cover the part.")

if st.button("▶️ Play Animation"):
    frame_placeholder = st.empty()

    angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)
    trail_history = []

    for frame in range(60):  # simulate 2 seconds at 30 FPS
        t = frame / 30
        turntable_angle = 2 * np.pi * (turntable_rpm / 60) * t
        nozzle_angle = -2 * np.pi * (nozzle_rpm / 60) * t

        # Local nozzle positions
        x = nozzle_radius * np.cos(angles + nozzle_angle)
        y = nozzle_radius * np.sin(angles + nozzle_angle)

        # Rotate the whole thing with turntable
        rotated_x = x * np.cos(turntable_angle) - y * np.sin(turntable_angle)
        rotated_y = x * np.sin(turntable_angle) + y * np.cos(turntable_angle)

        # Save current nozzle positions for trails
        trail_history.append((rotated_x.copy(), rotated_y.copy()))
        if len(trail_history) > trail_length:
            trail_history.pop(0)

        # Plot
        fig, ax = plt.subplots()
        ax.set_xlim(-radius - 5, radius + 5)
        ax.set_ylim(-radius - 5, radius + 5)
        ax.set_aspect('equal')
        ax.set_title(f"Frame {frame + 1}/60")

        # Draw turntable
        turntable_circle = plt.Circle((0, 0), radius, fill=False, linestyle='--', linewidth=1)
        ax.add_patch(turntable_circle)

        # Draw trails (older = lighter)
        for i, (tx, ty) in enumerate(trail_history):
            alpha = (i + 1) / len(trail_history)
            ax.scatter(tx, ty, color='skyblue', s=40, alpha=alpha)

        # Draw current nozzles
        ax.scatter(rotated_x, rotated_y, c='blue', s=100, label='Current Nozzle')
        ax.legend()

        # Update frame
        frame_placeholder.pyplot(fig)
        time.sleep(0.05)
