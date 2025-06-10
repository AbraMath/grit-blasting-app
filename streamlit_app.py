import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

# Set Streamlit config
st.set_page_config(page_title="Grit Blasting Visualizer", layout="centered")

st.title("🌀 Grit Blasting Nozzle Path Visualization")

# --- Parameters ---
turntable_radius = 18  # inches (36" diameter / 2)
nozzle_ring_radius = turntable_radius / 4  # radius of the nozzle ring
nozzle_ring_offset = turntable_radius / 2  # distance from turntable center
num_nozzles = 6

# UI Controls
turntable_rpm = st.slider("Turntable RPM", 1, 60, 20)
nozzle_rpm = st.slider("Nozzle Ring RPM", 1, 60, 20)
trail_length = st.slider("Trail Length (frames)", 1, 150, 20)

st.markdown("Press ▶️ to visualize nozzle movement around a stationary center and their impact on a spinning turntable.")

if st.button("▶️ Play Animation"):
    frame_placeholder = st.empty()

    nozzle_angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)
    trail_history = []

    for frame in range(100):
        t = frame / 30  # time in seconds (assuming 30 FPS)
        turntable_angle = 2 * np.pi * (turntable_rpm / 60) * t
        nozzle_angle = -2 * np.pi * (nozzle_rpm / 60) * t

        # Calculate nozzle positions (relative to nozzle ring center)
        local_x = nozzle_ring_radius * np.cos(nozzle_angles + nozzle_angle)
        local_y = nozzle_ring_radius * np.sin(nozzle_angles + nozzle_angle)

        # Fixed nozzle ring center
        center_x = nozzle_ring_offset
        center_y = 0

        nozzle_x = local_x + center_x
        nozzle_y = local_y + center_y

        # Rotate impact points with turntable
        imp
