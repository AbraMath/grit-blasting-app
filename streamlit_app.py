import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Must be first
st.set_page_config(page_title="Grit Blasting Visualizer with Offset Nozzles", layout="wide")
st.title("🌀 Grit Blasting Nozzle Path Coverage Comparison (with Fixed Nozzle Ring Center)")

# --- Parameters ---
turntable_radius = 18  # inches (36" diameter / 2)
nozzle_ring_radius = turntable_radius / 4  # ring of nozzles is smaller
nozzle_ring_offset = turntable_radius / 2  # fixed offset from center (9 inches)
num_nozzles = 6
frames = 100
grid_res = 1  # inch per cell
grid_size = int(2 * turntable_radius / grid_res)
trail_length = 20  # fixed for speed

# --- UI Controls ---
st.sidebar.header("Simulation Settings")
turntable_rpms = st.sidebar.multiselect("Turntable RPMs", list(range(5, 65, 5)), default=[20, 40])
nozzle_rpms = st.sidebar.multiselect("Nozzle RPMs", list(range(5, 65, 5)), default=[20, 40])
threshold = st.sidebar.slider("Heatmap Threshold (min hits to count)", 1, 50, 5)
run_batch = st.sidebar.button("▶️ Run RPM Batch Simulation")

# --- Grid setup ---
x = np.linspace(-turntable_radius, turntable_radius, grid_size)
y = np.linspace(-turntable_radius, turntable_radius, grid_size)
X, Y = np.meshgrid(x, y)

def simulate_coverage(turn_rpm, noz_rpm):
    impact_map = np.zeros_like(X)

    nozzle_angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)

    for frame in range(frames):
        t = frame / 30  # time in seconds (30 FPS)
        turntable_angle = 2 * np.pi * (turn_rpm / 60) * t
        nozzle_angle = -2 * np.pi * (noz_rpm / 60) * t

        # Nozzle local positions around ring center
        local_x = nozzle_ring_radius * np.cos(nozzle_angles + nozzle_angle)
        local_y = nozzle_ring_radius * np.sin(nozzle_angles + nozzle_angle)

        # Fixed ring center
        center_x = nozzle_ring_offset
        center_y = 0

        # Absolute nozzle tip positions
        nozzle_x = local_x + center_x
        nozzle_y = local_y + center_y

        # Rotate with turntable
        impact_x = nozzle_x * np.cos(turntable_angle) - nozzle_y * np.sin(turntable_angle)
        impact_y = nozzle_x * np.sin(turntable_angle) + nozzle_y * np.cos(turntable_angle)

        # Convert to grid and accumulate hits
        for ix, iy in zip(impact_x, impact_y):
            gx = int((ix + turntable_radius) / grid_res)
            gy = int((iy + turntable_radius) / grid_res)
            if 0 <= gx < grid_size and 0 <= gy < grid_size:
                impact_map[gy, gx] += 1

    return impact_map

def compute_coverage_score(map_data, threshold):
    total = np.sum((X**2 + Y**2) <= turntable_radius**2)
    covered = np.sum((map_data >= threshold) & ((X**2 + Y**2) <= turntable_radius**2))
    return round((covered / total) * 100, 1)

# --- Run batch comparison ---
if run_batch:
    st.subheader("🔍 RPM Coverage Comparison")

    cols = st.columns(len(nozzle_rpms))

    for i, noz_rpm in enumerate(nozzle_rpms):
        with cols[i]:
            for turn_rpm in turntable_rpms:
                impact_map = simulate_coverage(turn_rpm, noz_rpm)
                score = compute_coverage_score(impact_map, threshold)

                fig, ax = plt.subplots()
                ax.set_title(f"TT: {turn_rpm} RPM, Nozzle: {noz_rpm} RPM\nCoverage: {score}%")
                heatmap = np.ma.masked_where((X**2 + Y**2) > turntable_radius**2, impact_map)
                im = ax.imshow(heatmap, extent=(-turntable_radius, turntable_radius, -turntable_radius, turntable_radius),
                               origin='lower', cmap='hot', interpolation='nearest')
                ax.set_xlabel("X (inches)")
                ax.set_ylabel("Y (inches)")
                plt.colorbar(im, ax=ax, label="Hit Count")

                st.pyplot(fig)
