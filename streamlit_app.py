import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import streamlit.components.v1 as components

# App title
st.title("Grit Blasting Machine Visualization")
st.subheader("Simulate Nozzle and Turntable Rotation")

# User Inputs
col1, col2 = st.columns(2)

with col1:
    turntable_rpm = st.slider("Turntable RPM", 1, 60, 30)
    turntable_radius = st.number_input("Turntable Diameter (in)", 36.0) / 2
    blast_time = st.slider("Blast Duration (seconds)", 10, 60, 30)

with col2:
    nozzle_rpm = st.slider("Nozzle Assembly RPM", 1, 60, 30)
    num_nozzles = st.slider("Number of Nozzles", 1, 12, 6)
    nozzle_r = st.number_input("Nozzle Radius from Center (in)", turntable_radius / 2)

st.markdown("---")
st.markdown("### Live Visualization")

# Create figure
fig, ax = plt.subplots()
ax.set_xlim(-turntable_radius - 5, turntable_radius + 5)
ax.set_ylim(-turntable_radius - 5, turntable_radius + 5)
ax.set_aspect('equal')
ax.set_title("Top-Down View of Nozzle and Table Rotation")
turntable_circle = plt.Circle((0, 0), turntable_radius, fill=False, linestyle='--')
ax.add_artist(turntable_circle)

# Initial positions of nozzles
angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)
x = nozzle_r * np.cos(angles)
y = nozzle_r * np.sin(angles)
scat = ax.scatter(x, y, c='blue', label='Nozzles')

# Update function
def update(frame):
    tt_angle = 2 * np.pi * (turntable_rpm / 60) * (frame / 30)
    nozzle_angle = -2 * np.pi * (nozzle_rpm / 60) * (frame / 30)

    angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)
    x = nozzle_r * np.cos(angles + nozzle_angle)
    y = nozzle_r * np.sin(angles + nozzle_angle)

    rotated_x = x * np.cos(tt_angle) - y * np.sin(tt_angle)
    rotated_y = x * np.sin(tt_angle) + y * np.cos(tt_angle)

    offsets = np.column_stack((rotated_x, rotated_y))
    scat.set_offsets(offsets)
    return scat,

# Init function
def init():
    angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False)
    x = nozzle_r * np.cos(angles)
    y = nozzle_r * np.sin(angles)
    offsets = np.column_stack((x, y))
    scat.set_offsets(offsets)
    return scat,

ani = animation.FuncAnimation(
    fig, update, frames=np.arange(0, 60),
    init_func=init, blit=True, repeat=True
)

# Display the animation in Streamlit
st.pyplot(fig)

st.markdown("---")
st.markdown("### Summary")

st.write(f"**Nozzle Assembly Radius:** {nozzle_r:.2f} inches")
st.write(f"**Turntable Radius:** {turntable_radius:.2f} inches")
st.write(f"**Nozzles:** {num_nozzles}")
st.write(f"**Estimated Blast Coverage Time:** {blast_time} seconds")

st.success("Adjust parameters to compare different scenarios.")

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

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
ax.set_xlim(-radius - 5, radius_
