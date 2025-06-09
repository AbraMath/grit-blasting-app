import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# MUST BE FIRST Streamlit command!
st.set_page_config(page_title="Grit Blasting Visualizer", layout="centered")

st.title("Grit Blasting Machine Simulation")
st.markdown("Top-down animation of turntable and counter-rotating nozzles.")

# --- INPUTS ---
col1, col2 = st.columns(2)
with col1:
    turntable_rpm = st.slider("Turntable RPM", 1, 60, 20, key="turntable_rpm")
    diameter = st.number_input("Turntable Diameter (in)", 1.0, 100.0, 36.0, key="diameter")
    blast_time = st.slider("Blast Duration (sec)", 5, 60, 30, key="blast_time")
with col2:
    nozzle_rpm = st.slider("Nozzle Assembly RPM", 1, 60, 40, key="nozzle_rpm")
    num_nozzles = st.slider("Number of Nozzles", 1, 12, 6, key="num_nozzles")
    nozzle_radius = diameter / 4

radius = diameter / 2

# --- FRAME SELECTION ---
frame = st.slider("Animation Frame", 0, 60, 0, key="frame_slider")

# --- CALCULATIONS ---
turntable_angle = 2 * np.pi * (turntable_rpm / 60) * (frame / 30)
nozzle_angle = -2 * np.pi * (nozzle_rpm / 60) * (frame / 30)

# Nozzle positions
angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)
x = nozzle_radius * np.cos(angles + nozzle_angle)
y = nozzle_radius * np.sin(angles + nozzle_angle)

# Rotate nozzles with turntable
rotated_x = x * np.cos(turntable_angle) - y * np.sin(turntable_angle)
rotated_y = x * np.sin(turntable_angle) + y * np.cos(turntable_angle)

# --- PLOTTING ---
fig, ax = plt.subplots()
ax.set_xlim(-radius - 5, radius + 5)
ax.set_ylim(-radius - 5, radius + 5)
ax.set_aspect('equal')
ax.set_title("Frame-by-Frame Rotation")

# Draw turntable
turntable_circle = plt.Circle((0, 0), radius, fill=False, linestyle='--', linewidth=1)
ax.add_patch(turntable_circle)

# Draw nozzle positions
ax.scatter(rotated_x, rotated_y, c='blue', label='Nozzles')

# Show plot in Streamlit
st.pyplot(fig)

# --- INFO ---
st.markdown("---")
st.markdown(f"**Frame:** {frame} | **Turntable Angle:** {np.degrees(turntable_angle):.2f}° | **Nozzle Angle:** {np.degrees(nozzle_angle):.2f}°")
st.markdown("Use the slider to step through time and visualize nozzle + table movement.")
