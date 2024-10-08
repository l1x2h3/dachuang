import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import json

# 定义船只类
class Ship:
    def __init__(self, x, y, vx, vy, shape, turn_rate):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.shape = shape
        self.turn_rate = turn_rate

    def move(self, dt):
        step = max(self.shape[0][0], self.shape[0][1]) * 0.1  # 移动步长为船只大小的10%
        self.x += self.vx * step * dt
        self.y += self.vy * step * dt

    def turn(self, direction, dt):
        if direction == 'left':
            self.vx, self.vy = -self.vy, self.vx
        elif direction == 'right':
            self.vx, self.vy = self.vy, -self.vx

    def get_vertices(self):
        return [(self.x + x, self.y + y) for x, y in self.shape]

# 定义碰撞检测函数（使用分离轴定理）
def detect_collision(ship1, ship2):
    vertices1 = ship1.get_vertices()
    vertices2 = ship2.get_vertices()

    for vertices in [vertices1, vertices2]:
        for i in range(len(vertices)):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % len(vertices)]
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            axis = (-edge[1], edge[0])

            min1, max1 = project(vertices1, axis)
            min2, max2 = project(vertices2, axis)

            if max1 < min2 or max2 < min1:
                return False

    return True

def project(vertices, axis):
    projections = [np.dot(vertex, axis) for vertex in vertices]
    return min(projections), max(projections)


def use_single_step():
    # Streamlit前端
    st.set_page_config(page_title="Ship Collision Simulation", layout="wide")
    st.title("Ship Collision Simulation")

    # 用户输入参数
    st.sidebar.header("Ship Parameters")
    ship1_x = st.sidebar.number_input("Ship 1 Initial X", value=0.0)
    ship1_y = st.sidebar.number_input("Ship 1 Initial Y", value=0.0)
    ship1_vx = st.sidebar.number_input("Ship 1 Velocity X", value=1.0)
    ship1_vy = st.sidebar.number_input("Ship 1 Velocity Y", value=0.0)
    ship1_length = st.sidebar.number_input("Ship 1 Length", value=4.0)
    ship1_width = st.sidebar.number_input("Ship 1 Width", value=2.0)

    ship2_x = st.sidebar.number_input("Ship 2 Initial X", value=10.0)
    ship2_y = st.sidebar.number_input("Ship 2 Initial Y", value=0.0)
    ship2_vx = st.sidebar.number_input("Ship 2 Velocity X", value=-1.0)
    ship2_vy = st.sidebar.number_input("Ship 2 Velocity Y", value=0.0)
    ship2_length = st.sidebar.number_input("Ship 2 Length", value=4.0)
    ship2_width = st.sidebar.number_input("Ship 2 Width", value=2.0)

    turn_distance = st.sidebar.number_input("Turn Distance", value=5.0)
    turn_direction = st.sidebar.selectbox("Turn Direction", ["left", "right"])

    # 创建船只形状（长条六边形）
    def create_ship_shape(length, width):
        half_length = length / 2
        half_width = width / 2
        return [
            (-half_length, -half_width),
            (-half_length, half_width),
            (0, half_width + half_width / 2),
            (half_length, half_width),
            (half_length, -half_width),
            (0, -half_width - half_width / 2)
        ]

    ship1_shape = create_ship_shape(ship1_length, ship1_width)
    ship2_shape = create_ship_shape(ship2_length, ship2_width)

    # 创建船只对象
    ship1 = Ship(ship1_x, ship1_y, ship1_vx, ship1_vy, ship1_shape, 0.1)
    ship2 = Ship(ship2_x, ship2_y, ship2_vx, ship2_vy, ship2_shape, 0.1)

    # 初始化状态
    initial_state = {
        "ship1": {
            "x": ship1_x,
            "y": ship1_y,
            "vx": ship1_vx,
            "vy": ship1_vy,
            "length": ship1_length,
            "width": ship1_width
        },
        "ship2": {
            "x": ship2_x,
            "y": ship2_y,
            "vx": ship2_vx,
            "vy": ship2_vy,
            "length": ship2_length,
            "width": ship2_width
        },
        "turn_distance": turn_distance,
        "turn_direction": turn_direction
    }

    # 点击按钮逐步仿真
    if 'step' not in st.session_state:
        st.session_state.step = 0

    def step():
        dt = 0.1
        ship1.move(dt)
        ship2.move(dt)

        if np.sqrt((ship1.x - ship2.x)**2 + (ship1.y - ship2.y)**2) < turn_distance:
            ship1.turn(turn_direction, dt)
            ship2.turn(turn_direction, dt)

        st.session_state.step += 1

    # 点击按钮恢复到初始状态
    if st.button("Clear", key="clear_button"):
        ship1 = Ship(initial_state["ship1"]["x"], initial_state["ship1"]["y"], initial_state["ship1"]["vx"], initial_state["ship1"]["vy"], ship1_shape, 0.1)
        ship2 = Ship(initial_state["ship2"]["x"], initial_state["ship2"]["y"], initial_state["ship2"]["vx"], initial_state["ship2"]["vy"], ship2_shape, 0.1)
        st.session_state.step = 0

    # 点击按钮存档当前位置和参数信息
    if st.button("Save", key="save_button"):
        current_state = {
            "ship1": {
                "x": ship1.x,
                "y": ship1.y,
                "vx": ship1.vx,
                "vy": ship1.vy,
                "length": ship1_length,
                "width": ship1_width
            },
            "ship2": {
                "x": ship2.x,
                "y": ship2.y,
                "vx": ship2.vx,
                "vy": ship2.vy,
                "length": ship2_length,
                "width": ship2_width
            },
            "turn_distance": turn_distance,
            "turn_direction": turn_direction
        }
        with open("ship_state.json", "w") as f:
            json.dump(current_state, f)
        st.write("State saved to ship_state.json")

    # 点击按钮加载存档
    if st.button("Load", key="load_button"):
        with open("ship_state.json", "r") as f:
            loaded_state = json.load(f)

        ship1 = Ship(loaded_state["ship1"]["x"], loaded_state["ship1"]["y"], loaded_state["ship1"]["vx"], loaded_state["ship1"]["vy"], ship1_shape, 0.1)
        ship2 = Ship(loaded_state["ship2"]["x"], loaded_state["ship2"]["y"], loaded_state["ship2"]["vx"], loaded_state["ship2"]["vy"], ship2_shape, 0.1)
        turn_distance = loaded_state["turn_distance"]
        turn_direction = loaded_state["turn_direction"]
        st.session_state.step = 0

    # 绘制结果
    fig, ax = plt.subplots()
    ax.set_xlim(-10, 10)  # 缩小绘图范围
    ax.set_ylim(-10, 10)  # 缩小绘图范围
    ax.set_aspect('equal')

    ax.add_patch(Polygon(ship1.get_vertices(), fill=False, color='blue', label="Ship 1"))
    ax.add_patch(Polygon(ship2.get_vertices(), fill=False, color='red', label="Ship 2"))

    if detect_collision(ship1, ship2):
        ax.plot(ship1.get_vertices()[0][0], ship1.get_vertices()[0][1], 'ro', label="Collision")
        ax.plot(ship2.get_vertices()[0][0], ship2.get_vertices()[0][1], 'ro')

    ax.legend()
    st.pyplot(fig)

    # 显示碰撞结果
    if detect_collision(ship1, ship2):
        st.write("Collision detected!")
    else:
        st.write("No collision detected.")

    # 横向排列按钮
    button_col1, button_col2, button_col3, button_col4 = st.columns(4)

    with button_col1:
        if st.button("Step", key="step_button"):
            step()

    with button_col2:
        if st.button("Clear", key="clear_button_2"):
            ship1 = Ship(initial_state["ship1"]["x"], initial_state["ship1"]["y"], initial_state["ship1"]["vx"], initial_state["ship1"]["vy"], ship1_shape, 0.1)
            ship2 = Ship(initial_state["ship2"]["x"], initial_state["ship2"]["y"], initial_state["ship2"]["vx"], initial_state["ship2"]["vy"], ship2_shape, 0.1)
            st.session_state.step = 0

    with button_col3:
        if st.button("Save", key="save_button_2"):
            current_state = {
                "ship1": {
                    "x": ship1.x,
                    "y": ship1.y,
                    "vx": ship1.vx,
                    "vy": ship1.vy,
                    "length": ship1_length,
                    "width": ship1_width
                },
                "ship2": {
                    "x": ship2.x,
                    "y": ship2.y,
                    "vx": ship2.vx,
                    "vy": ship2.vy,
                    "length": ship2_length,
                    "width": ship2_width
                },
                "turn_distance": turn_distance,
                "turn_direction": turn_direction
            }
            with open("ship_state.json", "w") as f:
                json.dump(current_state, f)
            st.write("State saved to ship_state.json")

    with button_col4:
        if st.button("Load", key="load_button_2"):
            with open("ship_state.json", "r") as f:
                loaded_state = json.load(f)

            ship1 = Ship(loaded_state["ship1"]["x"], loaded_state["ship1"]["y"], loaded_state["ship1"]["vx"], loaded_state["ship1"]["vy"], ship1_shape, 0.1)
            ship2 = Ship(loaded_state["ship2"]["x"], loaded_state["ship2"]["y"], loaded_state["ship2"]["vx"], loaded_state["ship2"]["vy"], ship2_shape, 0.1)
            turn_distance = loaded_state["turn_distance"]
            turn_direction = loaded_state["turn_direction"]
            st.session_state.step = 0