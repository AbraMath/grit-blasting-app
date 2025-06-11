import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

# --- App Setup ---
st.set_page_config(page_title="Batch Grit Blasting Optimizer", layout="wide")
st.title("📊 Grit Blasting Batch Optimizer (25x25 Grid)")

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

# --- Batch Run Controls ---
run_seconds = st.slider("Run Time (seconds)", 5, 30, 10, step=1)
step = st.select_slider("RPM Step Size", options=[1, 5, 10], value=5)
run_button = st.button("🚀 Run Batch Simulation")

if run_button:
