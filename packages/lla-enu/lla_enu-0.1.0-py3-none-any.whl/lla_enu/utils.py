import numpy as np

# 地球平均半径（单位：米）
EARTH_RADIUS = 6371000

def distance_enu(lon1, lat1, alt1, lon2, lat2, alt2):
    """
    平面近似法计算两个经纬高坐标之间的不同分量的距离（东向、北向和总距离），单位为米。

    :param lon1: 起始点经度（度）
    :param lat1: 起始点纬度（度）
    :param alt1: 起始点高度（米）
    :param lon2: 终点经度（度）
    :param lat2: 终点纬度（度）
    :param alt2: 终点点高度（米）
    :return: np.array([东向距离、北向距离、垂直距离])
    """

    # 将纬度和经度转换为弧度
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    # 计算纬度和经度的差值（弧度）
    d_lat = lat2_rad - lat1_rad
    d_lon = lon2_rad - lon1_rad

    # 北向距离
    north_distance = EARTH_RADIUS * d_lat

    # 东向距离
    avg_lat_rad = (lat1_rad + lat2_rad) / 2
    east_distance = EARTH_RADIUS * np.cos(avg_lat_rad) * d_lon

    # 高度距离
    alt_distance = alt2 - alt1

    return np.array([north_distance, east_distance, alt_distance])

def distance_lla(lon1, lat1, alt1, lon2, lat2, alt2):
    """
    平面近似法计算两个经纬高坐标之间的距离，单位为米。

    :param lon1: 起始点经度（度）
    :param lat1: 起始点纬度（度）
    :param alt1: 起始点高度（米）
    :param lon2: 终点经度（度）
    :param lat2: 终点纬度（度）
    :param alt2: 终点点高度（米）
    :return: np.array([新经度, 新纬度, 新海拔])
    """
    enu = distance_enu(lon1, lat1, alt1, lon2, lat2, alt2)
    dis = np.linalg.norm(enu)
    return dis

def lla_add_enu(lon, lat, alt, east, north, up):
    """
    平面近似法计算经纬高坐标偏移东北天一定距离后的新坐标。

    :param lon: 起始点经度（度）
    :param lat: 起始点纬度（度）
    :param alt: 起始点高度（米）
    :param east: 东向距离（米）
    :param north: 北向距离（米）
    :param up: 天向距离（米）
    :return: np.array([新经度（度）, 新纬度（度）, 新海拔（米）])
    """

    # 1. 计算每米纬度变化量(固定)
    lat_change_per_m = 180 / (np.pi * (EARTH_RADIUS + alt + up))  # 单位：度/米

    # 2. 计算每米经度变化量(依赖纬度)
    lat_rad = np.radians(lat)
    lon_change_per_m = 180 / (np.pi * (EARTH_RADIUS + alt + up) * np.cos(lat_rad))  # 单位：度/米

    # 3. 计算新坐标
    new_lat = lat + north * lat_change_per_m
    new_lon = lon + east * lon_change_per_m
    new_alt = alt + up

    return np.array([new_lon, new_lat, new_alt])


def vector_angle(vec1, vec2):
    """
    计算两个三维向量之间的夹角

    :param vec1: 向量1
    :param vec2: 向量2
    :return: 向量夹角（弧度）
    """
    a = np.array(vec1)
    norm_a = a / np.linalg.norm(a)
    b = np.array(vec2)
    norm_b = b / np.linalg.norm(b)

    angle = np.arccos(np.dot(norm_a, norm_b))
    return angle