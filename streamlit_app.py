import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Config
st.set_page_config(page_title="Blast Coverage Optimizer", layout="wide")
st.title("🧠 Optimizing Grit Blasting Coverage")

# Constants
turntable_radius = 18  # inches
nozzle_ring_radius = turntable_radius / 4
nozzle_ring_offset = turntable_radius / 2
num_nozzles = 6
nozzle_diameter = 2  # inches
resolution = 1  # 1 inch per pixel
frames = 100  # simulate ~3.3 seconds

# Simulation grid
grid_size = int(turntable_radius * 2 / resolution) + 1
grid = np.zeros((grid_size, grid_size))
X, Y = np.meshgrid(
    np.linspace(-turntable_radius, turntable_radius, grid_size),
    np.linspace(-turntable_radius, turntable_radius, grid_size)
)
distance_map = np.sqrt(X**2 + Y**2)
within_turntable = distance_map <= turntable_radius

# Precompute nozzle angles
nozzle_angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)

# Evaluate combinations
rpms = list(range(5, 65, 5))  # 5–60 in steps of 5
results = []

with st.spinner("Simulating RPM combinations..."):
    for turntable_rpm in rpms:
        for nozzle_rpm in rpms:
            coverage = np.zeros_like(grid, dtype=float)

            for frame in range(frames):
                t = frame / 30
                tt_angle = 2 * np.pi * (turntable_rpm / 60) * t
                nozzle_angle = -2 * np.pi * (nozzle_rpm / 60) * t

                center_x = nozzle_ring_offset * np.cos(nozzle_angle)
                center_y = nozzle_ring_offset * np.sin(nozzle_angle)

                local_x = nozzle_ring_radius * np.cos(nozzle_angles)
                local_y = nozzle_ring_radius * np.sin(nozzle_angles)
                x = local_x + center_x
                y = local_y + center_y

                rot_x = x * np.cos(tt_angle) - y * np.sin(tt_angle)
                rot_y = x * np.sin(tt_angle) + y * np.cos(tt_angle)

                for nx, ny in zip(rot_x, rot_y):
                    dx = X - nx
                    dy = Y - ny
                    nozzle_mask = dx**2 + dy**2 <= (nozzle_diameter / 2) ** 2
                    coverage += nozzle_mask.astype(float)

            # Normalize and calculate score
            covered_area = np.sum((coverage > 0) & within_turntable)
            total_area = np.sum(within_turntable)
            coverage_score = covered_area / total_area

            results.append({
                "tt_rpm": turntable_rpm,
                "noz_rpm": nozzle_rpm,
                "score": coverage_score,
                "coverage_map": coverage.copy(),
            })

# Sort and display top results
results.sort(key=lambda x: -x['score'])
st.subheader("📊 Top RPM Combinations by Coverage Score")

cols = st.columns(3)
for i, res in enumerate(results[:6]):
    fig, ax = plt.subplots()
    ax.set_title(f"TT: {res['tt_rpm']} RPM, Nozzle: {res['noz_rpm']} RPM\nScore: {res['score']:.2%}")
    ax.imshow(res['coverage_map'], cmap='hot', extent=[-18, 18, -18, 18], origin='lower')
    ax.set_xticks([])
    ax.set_yticks([])
    cols[i % 3].pyplot(fig)

st.success("Done! You can adjust resolution or frames for finer analysis.")
