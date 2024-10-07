import numpy as np
import plotly.graph_objects as go
from PIL import Image

# 加载图片
coast_image = Image.open("fig/coast.png")
island_image = Image.open("fig/island1.png")
ship_image = Image.open("fig/ship.png")

# 缩放海岸线图片
coast_image = coast_image.resize((100, 100))

# 模拟地图
def simulate_map(num_ships, weather, ship_type, speed):
    # 初始化地图
    map_size = 100
    map_data = np.zeros((map_size, map_size))

    # 生成岛礁
    num_islands = 5
    islands = []
    for _ in range(num_islands):
        x, y = np.random.randint(10, 90, 2)
        islands.append((x, y))

    # 初始化船只位置和速度
    positions = np.random.rand(num_ships, 2) * 80 + 10
    velocities = np.random.rand(num_ships, 2) * speed

    # 设置目的地
    destinations = np.random.rand(num_ships, 2) * 80 + 10

    # 模拟时间步长
    dt = 0.1
    num_steps = 50  # 调整为 50 步，每步 0.1 秒，总共 5 秒

    # 存储轨迹
    trajectories = [positions]

    # 存储出发时间和到达时间
    start_times = np.zeros(num_ships)
    end_times = np.zeros(num_ships)

    for step in range(num_steps):
        # 更新位置
        for i in range(num_ships):
            if step == 0:
                start_times[i] = step * dt

            # 计算到目的地的方向
            direction = destinations[i] - positions[i]
            direction /= np.linalg.norm(direction)
            velocities[i] = direction * speed

            # 绕开障碍物
            for island in islands:
                obstacle_pos = np.array(island)
                dist = np.linalg.norm(positions[i] - obstacle_pos)
                if dist < 10:  # 假设障碍物距离为10
                    # 绕开障碍物
                    velocities[i] += (positions[i] - obstacle_pos) / dist

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

        # 更新到达时间
        for i in range(num_ships):
            if np.linalg.norm(positions[i] - destinations[i]) < 1:
                end_times[i] = step * dt

    return map_data, np.array(trajectories), destinations, start_times, end_times, islands

# 绘制地图和船只轨迹
def plot_map_simulation(map_data, trajectories, destinations, start_times, end_times, islands):
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
    return fig, start_times, end_times