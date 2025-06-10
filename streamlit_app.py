import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

# Set page config (must be FIRST)
st.set_page_config(page_title="Grit Blasting Visualizer", layout="centered")

st.title("🧼 Grit Blasting Nozzle Animation (Autoplay)")

# --- Parameters ---
radius = 18  # inches (36" diameter / 2)
nozzle_radius = radius / 2  # nozzles rotate around midpoint (18"/2)
num_nozzles = 6

turntable_rpm = st.slider("Turntable RPM", 1, 60, 20)
nozzle_rpm = st.slider("Nozzle Assembly RPM", 1, 60, 20)

st.markdown("Press the button below to start auto-animation.")

if st.button("▶️ Play Animation"):
    frame_placeholder = st.empty()

    # Angle positions of nozzles
    angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)

    for frame in range(60):  # simulate 2 seconds at ~30 FPS
        t = frame / 30
        turntable_angle = 2 * np.pi * (turntable_rpm / 60) * t
        nozzle_angle = -2 * np.pi * (nozzle_rpm / 60) * t

        # Nozzle positions in local coordinate system
        x = nozzle_radius * np.cos(angles + nozzle_angle)
        y = nozzle_radius * np.sin(angles + nozzle_angle)

        # Rotate the whole assembly with turntable
        rotated_x = x * np.cos(turntable_angle) - y * np.sin(turntable_angle)
        rotated_y = x * np.sin(turntable_angle) + y * np.cos(turntable_angle)

        # Plot
        fig, ax = plt.subplots()
