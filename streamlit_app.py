import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import streamlit.components.v1 as components
import tempfile
import os

st.set_page_config(page_title="Grit Blasting Calculator", layout="wide")
st.title("🔧 Automated Grit Blasting System Calculator")

# Inputs
st.sidebar.header("System Parameters")
nozzle_diameter = st.sidebar.number_input("Nozzle Diameter (in)", 0.1, 1.0, 0.375, 0.01)
air_pressure = st.sidebar.slider("Air Pressure (PSI)", 10, 100, 40)
num_nozzles = st.sidebar.slider("Number of Nozzles", 1, 12, 6)
turntable_diameter = st.sidebar.number_input("Turntable Diameter (in)", 12.0, 60.0, 36.0, 0.5)
flow_rate_per_nozzle = st.sidebar.slider("Flow Rate per Nozzle (lbs/min)", 0.5, 5.0, 2.0, 0.1)
duration = st.sidebar.slider("Blast Duration (seconds)", 5, 60, 30)
abrasive_cost = st.sidebar.number_input("Abrasive Cost per lb (USD)", 0.1, 10.0, 1.2, 0.1)
parts_per_cycle = st.sidebar.slider("Parts per Cycle", 1, 100, 20)

nozzle_arm_radius = turntable_diameter / 4

# Scenario button
tabs = st.tabs(["Scenario 1", "Scenario 2"])

for idx, tab in enumerate(tabs):
    with tab:
        st.subheader(f"📊 Scenario {idx + 1} Results")

        total_flow_rate_min = flow_rate_per_nozzle * num_nozzles
        total_flow_rate_sec = total_flow_rate_min / 60
        abrasive_used = total_flow_rate_sec * duration
        cost_per_cycle = abrasive_used * abrasive_cost
        cost_per_part = cost_per_cycle / parts_per_cycle

        st.metric("Abrasive Used (lbs/cycle)", f"{abrasive_used:.2f}")
        st.metric("Cost per Cycle (USD)", f"${cost_per_cycle:.2f}")
        st.metric("Cost per Part (USD)", f"${cost_per_part:.2f}")

        st.subheader("🌀 Nozzle Coverage Over Turntable")
        theta = np.linspace(0, 2 * np.pi, 100)
        table_r = turntable_diameter / 2
        nozzle_r = nozzle_arm_radius
        table_x = table_r * np.cos(theta)
        table_y = table_r * np.sin(theta)

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.plot(table_x, table_y, label='Turntable (Outer)')
        ax.set_aspect('equal')
        ax.set_xlabel("Inches")
        ax.set_ylabel("Inches")
        ax.set_title("Nozzle Rotation Animation")
        scat = ax.scatter([], [], c='red', label='Nozzles')
        ax.legend()

        def init():
            scat.set_offsets([])
            return scat,

        def update(frame):
            angles = np.linspace(0, 2 * np.pi, num_nozzles, endpoint=False) + frame * np.pi / 30
            x = nozzle_r * np.cos(angles)
            y = nozzle_r * np.sin(angles)
            offsets = np.column_stack((x, y))
            scat.set_offsets(offsets)
            return scat,

        ani = animation.FuncAnimation(fig, update, frames=np.arange(0, 60), init_func=init, blit=True, repeat=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
            ani.save(tmpfile.name, writer='html', fps=10)
            with open(tmpfile.name, "r") as f:
                html = f.read()
            components.html(html, height=500)
            os.unlink(tmpfile.name)

st.caption("Built for automated grit blasting systems optimizing surface finishing performance.")
