import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import contextily as ctx
from shapely.geometry import LineString, Point
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import numpy as np

# === 1. 广州 -> 深圳 路线 ===
guangzhou = (113.2644, 23.1291)
shenzhen = (114.0579, 22.5431)
line = LineString([guangzhou, shenzhen])

# === 2. 插值出轨迹点 ===
def interpolate_route(line: LineString, num_points: int) -> list[Point]:
    distances = np.linspace(0, line.length, num_points)
    return [line.interpolate(distance) for distance in distances]

points = interpolate_route(line, 100)
route_gdf = gpd.GeoSeries([line], crs="EPSG:4326")

# === 3. 火车图标（红色矩形模拟） ===
train_icon = Image.new("RGBA", (20, 10), (255, 0, 0, 255))
train_img = OffsetImage(train_icon, zoom=0.5)

# === 4. 设置画布和坐标系 ===
fig, ax = plt.subplots(figsize=(10, 8))
plt.tight_layout()

def draw_frame(i):
    ax.clear()
    route_gdf.to_crs(epsg=3857).plot(ax=ax, color='gray', linewidth=3, label="High-Speed Rail")

    # 当前火车点（WGS84 -> Web Mercator）
    pt = gpd.GeoSeries([points[i]], crs="EPSG:4326").to_crs(epsg=3857).geometry.iloc[0]
    ab = AnnotationBbox(train_img, (pt.x, pt.y), frameon=False)
    ax.add_artist(ab)

    # 添加底图
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, crs="EPSG:3857")

    # 添加城市标注（转换投影后写死位置或重新投影点）
    ax.text(1.261e7, 2.676e6, "Guangzhou", fontsize=12, ha='right', va='bottom')
    ax.text(1.270e7, 2.565e6, "Shenzhen", fontsize=12, ha='left', va='top')

    ax.set_xlim(1.258e7, 1.273e7)
    ax.set_ylim(2.53e6, 2.69e6)
    ax.set_title(f"Train from Guangzhou to Shenzhen\nFrame {i+1}/100", fontsize=14)

# === 5. 输出为 GIF 或 MP4 ===
ani = animation.FuncAnimation(fig, draw_frame, frames=len(points), interval=100, repeat=False)

# --- 保存为 GIF ---
ani.save("train_map_with_basemap.gif", writer="pillow")

# --- 或保存为 MP4（需要 ffmpeg）---
# ani.save("train_map_with_basemap.mp4", writer="ffmpeg", fps=10)
