import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

st.set_page_config(page_title="Grit Blasting Visualizer", layout="centered")
st.title("🌀 Grit Blasting Visualization with Moving Arrows")

# --- Parameters ---
turntable_radius = 18  # inches
nozzle_ring_radius = turntable_radius / 4
nozzle_ring_offset = turntable_radius / 2  # fixed offset from center
num_nozzles = 6

turntable_rpm = st.slider("Turntable RPM", 1, 60, 20)
nozzle_rpm = st.slider("Nozzle Ring RPM", 1, 60, 20)
trail_length = st.slider("Trail Length (frames)", 1, 150, 20)

st.markdown("Press ▶️ to animate. Arrows rotate **with** the nozzle ring and turntable.")

if st.button("▶️ Play Animation"):
    frame_placeholder = st.empty()
    nozzle_angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)
    trail_history = []

    for frame in range(100):  # simulate ~3 sec
        t = frame / 30
        turntable_angle = 2 * np.pi * (turntable_rpm / 60) * t
        nozzle_angle = 2 * np.pi * (nozzle_rpm / 60) * t

        # --- Fixed nozzle ring center ---
        ring_cx, ring_cy = nozzle_ring_offset, 0

        # --- Compute nozzle positions (rotate around ring center) ---
        x, y = [], []
        for offset in nozzle_angles:
            angle = nozzle_angle + offset
            px = ring_cx + nozzle_ring_radius * np.cos(angle)
            py = ring_cy + nozzle_ring_radius * np.sin(angle)

            # Apply turntable rotation (around origin)
            rx = px * np.cos(turntable_angle) - py * np.sin(turntable_angle)
            ry = px * np.sin(turntable_angle) + py * np.cos(turntable_angle)

            x.append(rx)
            y.append(ry)

        x = np.array(x)
        y = np.array(y)

        # --- Save trail ---
        trail_history.append((x.copy(), y.copy()))
        if len(trail_history) > trail_length:
            trail_history.pop(0)

        # --- Plotting ---
        fig, ax = plt.subplots()
        ax.set_xlim(-turntable_radius - 5, turntable_radius + 5)
        ax.set_ylim(-turntable_radius - 5, turntable_radius + 5)
        ax.set_aspect('equal')
        ax.set_title(f"Frame {frame + 1}/100")

        # Draw turntable outline
        ax.add_patch(plt.Circle((0, 0), turntable_radius, fill=False, linestyle='--', linewidth=1))

        # ➤ Turntable arrow (rotates around origin)
        base_angle = np.radians(45)
        arrow_base_radius = turntable_radius - 3
        tx = arrow_base_radius * np.cos(base_angle + turntable_angle)
        ty = arrow_base_radius * np.sin(base_angle + turntable_angle)
        dx = -1.5 * np.sin(base_angle + turntable_angle)
        dy =  1.5 * np.cos(base_angle + turntable_angle)
        ax.arrow(tx, ty, dx, dy, head_width=1, head_length=1.5, fc='gray', ec='gray', label='Turntable Rotation')

        # ➤ Nozzle ring arrow (rotates with nozzles around ring center)
        arrow_ring_angle = nozzle_angle
        nx = ring_cx + nozzle_ring_radius * np.cos(arrow_ring_angle)
        ny = ring_cy + nozzle_ring_radius * np.sin(arrow_ring_angle)
        tangent_angle = arrow_ring_angle + np.pi / 2
        dxr = 1.5 * np.cos(tangent_angle)
        dyr = 1.5 * np.sin(tangent_angle)

        # Rotate the arrow around origin (turntable)
        nx_rot = nx * np.cos(turntable_angle) - ny * np.sin(turntable_angle)
        ny_rot = nx * np.sin(turntable_angle) + ny * np.cos(turntable_angle)
        dxr_rot = dxr * np.cos(turntable_angle) - dyr * np.sin(turntable_angle)
        dyr_rot = dxr * np.sin(turntable_angle) + dyr * np.cos(turntable_angle)

        ax.arrow(nx_rot, ny_rot, dxr_rot, dyr_rot, head_width=1, head_length=1.5, fc='blue', ec='blue', label='Nozzle Ring Rotation')

        # --- Draw trails ---
        for i, (txs, tys) in enumerate(trail_history):
            alpha = (i + 1) / len(trail_history)
            ax.scatter(txs, tys, color='skyblue', s=200, alpha=alpha)

        # --- Current nozzle positions ---
        ax.scatter(x, y, c='blue', s=200, label='Current Nozzles')
        ax.legend(loc='upper right')

        frame_placeholder.pyplot(fig)
        time.sleep(0.01)
