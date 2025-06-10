import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

st.set_page_config(page_title="Grit Blasting Visualizer", layout="centered")
st.title("🎯 Grit Blasting - Nozzle Motion on Stationary Ring")

# --- Parameters ---
turntable_radius = 18  # inches
nozzle_ring_radius = turntable_radius / 4
nozzle_ring_offset = turntable_radius / 2  # fixed offset from center
num_nozzles = 6

turntable_rpm = st.slider("Turntable RPM", 1, 60, 20)
nozzle_rpm = st.slider("Nozzle Ring RPM", 1, 60, 20)
trail_length = st.slider("Trail Length (frames)", 1, 150, 20)

st.markdown("Press ▶️ to animate. Nozzles rotate around fixed ring center. Trails rotate with the turntable.")

if st.button("▶️ Play Animation"):
    frame_placeholder = st.empty()
    nozzle_offsets = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)
    trail_history = []

    for frame in range(100):
        t = frame / 30  # simulate ~30 FPS
        turntable_angle = 2 * np.pi * (turntable_rpm / 60) * t
        nozzle_angle = 2 * np.pi * (nozzle_rpm / 60) * t

        # Nozzle ring center is fixed
        ring_cx, ring_cy = nozzle_ring_offset, 0

        # --- Impact points (rotate on turntable) ---
        impact_x, impact_y = [], []
        # --- Nozzle positions (visual only, rotate around ring center) ---
        nozzle_viz_x, nozzle_viz_y = [], []

        for offset in nozzle_offsets:
            angle = nozzle_angle + offset

            # Nozzle visual position
            nvx = ring_cx + nozzle_ring_radius * np.cos(angle)
            nvy = ring_cy + nozzle_ring_radius * np.sin(angle)
            nozzle_viz_x.append(nvx)
            nozzle_viz_y.append(nvy)

            # Impact point position (same as above, but rotated with turntable)
            rx = nvx * np.cos(turntable_angle) - nvy * np.sin(turntable_angle)
            ry = nvx * np.sin(turntable_angle) + nvy * np.cos(turntable_angle)
            impact_x.append(rx)
            impact_y.append(ry)

        # Store trail
        trail_history.append((impact_x.copy(), impact_y.copy()))
        if len(trail_his_
