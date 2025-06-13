import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

st.set_page_config(page_title="Grit Blasting Visualizer", layout="centered")
st.title("🌀 Grit Blasting Nozzle Path Visualization (25x25 Grid)")

# --- Parameters ---
turntable_radius = 30  # inches (36" diameter / 2) 
nozzle_ring_radius = 15
nozzle_ring_offset = turntable_radius / 2
num_nozzles = 6

turntable_rpm = st.slider("Turntable RPM", 1, 8, 0)
nozzle_rpm = st.slider("Nozzle Ring RPM", 1, 44, 0)
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
        turntable_angle = 2 * np.pi * (turntable_rpm / 60) * t
        nozzle_angle = -2 * np.pi * (nozzle_rpm / 60) * t

        local_x = nozzle_ring_radius * np.cos(nozzle_angles + nozzle_angle)
        local_y = nozzle_ring_radius * np.sin(nozzle_angles + nozzle_angle)

        center_x = nozzle_ring_offset
        center_y = 0

        nozzle_x = local_x + center_x
        nozzle_y = local_y + center_y

        impact_x = nozzle_x * np.cos(turntable_angle) - nozzle_y * np.sin(turntable_angle)
        impact_y = nozzle_x * np.sin(turntable_angle) + nozzle_y * np.cos(turntable_angle)

        trail_history.append((impact_x.copy(), impact_y.copy()))
        if len(trail_history) > trail_length:
            trail_history.pop(0)

        # Update heatmap
        hist, _, _ = np.histogram2d(impact_x, impact_y, bins=[x_edges, y_edges])
        heatmap_grid += hist

        # --- Plotting ---
        ax.clear()
        ax.set_xlim(-turntable_radius - 5, turntable_radius + 5)
        ax.set_ylim(-turntable_radius - 5, turntable_radius + 5)
        ax.set_aspect('equal')
        ax.set_title(f"Frame {frame + 1}/{total_frames}")

        turntable_circle = plt.Circle((0, 0), turntable_radius, fill=False, linestyle='--', linewidth=1)
        ax.add_patch(turntable_circle)

        ax.scatter(center_x, center_y, c='red', s=100, label="Nozzle Ring Center")

        arrow_length = 4
        arrow_dx = -arrow_length * np.sin(nozzle_angle)
        arrow_dy = arrow_length * np.cos(nozzle_angle)
        ax.arrow(center_x, center_y, arrow_dx, arrow_dy, color='red', width=0.3, head_width=1)

        t_dx = -arrow_length * np.sin(turntable_angle)
        t_dy = arrow_length * np.cos(turntable_angle)
        ax.arrow(0, 0, t_dx, t_dy, color='gray', width=0.3, head_width=1)

        for i, (tx, ty) in enumerate(trail_history):
            alpha = (i + 1) / len(trail_history)
            ax.scatter(tx, ty, color=(0.3, 0.5, 0.9, alpha), s=200)  # Mid-tone blue trail

        ax.scatter(nozzle_x, nozzle_y, c='blue', s=200, label='Nozzle Tips')
        ax.legend(loc='upper right')

        frame_placeholder.pyplot(fig)
        time.sleep(0.005)

    # --- After animation: show heatmap ---
    fig2, ax2 = plt.subplots()
    ax2.set_title("🔆 Coverage Heatmap (25x25 Grid)")
    extent = [-turntable_radius, turntable_radius, -turntable_radius, turntable_radius]
    cax = ax2.imshow(np.flipud(heatmap_grid.T), extent=extent, cmap='hot', origin='lower')
    fig2.colorbar(cax, ax=ax2, label="Blast Intensity")
    ax2.set_xlabel("X (inches)")
    ax2.set_ylabel("Y (inches)")
    ax2.set_aspect('equal')
    st.pyplot(fig2)

    # --- Coverage Score ---
    total_cells = np.sum(mask)
    hit_count = np.count_nonzero(heatmap_grid[mask])
    coverage_score = (hit_count / total_cells) * 100
    st.metric("📈 Estimated Coverage %", f"{coverage_score:.1f}%")

    # --- Extra Stats ---
    turntable_revs = (turntable_rpm * run_seconds) / 60
    nozzle_revs = (nozzle_rpm * run_seconds) / 60
    col1, col2 = st.columns(2)
    col1.metric("🔄 Turntable Revolutions", f"{turntable_revs:.2f}")
    col2.metric("🔁 Nozzle Ring Revolutions", f"{nozzle_revs:.2f}")
