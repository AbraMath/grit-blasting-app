import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
from io import BytesIO

st.set_page_config(page_title="Grit Blasting Visualizer", layout="wide")
st.title("🌀 Grit Blasting Coverage Comparison Tool (25x25 Grid)")

# --- Parameters ---
turntable_radius = 30  # inches
nozzle_ring_radius = turntable_radius / 4
nozzle_ring_offset = turntable_radius / 2
num_nozzles = 6
grid_size = 25

# RPM combo settings
st.sidebar.header("Simulation Settings")
rpm_step = st.sidebar.slider("RPM Step Size", 5, 20, 10)
run_seconds = st.sidebar.slider("Run Duration (seconds)", 1, 30, 5)
trail_length = st.sidebar.slider("Trail Length (frames)", 1, 150, 20)

turntable_rpms = list(range(5, 65, rpm_step))
nozzle_rpms = list(range(5, 65, rpm_step))
rpm_pairs = [(tt, nz) for tt in turntable_rpms for nz in nozzle_rpms]


def simulate_rpm_pair(turntable_rpm, nozzle_rpm, run_seconds, grid_size=25):
    fps = 30
    total_frames = int(run_seconds * fps)
    nozzle_angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)

    x_edges = np.linspace(-turntable_radius, turntable_radius, grid_size + 1)
    y_edges = np.linspace(-turntable_radius, turntable_radius, grid_size + 1)
    heatmap_grid = np.zeros((grid_size, grid_size))

    # Mask for valid area
    xx, yy = np.meshgrid(
        (x_edges[:-1] + x_edges[1:]) / 2,
        (y_edges[:-1] + y_edges[1:]) / 2,
        indexing='ij'
    )
    mask = xx**2 + yy**2 <= turntable_radius**2

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

    total_cells = np.sum(mask)
    hit_cells = np.count_nonzero(heatmap_grid[mask])
    coverage_score = (hit_cells / total_cells) * 100
    return heatmap_grid, coverage_score


def plot_heatmap(grid, title="Coverage Heatmap"):
    fig, ax = plt.subplots()
    extent = [-turntable_radius, turntable_radius, -turntable_radius, turntable_radius]
    im = ax.imshow(np.flipud(grid.T), extent=extent, cmap="hot", origin="lower")
    ax.set_title(title)
    ax.set_xlabel("X (inches)")
    ax.set_ylabel("Y (inches)")
    ax.set_aspect("equal")
    fig.colorbar(im, ax=ax, label="Blast Intensity")
    return fig


# --- Run simulations ---
st.markdown(f"### 🔁 Simulating All RPM Pairs ({len(rpm_pairs)} total)")

results = []
cols = st.columns(3)

for idx, (tt_rpm, nz_rpm) in enumerate(rpm_pairs):
    grid, score = simulate_rpm_pair(tt_rpm, nz_rpm, run_seconds)
    results.append({
        "turntable_rpm": tt_rpm,
        "nozzle_rpm": nz_rpm,
        "coverage": score,
        "grid": grid
    })

    with cols[idx % 3]:
        st.write(f"**TT: {tt_rpm} RPM / NZ: {nz_rpm} RPM**")
        fig = plot_heatmap(grid, title=f"TT {tt_rpm} / NZ {nz_rpm}")
        st.pyplot(fig, clear_figure=True)
        st.metric("Coverage", f"{score:.1f}%")


# --- Best combo summary ---
best = max(results, key=lambda r: r["coverage"])
st.markdown("---")
st.subheader("🏆 Best RPM Combination")
st.write(f"**Turntable RPM: {best['turntable_rpm']} | Nozzle RPM: {best['nozzle_rpm']}**")
st.metric("✅ Highest Coverage", f"{best['coverage']:.1f}%")
st.pyplot(plot_heatmap(best["grid"], title="Best Coverage Heatmap"), clear_figure=True)

# --- Download options ---
heatmap_df = pd.DataFrame(best["grid"])
csv = heatmap_df.to_csv(index=False)
st.download_button("📥 Download Best Heatmap CSV", csv, file_name="best_heatmap.csv")

buf = BytesIO()
plot_heatmap(best["grid"]).savefig(buf, format="png")
st.download_button("📷 Download Best Heatmap Image", buf.getvalue(), file_name="best_heatmap.png")
