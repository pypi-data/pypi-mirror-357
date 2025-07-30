from .base import close, array2float
from logging import getLogger
from typing import Optional
import numpy as np

logger = getLogger(__name__)

@array2float
def angle_3p_countclockwise(start: np.ndarray, center: np.ndarray, end: np.ndarray) -> float:
    """
    计算三维空间中三点构成的角度，按照右手系从 (start - center) 向量到 (end - center) 向量的旋转角度

    Returns: `float`, 弧度值，`[0, 2*pi)`
    """
    vec1 = start - center
    vec2 = end - center
    
    # 检查零向量
    norm_vec1 = float(np.linalg.norm(vec1))
    norm_vec2 = float(np.linalg.norm(vec2))
    if close(norm_vec1, 0) or close(norm_vec2, 0):
        logger.warning(f"无法计算角度：向量不能为零向量：{vec1}, {vec2}")
        raise ValueError(f"无法计算角度：向量不能为零向量：{vec1}, {vec2}")
    
    u1 = vec1 / norm_vec1
    u2 = vec2 / norm_vec2
    # 计算点积 (cos(theta) 的分子)
    dot_product = np.dot(u1, u2)
    
    # 计算叉积向量 (sin(theta) 的方向和大小)
    cross_product_vec = np.cross(u1, u2)
    
    # 叉积向量的模长 (sin(theta) 的绝对值)
    sin_abs = float(np.linalg.norm(cross_product_vec))

    # 检查三点共线
    if close(sin_abs, 0):
        # 如果叉积模长为0，说明 u1 和 u2 共线
        if dot_product >= 0: # 同向
            return 0.0
        else: # 反向
            return np.pi

    # 在局部二维平面内计算角度
    # x_prime = u1 (归一化的 vec1)
    # z_prime = cross_product_vec / sin_abs (归一化的法向量)
    # y_prime = np.cross(z_prime, x_prime) (与 x_prime 垂直，且在平面内)
    # 将 u2 投影到这个局部坐标系
    local_x_axis = u1
    x_component_in_local_plane = np.dot(u2, local_x_axis)
    y_component_in_local_plane = np.dot(u2, np.cross(cross_product_vec / sin_abs, local_x_axis))
    angle_rad = np.arctan2(y_component_in_local_plane, x_component_in_local_plane)
    
    if angle_rad < 0:
        angle_rad += 2 * np.pi
    
    return angle_rad

@array2float
def point_3p_countclockwise(start: np.ndarray, center: np.ndarray, angle_rad: float, axis_vec: Optional[np.ndarray] = None) -> np.ndarray:
    """
    根据始点、中心点和角度，按逆时针方向计算终点
    
    - `start`: 始点
    - `center`: 中心点
    - `angle_rad`: 角度（弧度），逆时针为正
    - `axis_vec`: 旋转轴向量（默认使用 z 轴）
    
    Returns: 终点坐标
    """
    vec1 = start - center

    if axis_vec is None:
        axis_vec = np.array([0.0, 0.0, 1.0])
    else:
        # 确保轴向量是单位向量
        norm_axis = np.linalg.norm(axis_vec)
        if not close(float(norm_axis), 0): # 使用 close 来判断是否为零向量
            axis_vec = axis_vec / norm_axis
        else:
            logger.warning("旋转轴向量不能为零向量")
            raise ValueError("旋转轴向量不能为零向量")
    
    norm_vec1 = float(np.linalg.norm(vec1))
    if close(norm_vec1, 0):
        # 始点与中心重合，直接返回始点
        logger.warning(f"始点与中心重合：{start}, {center}")
        return start.copy()
    
    # 对于2D情况的特殊处理
    if len(vec1) == 2:
        # 2D旋转矩阵
        cos_angle = np.cos(angle_rad)
        sin_angle = np.sin(angle_rad)
        rotation_matrix = np.array([
            [cos_angle, -sin_angle],
            [sin_angle, cos_angle]
        ])
        rotated_vec = rotation_matrix @ vec1
        return center + rotated_vec
    
    # 3D情况：使用Rodrigues旋转公式
    if len(vec1) == 3:
        
        # Rodrigues旋转公式
        cos_angle = np.cos(angle_rad)
        sin_angle = np.sin(angle_rad)
        
        rotated_vec = (vec1 * cos_angle + np.cross(axis_vec, vec1) * sin_angle + axis_vec * np.dot(axis_vec, vec1) * (1 - cos_angle))
        return center + rotated_vec
    
    raise ValueError(f"不支持的维度：{len(vec1)}")