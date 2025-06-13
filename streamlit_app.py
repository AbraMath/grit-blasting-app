import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time

# --- Page Setup ---
st.set_page_config(page_title="Grit Blasting Visualizer", layout="wide")
st.title("🌀 Grit Blasting Nozzle Path Visualization (25x25 Grid)")

# --- Parameters ---
turntable_radius = 18  # inches (36" diameter / 2)
nozzle_ring_radius = turntable_radius / 4
nozzle_ring_offset = turntable_radius / 2
num_nozzles = 6
nozzle_diameter = 2  # 2-inch diameter impact

# --- User Controls ---
st.sidebar.header("Simulation Settings")
turntable_rpm = st.sidebar.slider("Turntable RPM", 0, 60, 2, 1)
nozzle_rpm = st.sidebar.slider("Nozzle Assembly RPM", 0, 60, 22, 1)
run_seconds = st.sidebar.slider("Blast Duration (s)", 1, 30, 10)
fps = 30
run_batch = st.sidebar.checkbox("Run batch simulation (auto-sweep RPMs)")

# --- Common Setup ---
total_frames = int(run_seconds * fps)
grid_size = 25
x_edges = np.linspace(-turntable_radius, turntable_radius, grid_size + 1)
y_edges = np.linspace(-turntable_radius, turntable_radius, grid_size + 1)
xx, yy = np.meshgrid(
    (x_edges[:-1] + x_edges[1:]) / 2,
    (y_edges[:-1] + y_edges[1:]) / 2,
    indexing='ij'
)
mask = xx**2 + yy**2 <= turntable_radius**2

# --- Batch Mode ---
if run_batch:
    st.markdown("### 🔄 Running batch simulation...")
    rpm_steps = [0, 2, 4, 6, 8]
    nozzle_steps = [0, 11, 22, 33, 44]
    results = []
    progress = st.progress(0.0)
    total_tests = len(rpm_steps) * len(nozzle_steps)

    for i, turn_rpm in enumerate(rpm_steps):
        for j, noz_rpm in enumerate(nozzle_steps):
            heatmap = np.zeros((grid_size, grid_size))
            nozzle_angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)

            for frame in range(total_frames):
                t = frame / fps
                turntable_angle = 2 * np.pi * (turn_rpm / 60) * t
                nozzle_angle = -2 * np.pi * (noz_rpm / 60) * t

                local_x = nozzle_ring_radius * np.cos(nozzle_angles + nozzle_angle)
                local_y = nozzle_ring_radius * np.sin(nozzle_angles + nozzle_angle)
                center_x = nozzle_ring_offset
                center_y = 0

                nozzle_x = local_x + center_x
                nozzle_y = local_y + center_y

                impact_x = nozzle_x * np.cos(turntable_angle) - nozzle_y * np.sin(turntable_angle)
                impact_y = nozzle_x * np.sin(turntable_angle) + nozzle_y * np.cos(turntable_angle)

                hist, _, _ = np.histogram2d(impact_x, impact_y, bins=[x_edges, y_edges])
                heatmap += hist

            hit_count = np.count_nonzero(heatmap[mask])
            total_cells = np.sum(mask)
            coverage_score = (hit_count / total_cells) * 100
            results.append((turn_rpm, noz_rpm, coverage_score))

            progress.progress((i * len(nozzle_steps) + j + 1) / total_tests)

    # --- Show Results ---
    st.subheader("📊 RPM Coverage Matrix")
    df = pd.DataFrame(
        np.zeros((len(rpm_steps), len(nozzle_steps))),
        index=[f"T:{r}" for r in rpm_steps],
        columns=[f"N:{n}" for n in nozzle_steps],
    )

    for turn_rpm, noz_rpm, score in results:
        df.loc[f"T:{turn_rpm}", f"N:{noz_rpm}"] = score

    best_idx = np.unravel_index(np.argmax(df.values), df.shape)
    best_turn = rpm_steps[best_idx[0]]
    best_noz = nozzle_steps[best_idx[1]]
    best_score = df.values[best_idx]

    st.dataframe(df.style.background_gradient(cmap='YlGnBu').format("{:.1f}%"))
    st.success(f"✅ Best Coverage: {best_score:.1f}% at Turntable {best_turn} RPM, Nozzle {best_noz} RPM")

    # Optional CSV export
    csv = df.to_csv().encode("utf-8")
    st.download_button("📥 Download Coverage Matrix (CSV)", data=csv, file_name="blast_coverage_matrix.csv", mime="text/csv")

# --- Single Animation Mode ---
else:
    if st.button("▶️ Play Animation"):
        st.subheader("🎬 Nozzle Path Simulation")
        heatmap = np.zeros((grid_size, grid_size))
        nozzle_angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)

        fig, ax = plt.subplots()
        ax.set_xlim(-turntable_radius, turntable_radius)
        ax.set_ylim(-turntable_radius, turntable_radius)
        ax.set_aspect("equal")
        ax.set_title("Nozzle Impact Path")

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
            heatmap += hist

            for x, y in zip(impact_x, impact_y):
                circ = plt.Circle((x, y), radius=nozzle_diameter / 2, color='blue', alpha=0.1)
                ax.add_patch(circ)

            if frame % 10 == 0:
                ax.plot()  # optional: refresh every 10 frames

        st.pyplot(fig)

        hit_count = np.count_nonzero(heatmap[mask])
        total_cells = np.sum(mask)
        coverage_score = (hit_count / total_cells) * 100
        st.success(f"🧮 Coverage Score: {coverage_score:.1f}%")
