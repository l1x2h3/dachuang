import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from coastline_simulation import simulate_map, plot_map_simulation

# 模拟模型函数，返回事故发生的可能性及影响
def predict_accident_probability(weather, ship_type, speed):
    weather_impact = {'sunny': 0.1, 'cloudy': 0.2, 'rainy': 0.5, 'stormy': 0.8}
    ship_type_impact = {'cargo': 0.2, 'passenger': 0.3, 'fishing': 0.4, 'military': 0.1}
    speed_impact = speed / 50.0

    probability = weather_impact[weather] + ship_type_impact[ship_type] + speed_impact
    impact = probability * 10  # 假设影响是概率的10倍

    return probability, impact

# 模拟船只运动和碰撞
def simulate_ships(num_ships, weather, ship_type, speed):
    # 初始化船只位置和速度
    positions = np.random.rand(num_ships, 2) * 100
    velocities = np.random.rand(num_ships, 2) * speed

    # 模拟时间步长
    dt = 0.1
    num_steps = 50  # 调整为 50 步，每步 0.1 秒，总共 5 秒

    # 存储轨迹
    trajectories = [positions]

    for _ in range(num_steps):
        # 更新位置
        positions += velocities * dt

        # 简单的碰撞检测和处理
        for i in range(num_ships):
            for j in range(i + 1, num_ships):
                dist = np.linalg.norm(positions[i] - positions[j])
                if dist < 10:  # 假设碰撞距离为10
                    # 简单的反弹处理
                    velocities[i] = -velocities[i]
                    velocities[j] = -velocities[j]

        # 存储轨迹
        trajectories.append(positions.copy())

    return np.array(trajectories)

# Streamlit应用
st.set_page_config(layout="wide", page_title="航行模拟器", page_icon="fig/logo.png")

# 添加网站名称和Logo
# st.title("航行模拟器")

# 导航栏
st.sidebar.title("导航栏")
page = st.sidebar.selectbox("选择页面", ["航行条件分析与碰撞模拟", "地图模拟"])

if page == "航行条件分析与碰撞模拟":
    st.title("航行条件分析与碰撞模拟")

    # 输入参数
    st.sidebar.header("输入参数")
    weather = st.sidebar.selectbox("天气条件", ["sunny", "cloudy", "rainy", "stormy"])
    ship_type = st.sidebar.selectbox("船舶类型", ["cargo", "passenger", "fishing", "military"])
    speed = st.sidebar.slider("航行速度 (节)", min_value=0.0, max_value=50.0, step=0.1)
    num_ships = st.sidebar.slider("船只数量", min_value=2, max_value=10, step=1)

    # 分析按钮
    if st.sidebar.button("分析"):
        # 调用模型函数
        probability, impact = predict_accident_probability(weather, ship_type, speed)

        # 展示结果
        st.header("分析结果")
        st.write(f"事故发生的可能性: {probability:.2f}")
        st.write(f"事故影响: {impact:.2f}")

        # 模拟船只运动和碰撞
        trajectories = simulate_ships(num_ships, weather, ship_type, speed)

        # 绘制轨迹图
        fig = go.Figure()

        for i in range(num_ships):
            x_coords = trajectories[:, i, 0]
            y_coords = trajectories[:, i, 1]
            fig.add_trace(go.Scatter(x=x_coords, y=y_coords, mode='lines+markers', name=f'Ship {i+1}'))

        fig.update_layout(title="船只轨迹与碰撞模拟", xaxis_title="X坐标", yaxis_title="Y坐标")
        st.plotly_chart(fig)

elif page == "地图模拟":
    st.title("地图模拟")

    # 输入参数
    st.sidebar.header("输入参数")
    weather = st.sidebar.selectbox("天气条件", ["sunny", "cloudy", "rainy", "stormy"])
    ship_type = st.sidebar.selectbox("船舶类型", ["cargo", "passenger", "fishing", "military"])
    speed = st.sidebar.slider("航行速度 (节)", min_value=0.0, max_value=50.0, step=0.1)
    num_ships = st.sidebar.slider("船只数量", min_value=2, max_value=10, step=1)

    # 模拟按钮
    if st.sidebar.button("模拟"):
        # 模拟地图和船只运动
        map_data, trajectories, destinations, start_times, end_times = simulate_map(num_ships, weather, ship_type, speed)

        # 绘制地图和船只轨迹
        fig, start_times, end_times = plot_map_simulation(map_data, trajectories, destinations, start_times, end_times)
        st.plotly_chart(fig)

        # 添加标注信息
        st.write("标注信息：")
        st.write("- 黑色区域：海岸线")
        st.write("- 灰色区域：岛礁")
        st.write("- 浅灰色区域：浅水区")
        st.write("- 蓝色线条：船只轨迹")
        st.write("- 红色点：船只目的地")

        # 显示出发时间和到达时间
        st.write("船只出发时间和到达时间：")
        for i in range(num_ships):
            st.write(f"船只 {i+1}: 出发时间 {start_times[i]:.2f} 秒, 到达时间 {end_times[i]:.2f} 秒")

        # 显示出发点和目的地的坐标
        st.write("出发点和目的地的坐标：")
        data = {
            "船只编号": [f"船只 {i+1}" for i in range(num_ships)],
            "出发点 X坐标": [trajectories[0, i, 0] for i in range(num_ships)],
            "出发点 Y坐标": [trajectories[0, i, 1] for i in range(num_ships)],
            "目的地 X坐标": [destinations[i, 0] for i in range(num_ships)],
            "目的地 Y坐标": [destinations[i, 1] for i in range(num_ships)]
        }
        df = pd.DataFrame(data)
        st.table(df)