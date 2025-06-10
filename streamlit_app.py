import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

# Must be first
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

st.markdown("Press ▶️ to see how the nozzles revolve around a fixed center and how trails map onto the rotating turntable.")

if st.button("▶️ Play Animation"):
    frame_placeholder = st.empty()

    nozzle_angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)
    trail_history = []

    for frame in range(100):  # simulate ~3 seconds at 30 FPS
        t = frame / 30
        turntable
