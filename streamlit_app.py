import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

st.set_page_config(page_title="Grit Blasting Visualizer", layout="centered")
st.title("🎯 Grit Blasting - Stationary Nozzle Ring Center")

# --- Parameters ---
turntable_radius = 18  # inches
nozzle_ring_radius = turntable_radius / 4
nozzle_ring_offset = turntable_radius / 2  # fixed offset from center
num_nozzles = 6

turntable_rpm = st.slider("Turntable RPM", 1, 60, 20)
nozzle_rpm = st.slider("Nozzle Ring RPM", 1, 60, 20)
trail_length = st.slider("Trail Length (frames)", 1, 150, 20)

st.markdown("Press ▶️ to animate. Arrows rotate **with** the nozzle ring and turntable independently.")

if st.button("▶️ Play Animation"):
    frame_placeholder = st.empty()
    nozzle_offsets = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)
    trail_history = []

    for frame in range(100):
        t = frame / 30  # simulate ~30 FPS
        turntable_angle = 2 * np.pi * (turntable_rpm / 60) * t
        nozzle_angle = 2 * np.pi * (nozzle_rpm / 60) * t

        # Fixed nozzle ring center (remains stationary in view)
        ring_cx, ring_cy = nozzle_ring_offset, 0

        # --- Compute impact points on turntable ---
        x, y = [], []
        for offset in nozzle_offsets:
            angle = nozzle_angle + offset
            nx = ring_cx + nozzle_ring_radius * np.cos(angle)
            ny = ring_cy + nozzle_ring_radius * np.sin(angle)

            # Apply turntable rotation (rotate impact point around (0,0))
            rx = nx * np.cos(turntable_angle) - ny * np.sin(turntable_angle)
            ry = nx * np.sin(turntable_angle) + ny * np.cos(turntable_angle)

            x.append(rx)
            y.append(ry)

        # Save trail
        trail_history.append((x.copy(), y.copy()))
        if len(trail_history) > trail_length:
            trail_history.pop(0)

        # --- Plotting ---
        fig, ax = plt.subplots()
        ax.set_xlim(-turntable_radius - 5, turntable_radius + 5)
        ax.set_ylim(-turntable_radius - 5, turntable_radius + 5)
        ax.set_aspect("equal")
        ax.set_title(f"Frame {frame + 1}/100")

        # Turntable outline
        ax.add_patch(plt.Circle((0, 0), turntable_radius, fill=False, linestyle='--', linewidth=1))

        # ➤ Turntable arrow (rotating)
        base_angle = np.radians(45)
        arrow_base_radius = turntable_radius - 3
        tx = arrow_base_radius * np.cos(base_angle + turntable_angle)
        ty = arrow_base_radius * np.sin(base_angle + turntable_angle)
        dx = -1.5 * np.sin(base_angle + turntable_angle)
        dy =  1.5 * np.cos(base_angle + turntable_angle)
        ax.arrow(tx, ty, dx, dy, head_width=1, head_length=1.5, fc='gray', ec='gray', label="Turntable Rotation")

        # ➤ Nozzle ring arrow (fixed center)
        nozzle_arrow_angle = nozzle_angle
        nx = ring_cx + nozzle_ring_radius * np.cos(nozzle_arrow_angle)
        ny = ring_cy + nozzle_ring_radius * np.sin(nozzle_arrow_angle)
        tangent_angle = nozzle_arrow_angle + np.pi / 2
        dxr = 1.5 * np.cos(tangent_angle)
        dyr = 1.5 * np.sin(tangent_angle)
        ax.arrow(nx, ny, dxr, dyr, head_width=1, head_length=1.5, fc='blue', ec='blue', label="Nozzle Ring Rotation")

        # --- Trails ---
        for i, (txs, tys) in enumerate(trail_history):
            alpha = (i + 1) / len(trail_history)
            ax.scatter(txs, tys, color='skyblue', s=200, alpha=alpha)

        # --- Current impact points ---
        ax.scatter(x, y, c='blue', s=200, label='Nozzles Impact Points')
        ax.legend(loc='upper right')

        frame_placeholder.pyplot(fig)
        time.sleep(0.01)
