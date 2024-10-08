import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from mpl_toolkits.mplot3d import Axes3D

# 定义船体参数
length = 10  # 船体长度
width = 5    # 船体宽度
height = 3   # 船体高度

# 定义漏水点参数
leak_points = [(5, 2.5, 0)]  # 漏水点位置 (x, y, z)
leak_rate = 0.1  # 漏水速度 (单位：m^3/s)

# 定义水面高度阈值
water_threshold = 2.5  # 水面高度超过这个值时，人会被淹没

# 定义逃离速度
escape_speeds = [0.5, 1.0, 2.0]  # 逃离速度 (单位：m/s)

# 模拟时间步长
dt = 0.1  # 时间步长 (单位：s)

# 初始化水面高度
water_height = 0

# 初始化时间
time = 0

# 初始化逃离时间
escape_times = {speed: None for speed in escape_speeds}

# 初始化淹没时间
submerged_time = None

# 模拟漏水过程
def simulate_leak(length, width, height, leak_points, leak_rate, water_threshold, escape_speeds, dt):
    water_height = 0
    time = 0
    escape_times = {speed: None for speed in escape_speeds}
    submerged_time = None

    water_volume = 0
    water_heights = []
    times = []

    while water_height < height:
        # 计算漏水量
        leak_volume = leak_rate * dt
        water_volume += leak_volume

        # 计算水面高度
        water_height = water_volume / (length * width)

        # 记录时间
        time += dt

        # 记录水面高度和时间
        water_heights.append(water_height)
        times.append(time)

        # 检查是否达到淹没阈值
        if water_height >= water_threshold and submerged_time is None:
            submerged_time = time

        # 检查逃离时间
        for speed in escape_speeds:
            if escape_times[speed] is None and water_height >= height - speed * time:
                escape_times[speed] = time

    return water_heights, times, escape_times, submerged_time

# 可视化结果
def visualize_results(water_heights, times, escape_times, submerged_time):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 绘制船体
    x = [0, length, length, 0, 0, length, length, 0]
    y = [0, 0, width, width, 0, 0, width, width]
    z = [0, 0, 0, 0, height, height, height, height]
    ax.plot(x, y, z, 'b-', label='船体')

    # 绘制水面
    water_x = np.linspace(0, length, 10)
    water_y = np.linspace(0, width, 10)
    water_X, water_Y = np.meshgrid(water_x, water_y)
    water_Z = np.full_like(water_X, water_heights[-1])
    ax.plot_surface(water_X, water_Y, water_Z, color='blue', alpha=0.5, label='水面')

    # 绘制逃离路径
    for speed, escape_time in escape_times.items():
        if escape_time is not None:
            escape_z = np.linspace(0, height, 10)
            escape_x = np.full_like(escape_z, length / 2)
            escape_y = np.full_like(escape_z, width / 2)
            ax.plot(escape_x, escape_y, escape_z, label=f'逃离速度: {speed} m/s')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))

    st.pyplot(fig)

# Streamlit前端界面
def main_box_leaking():
    st.title("船体漏水模型可视化")

    st.write("### 船体参数")
    length = st.slider("船体长度 (m)", 1, 20, 10)
    width = st.slider("船体宽度 (m)", 1, 10, 5)
    height = st.slider("船体高度 (m)", 1, 5, 3)

    st.write("### 漏水点参数")
    leak_rate = st.slider("漏水速度 (m^3/s)", 0.01, 1.0, 0.1)

    st.write("### 逃离速度")
    escape_speeds = [st.slider(f"逃离速度 {i+1} (m/s)", 0.1, 5.0, 0.5 * (i+1)) for i in range(3)]

    if st.button("更新模拟"):
        st.write("### 模拟结果")
        water_heights, times, escape_times, submerged_time = simulate_leak(length, width, height, leak_points, leak_rate, water_threshold, escape_speeds, dt)
        visualize_results(water_heights, times, escape_times, submerged_time)

        st.write(f"淹没时间: {submerged_time:.2f} s")
        for speed, escape_time in escape_times.items():
            st.write(f"逃离速度 {speed} m/s 的逃离时间: {escape_time:.2f} s")

