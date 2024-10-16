import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from coastline_simulation import simulate_map, plot_map_simulation
import mysql.connector
import hashlib
from PIL import Image
from streamlit_authenticator import Authenticate
from db_config import db_config
from box_leaking import main_box_leaking
from single_step import use_single_step

# 加载图片
coast_image = Image.open("fig/coast.png")
island_image = Image.open("fig/island1.png")
ship_image = Image.open("fig/ship.png")

# 缩放海岸线图片
coast_image = coast_image.resize((100, 100))

# 创建数据库连接
def create_connection():
    return mysql.connector.connect(**db_config)

# 注册用户
def register_user(email, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    connection = create_connection()
    cursor = connection.cursor()
    query = "INSERT INTO users (email, password) VALUES (%s, %s)"
    cursor.execute(query, (email, hashed_password))
    connection.commit()
    cursor.close()
    connection.close()

# 检查用户是否存在
def check_user(email, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE email = %s AND password = %s"
    cursor.execute(query, (email, hashed_password))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result is not None

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
st.title("航行模拟器")

# 导航栏
st.sidebar.title("导航栏")
page = st.sidebar.selectbox("选择页面", ["注册", "登录", "航行条件分析与碰撞模拟", "地图模拟","漏水检测" , "单步模拟"])

# 背景图片




if page == "注册":
    st.title("用户注册")

    # 注册表单
    email = st.text_input("QQ邮箱")
    password = st.text_input("密码", type="password")
    confirm_password = st.text_input("确认密码", type="password")

    if st.button("注册"):
        if password == confirm_password:
            try:
                register_user(email, password)
                st.success("注册成功！请登录")
            except mysql.connector.Error as err:
                st.error(f"注册失败: {err}")
        else:
            st.error("密码不匹配")

elif page == "登录":
    st.title("用户登录")

    # 登录表单
    email = st.text_input("QQ邮箱")
    password = st.text_input("密码", type="password")

    if st.button("登录"):
        if check_user(email, password):
            st.success("登录成功！")
            st.session_state['logged_in'] = True
        else:
            st.error("登录失败，请检查邮箱和密码")

# if 'logged_in' in st.session_state and st.session_state['logged_in']:
if 1:
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

    elif page == "漏水检测":
        main_box_leaking()

    elif page == "单步模拟":
        use_single_step()

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
            map_data, trajectories, destinations, start_times, end_times, islands = simulate_map(num_ships, weather, ship_type, speed)

            # 绘制动态图
            fig = go.Figure()

            # 添加海岸线
            fig.add_layout_image(
                dict(
                    source=coast_image,
                    xref="x",
                    yref="y",
                    x=0,
                    y=0,
                    sizex=100,
                    sizey=100,
                    xanchor="left",
                    yanchor="bottom",
                    sizing="stretch",
                    opacity=1,
                    layer="below"
                )
            )

            # 添加岛礁
            for island in islands:
                fig.add_layout_image(
                    dict(
                        source=island_image,
                        xref="x",
                        yref="y",
                        x=island[0],
                        y=island[1],
                        sizex=1,
                        sizey=1,
                        xanchor="center",
                        yanchor="middle",
                        sizing="stretch",
                        opacity=1,
                        layer="below"
                    )
                )

            # 添加船只轨迹
            for i in range(trajectories.shape[1]):
                x_coords = trajectories[:, i, 0]
                y_coords = trajectories[:, i, 1]
                fig.add_trace(go.Scatter(x=x_coords, y=y_coords, mode='lines+markers', name=f'Ship {i+1}', marker=dict(size=5)))

            # 添加目的地
            for i in range(destinations.shape[0]):
                fig.add_trace(go.Scatter(x=[destinations[i, 0]], y=[destinations[i, 1]], mode='markers', name=f'Destination {i+1}', marker=dict(size=10, color='red')))

            fig.update_layout(title="地图与船只航行模拟", xaxis_title="X坐标", yaxis_title="Y坐标", xaxis=dict(range=[0, 100]), yaxis=dict(range=[0, 100]))

            # 生成动态图
            frames = []
            for step in range(trajectories.shape[0]):
                frame = go.Frame(
                    data=[
                        go.Scatter(
                            x=trajectories[step, :, 0],
                            y=trajectories[step, :, 1],
                            mode='markers',
                            marker=dict(size=10, color='blue')
                        )
                    ]
                )
                frames.append(frame)

            fig.frames = frames

            # 添加动画控制
            fig.update_layout(
                updatemenus=[
                    dict(
                        type="buttons",
                        showactive=False,
                        buttons=[
                            dict(
                                label="Play",
                                method="animate",
                                args=[None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}]
                            ),
                            dict(
                                label="Pause",
                                method="animate",
                                args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}]
                            )
                        ]
                    )
                ]
            )

            st.plotly_chart(fig)

            # 添加标注信息
            st.write("标注信息：")
            cols = st.columns(5)  # 创建5列
            cols[0].write("- 黑色区域：海岸线")
            cols[1].write("- 灰色区域：岛礁")
            cols[2].write("- 浅灰色区域：浅水区")
            cols[3].write("- 蓝色线条：船只轨迹")
            cols[4].write("- 红色点：船只目的地")

            # 显示出发时间和到达时间
            st.write("船只出发时间和到达时间：")
            cols1 = st.columns(num_ships)
            for i in range(num_ships):
                cols1[i].write(f"船只 {i+1}: 出发时间 {start_times[i]:.2f} 秒, 到达时间 {end_times[i]:.2f} 秒")
                # st.write(f"船只 {i+1}: 出发时间 {start_times[i]:.2f} 秒, 到达时间 {end_times[i]:.2f} 秒")

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