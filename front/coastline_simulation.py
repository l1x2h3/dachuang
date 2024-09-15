import numpy as np
import plotly.graph_objects as go

# 模拟地图
def simulate_map(num_ships, weather, ship_type, speed):
    # 初始化地图
    map_size = 100
    map_data = np.zeros((map_size, map_size))

    # 生成海岸线
    for i in range(map_size):
        for j in range(map_size):
            if i < 10 or i > 90 or j < 10 or j > 90:
                map_data[i, j] = 1  # 海岸线用 1 表示

    # 生成岛礁
    num_islands = 5
    for _ in range(num_islands):
        x, y = np.random.randint(10, 90, 2)
        map_data[x-2:x+2, y-2:y+2] = 2  # 岛礁用 2 表示

    # 生成浅水区
    num_shallow_areas = 3
    for _ in range(num_shallow_areas):
        x, y = np.random.randint(10, 90, 2)
        map_data[x-5:x+5, y-5:y+5] = 3  # 浅水区用 3 表示

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
            for j in range(map_size):
                for k in range(map_size):
                    if map_data[j, k] in [1, 2, 3]:
                        obstacle_pos = np.array([j, k])
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

            # 地图障碍物检测
            if map_data[int(positions[i, 0]), int(positions[i, 1])] in [1, 2, 3]:
                velocities[i] = -velocities[i]

        # 存储轨迹
        trajectories.append(positions.copy())

        # 更新到达时间
        for i in range(num_ships):
            if np.linalg.norm(positions[i] - destinations[i]) < 1:
                end_times[i] = step * dt

    return map_data, np.array(trajectories), destinations, start_times, end_times

# 绘制地图和船只轨迹
def plot_map_simulation(map_data, trajectories, destinations, start_times, end_times):
    fig = go.Figure()

    # 添加地图
    fig.add_trace(go.Heatmap(z=map_data, colorscale='Greys', showscale=False))

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