import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

st.set_page_config(page_title="Grit Blasting Visualizer", layout="centered")
st.title("🌀 Grit Blasting Nozzle Path Visualization (25x25 Grid)")

# --- Parameters ---
turntable_radius = 30  # inches (36" diameter / 2) 
nozzle_ring_radius = turntable_radius / 4
nozzle_ring_offset = turntable_radius / 2
num_nozzles = 6

turntable_rpm = st.slider("Turntable RPM (CW)", 1, 60, 20)
nozzle_rpm = st.slider("Nozzle Ring RPM (CCW)", 1, 60, 20)
nozzle_diameter = st.slider("Nozzle Diameter (inches)", 0.5, 5.0, 2.0, step=0.1)
trail_length = st.slider("Trail Length (frames)", 1, 150, 20)
run_seconds = st.slider("Run Duration (seconds)", 1, 60, 10)

st.markdown("Press ▶️ to run the animation and see coverage with a 25x25 grid limited to the turntable.")

if st.button("▶️ Play Animation"):
    frame_placeholder = st.empty()

    nozzle_angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)
    trail_history = []

    # --- Grid for heatmap (25x25) ---
    grid_size = 25
    heatmap_grid = np.zeros((grid_size, grid_size))
    x_edges = np.linspace(-turntable_radius, turntable_radius, grid_size + 1)
    y_edges = np.linspace(-turntable_radius, turntable_radius, grid_size + 1)

    # Create mask for valid (circular) region
    xx, yy = np.meshgrid(
        (x_edges[:-1] + x_edges[1:]) / 2,
        (y_edges[:-1] + y_edges[1:]) / 2,
        indexing='ij'
    )
    mask = xx**2 + yy**2 <= turntable_radius**2

    fig, ax = plt.subplots()

    fps = 30
    total_frames = int(run_seconds * fps)

    for frame in range(total_frames):
        t = frame / fps

        # --- REVERSED ROTATION DIRECTIONS ---
        turntable_angle = -2 * np.pi * (turntable_rpm / 60) * t  # Now CW
        nozzle_angle = 2 * np.pi * (nozzle_rpm / 60) * t         # Now CCW

        local_x = nozzle_ring_radius * np.cos(nozzle_angles + nozzle_angle)
        local_y = nozzle_ring_radius * np.sin(nozzle_angles + nozzle_angle)

        center_x = nozzle_ring_offset
        center_y = 0

        nozzle_x = local_x + center_x
        nozzle_y = local_y + center_y

        # Rotate nozzle impact points by turntable rotation
        impact_x = nozzle_x * np.cos(turntable_angle) - nozzle_y * np.sin(turntable_angle)
        impact_y = nozzle_x * np.sin(turntable_angle) + nozzle_y * np.cos(turntable_angle)

        trail_history.append((impact_x.copy(), impact_y.copy()))
        if len(trail_history) > trail_length:
            trail_history.pop(0)

        # Update heatmap with nozzle diameter
        for x, y in zip(impact_x, impact_y):
            mask_x = (x_edges[:-1] <= x) & (x < x_edges[1:])
            mask_y = (y_edges[:-1] <= y) & (y < y_edges[1:])
            idx_x = np.where(mask_x)[0]
            idx_y = np.where(mask_y)[0]
            if idx_x.size > 0 and idx_y.size > 0:
                # Increase coverage area based on nozzle diameter
                radius_cells = int(np.ceil((nozzle_diameter / 2) / ((2
