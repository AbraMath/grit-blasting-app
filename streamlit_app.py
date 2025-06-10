import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

# Set page config (must be first)
st.set_page_config(page_title="Grit Blasting Visualizer", layout="centered")

st.title("🧼 Grit Blasting Nozzle Animation (Autoplay)")

# --- Parameters ---
radius = 18  # inches (36"/2)
nozzle_radius = radius / 2  # nozzles rotate at half radius
num_nozzles = 6

turntable_rpm = st.slider("Turntable RPM", 1, 60, 20)
nozzle_rpm = st.slider("Nozzle Assembly RPM", 1, 60, 20)

st.markdown("Press the button below to start auto-animation.")

if st.button("▶️ Play Animation"):
    frame_placeholder = st.empty()
    plot_placeholder = st.empty()
    
    # Angle positions of nozzles
    angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)

    for frame in range(60):
        # Calculate angles based on RPM and time
        t = frame / 30  # simulating ~2 seconds total (30 fps)
        turntable_angle = 2 * np.pi * (turntable_rpm / 60) * t
        nozzle_angle = -2 * np.pi * (nozzle_rpm / 60) * t

        # Nozzle positions before rotation
        x = nozzle_radius * np.cos(angles + nozzle_angle)
        y = nozzle_radius * np.sin(angles + nozzle_angle)

        # Rotate with turntable
        rotated_x = x * np.cos(turntable_angle) - y * np.sin(tu*_*_
