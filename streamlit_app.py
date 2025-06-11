import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

# --- App Setup ---
st.set_page_config(page_title="Grit Blasting Simulator", layout="wide")
st.title("🎯 Grit Blasting Coverage Simulator")

# --- Constants ---
turntable_radius = 18  # inches (36" diameter)
nozzle_ring_radius = turntable_radius / 4
nozzle_ring_offset = turntable_radius / 2
num_nozzles = 6
grid_size = 25
x_edges = np.linspace(-turntable_radius, turntable_radius, grid_size + 1)
y_edges = np.linspace(-turntable_radius, turntable_radius, grid_size + 1)

xx, yy = np.meshgrid(
    (x_edges[:-1] + x_edges[1:]) / 2,
    (y_edges[:-1] + y_edges[1:]) / 2,
    indexing='ij'
)
mask = xx**2 + yy**2 <= turntable_radius**2
total_cells = np.sum(mask)

def simulate_coverage(turntable_rpm, nozzle_rpm, run_seconds, fps=30):
    heatmap_grid = np.zeros((grid_size, grid_size))
    nozzle_angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)
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

        hist, _, _ = np.histogram2d(impact_x, impact_y, bins=[x_edges, y_edges])
        heatmap_grid += hist

    hit_count = np.count_nonzero(heatmap_grid[mask])
    coverage_score = (hit_count / total_cells) * 100
    return coverage_score, heatmap_grid

# --- Layout ---
left, right = st.columns(2)

# ================================
# 🔹 Left: Manual Single Simulation
# ================================
with left:
    st.subheader("🎛️ Manual Simulation")

    t_rpm = st.slider("Turntable RPM", 5, 60, 30, step=1)
    n_rpm = st.slider("Nozzle RPM", 5, 60, 30, step=1)
    run_seconds = st.slider("Simulation Time (s)", 1, 20, 5)
    run_manual = st.button("▶️ Run Manual Simulation")

    if run_manual:
        st.write(f"Running simulation for {run_seconds} seconds...")
        coverage, heatmap = simulate_coverage(t_rpm, n_rpm, run_seconds)

        st.metric("Coverage %", f"{coverage:.1f}%")

        fig, ax = plt.subplots()
        extent = [-turntable_radius, turntable_radius, -turntable_radius, turntable_radius]
        im = ax.imshow(np.flipud(heatmap.T), extent=extent, cmap='hot', origin='lower')
        fig.colorbar(im, ax=ax, label="Blast Intensity")
        ax.set_title(f"Heatmap - TT: {t_rpm} RPM, Nozzle: {n_rpm} RPM")
        ax.set_xlabel("X (in)")
        ax.set_ylabel("Y (in)")
        ax.set_aspect("equal")
        st.pyplot(fig)

# ================================
# 🔸 Right: Batch Optimizer
# ================================
with right:
    st.subheader("📊 Batch RPM Optimizer")

    batch_duration = st.slider("Batch Time (s)", 5, 30, 10)
    step = st.select_slider("RPM Step Size", options=[1, 5, 10], value=5)
    run_batch = st.button("🚀 Run Batch Optimization")

    if run_batch:
        rpm_range = list(range(5, 61, step))
        results = []

        with st.spinner("Simulating..."):
            best_score = -1
            best_combo = None
            best_heatmap = None

            for t_rpm in rpm_range:
                for n_rpm in rpm_range:
                    score, heatmap = simulate_coverage(t_rpm, n_rpm, batch_duration)
                    results.append({"Turntable RPM": t_rpm, "Nozzle RPM": n_rpm, "Coverage %": score})
                    if score > best_score:
                        best_score = score
                        best_combo = (t_rpm, n_rpm)
                        best_heatmap = heatmap

        st.metric("Best Coverage %", f"{best_score:.1f}%")
        col1, col2 = st.columns(2)
        col1.metric("Turntable RPM", best_combo[0])
        col2.metric("Nozzle RPM", best_combo[1])

        st.dataframe(results, use_container_width=True)

        fig, ax = plt.subplots()
        extent = [-turntable_radius, turntable_radius, -turntable_radius, turntable_radius]
        im = ax.imshow(np.flipud(best_heatmap.T), extent=extent, cmap='hot', origin='lower')
        fig.colorbar(im, ax=ax, label="Blast Intensity")
        ax.set_title(f"Best Combo Heatmap - TT: {best_combo[0]}, Nozzle: {best_combo[1]}")
        ax.set_xlabel("X (in)")
        ax.set_ylabel("Y (in)")
        ax.set_aspect("equal")
        st.pyplot(fig)
