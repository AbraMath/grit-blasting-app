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

# Nozzle impact size: 2 inch diameter circle
nozzle_diameter_in = 2.0
nozzle_radius_in = nozzle_diameter_in / 2
nozzle_radius_px = int(nozzle_radius_in * resolution / (2 * turntable_radius))

def to_pixel_coords(x, y, radius=turntable_radius):
    # Map (x,y) in inches on turntable to pixel coords in coverage_map
    px = int((x + radius) / (2 * radius) * (resolution - 1))
    py = int((y + radius) / (2 * radius) * (resolution - 1))
    return px, py

def draw_circle_on_map(coverage_map, center_x, center_y, radius_px):
    y_indices, x_indices = np.ogrid[-radius_px:radius_px+1, -radius_px:radius_px+1]
    mask = x_indices**2 + y_indices**2 <= radius_px**2
    h, w = coverage_map.shape
    x_start = max(center_x - radius_px, 0)
    y_start = max(center_y - radius_px, 0)
    x_end = min(center_x + radius_px + 1, w)
    y_end = min(center_y + radius_px + 1, h)

    mask_x_start = 0 if center_x - radius_px >= 0 else radius_px - center_x
    mask_y_start = 0 if center_y - radius_px >= 0 else radius_px - center_y
    mask_x_end = mask_x_start + (x_end - x_start)
    mask_y_end = mask_y_start + (y_end - y_start)

    coverage_map[y_start:y_end, x_start:x_end][mask[mask_y_start:mask_y_end, mask_x_start:mask_x_end]] += 1

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

        # Add coverage circles to map
        for ix, iy in zip(impact_x, impact_y):
            px, py = to_pixel_coords(ix, iy)
            if 0 <= px < resolution and 0 <= py < resolution:
                draw_circle_on_map(coverage_map, px, py, nozzle_radius_px)

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
