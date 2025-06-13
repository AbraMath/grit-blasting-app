import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(page_title="Optimized Grit Blasting RPMs", layout="wide")
st.title("🧠 Optimizing RPM Combinations for Blast Coverage")

# --- Parameters ---
turntable_radius = 30  # inches (36" diameter / 2)
nozzle_ring_radius = turntable_radius / 4
nozzle_ring_offset = turntable_radius / 2
num_nozzles = 6
impact_radius = 1  # 2 inch diameter (1 inch radius)
fps = 30
run_seconds = 10
total_frames = fps * run_seconds

# RPM ranges to evaluate
tt_rpm_range = range(0, 9)  # 0–8
nz_rpm_range = range(0, 45)  # 0–44

# Create grid
grid_size = 25
x_edges = np.linspace(-turntable_radius, turntable_radius, grid_size + 1)
y_edges = np.linspace(-turntable_radius, turntable_radius, grid_size + 1)
xx, yy = np.meshgrid((x_edges[:-1] + x_edges[1:]) / 2,
                     (y_edges[:-1] + y_edges[1:]) / 2, indexing='ij')
mask = xx**2 + yy**2 <= turntable_radius**2
cell_centers = np.stack([xx, yy], axis=-1)

best_score = -1
best_combo = (0, 0)
coverage_scores = []

progress = st.progress(0, text="Evaluating combinations...")

for i, tt_rpm in enumerate(tt_rpm_range):
    for j, nz_rpm in enumerate(nz_rpm_range):
        heatmap = np.zeros((grid_size, grid_size))
        nozzle_angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)

        for frame in range(total_frames):
            t = frame / fps
            turntable_angle = 2 * np.pi * (tt_rpm / 60) * t
            nozzle_angle = -2 * np.pi * (nz_rpm / 60) * t

            local_x = nozzle_ring_radius * np.cos(nozzle_angles + nozzle_angle)
            local_y = nozzle_ring_radius * np.sin(nozzle_angles + nozzle_angle)
            nozzle_x = local_x + nozzle_ring_offset
            nozzle_y = local_y

            # Apply turntable rotation
            impact_x = nozzle_x * np.cos(turntable_angle) - nozzle_y * np.sin(turntable_angle)
            impact_y = nozzle_x * np.sin(turntable_angle) + nozzle_y * np.cos(turntable_angle)

            for x, y in zip(impact_x, impact_y):
                distances = np.sqrt((xx - x)**2 + (yy - y)**2)
                heatmap += (distances <= impact_radius).astype(int)

        score = np.count_nonzero(heatmap[mask]) / np.sum(mask) * 100
        coverage_scores.append((tt_rpm, nz_rpm, score))
        if score > best_score:
            best_score = score
            best_combo = (tt_rpm, nz_rpm)
            best_heatmap = heatmap.copy()

        progress.progress(((i * len(nz_rpm_range) + j + 1) / (len(tt_rpm_range) * len(nz_rpm_range))),
                          text=f"Checking TT: {tt_rpm} RPM, NZ: {nz_rpm} RPM")

# --- Show Results ---
st.success(f"✅ Best Coverage: {best_score:.1f}% with Turntable {best_combo[0]} RPM and Nozzle {best_combo[1]} RPM")

fig, ax = plt.subplots()
ax.set_title("Best Coverage Heatmap (25x25 Grid)")
extent = [-turntable_radius, turntable_radius, -turntable_radius, turntable_radius]
cax = ax.imshow(np.flipud(best_heatmap.T), extent=extent, cmap='hot', origin='lower')
fig.colorbar(cax, ax=ax, label="Blast Intensity")
ax.set_xlabel("X (inches)")
ax.set_ylabel("Y (inches)")
ax.set_aspect('equal')
st.pyplot(fig)

# Show full table of RPM combos
if st.checkbox("Show all RPM coverage scores"):
    df = pd.DataFrame(coverage_scores, columns=["Turntable RPM", "Nozzle RPM", "Coverage %"])
    st.dataframe(df.sort_values("Coverage %", ascending=False).reset_index(drop=True))
