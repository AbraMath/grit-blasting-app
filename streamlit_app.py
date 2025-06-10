import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

st.set_page_config(page_title="Grit Blasting Coverage Heatmap", layout="centered")
st.title("🌀 Grit Blasting Coverage Heatmap Visualization")

# Parameters
turntable_radius = 18  # inches (36" diameter / 2)
nozzle_ring_radius = turntable_radius / 4
nozzle_ring_offset = turntable_radius / 2  # fixed center offset (9 inches)
num_nozzles = 6

turntable_rpm = st.slider("Turntable RPM", 1, 60, 20)
nozzle_rpm = st.slider("Nozzle Ring RPM", 1, 60, 20)
num_frames = st.slider("Number of Frames (Duration)", 10, 200, 100)

# Coverage map resolution
resolution = 400  # pixels for coverage map (square)
coverage_map = np.zeros((resolution, resolution))

def to_pixel_coords(x, y, radius=turntable_radius):
    # Map (x,y) in inches on turntable to pixel coords in coverage_map
    px = int((x + radius) / (2 * radius) * (resolution - 1))
    py = int((y + radius) / (2 * radius) * (resolution - 1))
    return px, py

st.markdown("Press ▶️ to simulate grit blast coverage accumulating on the turntable.")

if st.button("▶️ Start Simulation"):
    frame_placeholder = st.empty()

    nozzle_angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)

    # Clear coverage map at start
    coverage_map.fill(0)

    for frame in range(num_frames):
        t = frame / 30  # assume 30 FPS time

        # Independent rotations
        turntable_angle = 2 * np.pi * (turntable_rpm / 60) * t
        nozzle_angle = -2 * np.pi * (nozzle_rpm / 60) * t

        # Nozzles revolve around fixed ring center
        local_x = nozzle_ring_radius * np.cos(nozzle_angles + nozzle_angle)
        local_y = nozzle_ring_radius * np.sin(nozzle_angles + nozzle_angle)

        center_x = nozzle_ring_offset
        center_y = 0

        nozzle_x = local_x + center_x
        nozzle_y = local_y + center_y

        # Calculate impact points after turntable rotation
        impact_x = nozzle_x * np.cos(turntable_angle) - nozzle_y * np.sin(turntable_angle)
        impact_y = nozzle_x * np.sin(turntable_angle) + nozzle_y * np.cos(turntable_angle)

        # Add coverage to map
        for ix, iy in zip(impact_x, impact_y):
            px, py = to_pixel_coords(ix, iy)
            if 0 <= px < resolution and 0 <= py < resolution:
                coverage_map[py, px] += 1

        # Plot coverage heatmap
        fig, ax = plt.subplots(figsize=(6,6))
        ax.imshow(coverage_map, extent=[-turntable_radius, turntable_radius, -turntable_radius, turntable_radius],
                  origin='lower', cmap='Blues', alpha=0.7)

        # Draw turntable outline
        turntable_circle = plt.Circle((0, 0), turntable_radius, fill=False, linestyle='--', linewidth=1)
        ax.add_patch(turntable_circle)

        # Draw nozzle ring center (fixed)
        ax.scatter(center_x, center_y, c='red', s=100, label='Nozzle Ring Center')

        # Draw nozzles
        ax.scatter(nozzle_x, nozzle_y, c='blue', s=150, label='Nozzles')

        # Draw rotation direction arrows
        arrow_len = 3
        # Nozzle ring arrow (red)
        arrow_dx = -arrow_len * np.sin(nozzle_angle)
        arrow_dy = arrow_len * np.cos(nozzle_angle)
        ax.arrow(center_x, center_y, arrow_dx, arrow_dy, color='red', width=0.15, head_width=0.6)

        # Turntable arrow (gray) at origin
        t_dx = -arrow_len * np.sin(turntable_angle)
        t_dy = arrow_len * np.cos(turntable_angle)
        ax.arrow(0, 0, t_dx, t_dy, color='gray', width=0.15, head_width=0.6)

        ax.set_xlim(-turntable_radius-2, turntable_radius+2)
        ax.set_ylim(-turntable_radius-2, turntable_radius+2)
        ax.set_aspect('equal')
        ax.set_title(f"Frame {frame+1}/{num_frames}")
        ax.legend(loc='upper right')

        frame_placeholder.pyplot(fig)
        plt.close(fig)
        time.sleep(0.03)  # ~30 FPS
