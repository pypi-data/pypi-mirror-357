"""
Point 几何类
"""

from __future__ import annotations

from pydantic import Field, model_validator
from typing import TYPE_CHECKING, Any, List
import numpy as np

from ..base import BaseGeometry
from .adapter import PointAdapter
from .args import *

if TYPE_CHECKING:
    from ..angle import Angle
    from ..line import Line, LineSegment, Ray, InfinityLine
    from ..vector import Vector
    from ..circle import Circle
    type ConcreteLine = Union[LineSegment, Ray, InfinityLine]

from .intersections import (
    LL as IntersectionLL,
    LCir as IntersectionLCir,
    CirCir as IntersectionCirCir,
    ConcreteIntType
)

class Point(BaseGeometry):
    attrs: List[str] = Field(default=["coord"], description="点属性列表", init=False)
    coord: np.ndarray = Field(default=np.zeros(2), description="点坐标", init=False)
    args: PointConstructArgs = Field(discriminator='construct_type', description="点构造参数")

    @model_validator(mode='before')
    @classmethod
    def set_adapter_before_validation(cls, data: Any) -> Any:
        """在验证前设置 adapter 字段"""
        if isinstance(data, dict) and 'args' in data:
            # 假设 args 已经是 Pydantic 模型或可以被 PointAdapter 接受
            data['adapter'] = PointAdapter(args=data['args'])
        return data
    
    @property
    def construct_type(self) -> PointConstructType:
        return self.args.construct_type
    
    def model_post_init(self, __context: Any):
        """模型初始化后，更新名字并添加依赖关系"""
        # 实例化 PointAdapter，传入 PointConstructArgs
        self.adapter = PointAdapter(args=self.args)
        self.name = self.get_name(self.name)
        # 添加依赖关系
        self._extract_dependencies_from_args(self.args)
        self.update() # 首次计算
    
    def set_coord(self, coord: np.ndarray):
        """
        更新 `PointFree` 或 `PointConstraint` 坐标
        坐标设置仅对于 Free 构造有效，其他构造类型将抛出 ValueError
        """
        if self.construct_type not in ["Free"]:
            raise ValueError(f"不可设置非 FreePoint 点坐标 (当前构造类型: {self.construct_type})")
        
        new_args = FreeArgs(coord=coord)
        self.update(new_args)

    # 构造方法
    
    @classmethod
    def Free(cls, coord: np.ndarray, name: str = "") -> Point:
        """
        构造自由点（叶子节点）

        `coord`: 点坐标
        """
        return Point(
            name=name,
            args=FreeArgs(coord=coord)
        )
    
    @classmethod
    def Constraint(cls, coord: np.ndarray, name: str = "") -> Point:
        """
        构造约束点（非叶子节点）

        `coord`: 坐标
        """
        return Point(
            name=name,
            args=ConstraintArgs(coord=coord)
        )

    @classmethod
    def MidPP(cls, point1: Point, point2: Point, name: str = "") -> Point:
        """
        构造两点中点

        `point1`: 第一个点  
        `point2`: 第二个点
        """
        return Point(
            name=name,
            args=MidPPArgs(point1=point1, point2=point2)
        )
    
    @classmethod
    def MidL(cls, line: LineSegment, name: str = "") -> Point:
        """
        构造线段中点

        `line`: 线段对象
        """
        return Point(
            name=name,
            args=MidLArgs(line=line)
        )
    
    @classmethod
    def ExtensionPP(cls, start: Point, through: Point, factor: Number, name: str = "") -> Point:
        """
        构造比例延长（位似）点

        `start`: 起点  
        `through`: 经过点  
        `factor`: 延长比例, 1 为恒等延长
        """
        return Point(
            name=name,
            args=ExtensionPPArgs(start=start, through=through, factor=factor)
        )
    
    @classmethod
    def AxisymmetricPL(cls, point: Point, line: Line, name: str = "") -> Point:
        """
        构造轴对称点

        `point`: 原始点  
        `line`: 对称轴线
        """
        return Point(
            name=name,
            args=AxisymmetricPLArgs(point=point, line=line)
        )
    
    @classmethod
    def VerticalPL(cls, point: Point, line: Line, name: str = "") -> Point:
        """
        构造垂足点

        `point`: 原始基准点  
        `line`: 目标直线
        """
        return Point(
            name=name,
            args=VerticalPLArgs(point=point, line=line)
        )
    
    @classmethod
    def ParallelPL(cls, point: Point, line: Line, distance: Number, name: str = "") -> Point:
        """
        构造平行线上一点

        `point`: 基准点  
        `line`: 平行基准线  
        `distance`: 沿平行方向的绝对距离
        """
        return Point(
            name=name,
            args=ParallelPLArgs(point=point, line=line, distance=distance)
        )
    
    @classmethod
    def InversionPCir(cls, point: Point, circle: Circle, name: str = "") -> Point:
        """
        构造反演点

        `point`: 原始点  
        `circle`: 反演基准圆
        """
        return Point(
            name=name,
            args=InversionPCirArgs(point=point, circle=circle)
        )
    
    @classmethod
    def IntersectionLL(cls, line1: ConcreteLine, line2: ConcreteLine, regard_infinite: bool = False, name: str = "") -> Point:
        """
        构造两线交点

        `line1`: 第一条线  
        `line2`: 第二条线  
        `regard_infinite`: 是否视为无限长直线
        """
        return Point(
            name=name,
            args=IntersectionsArgs(int_type=IntersectionLL(line1=line1, line2=line2, as_infinity=regard_infinite))
        )
    
    @classmethod
    def TranslationPV(cls, point: Point, vector: Vector, name: str = "") -> Point:
        """
        构造平移点

        `point`: 原始点  
        `vector`: 平移向量
        """
        return Point(
            name=name,
            args=TranslationPVArgs(point=point, vector=vector)
        )
    
    @classmethod
    def CentroidPPP(cls, point1: Point, point2: Point, point3: Point, name: str = "") -> Point:
        """
        构造三角形重心

        `point1`: 第一个顶点  
        `point2`: 第二个顶点  
        `point3`: 第三个顶点
        """
        return Point(
            name=name,
            args=CentroidPPPArgs(point1=point1, point2=point2, point3=point3)
        )
    
    @classmethod
    def CircumcenterPPP(cls, point1: Point, point2: Point, point3: Point, name: str = "") -> Point:
        """
        构造三角形外心

        `point1`: 第一个顶点  
        `point2`: 第二个顶点  
        `point3`: 第三个顶点
        """
        return Point(
            name=name,
            args=CircumcenterPPPArgs(point1=point1, point2=point2, point3=point3)
        )
    
    @classmethod
    def IncenterPPP(cls, point1: Point, point2: Point, point3: Point, name: str = "") -> Point:
        """
        构造三角形内心

        `point1`: 第一个顶点  
        `point2`: 第二个顶点  
        `point3`: 第三个顶点
        """
        return Point(
            name=name,
            args=IncenterPPPArgs(point1=point1, point2=point2, point3=point3)
        )
    
    @classmethod
    def OrthocenterPPP(cls, point1: Point, point2: Point, point3: Point, name: str = "") -> Point:
        """
        构造三角形垂心

        `point1`: 第一个顶点  
        `point2`: 第二个顶点  
        `point3`: 第三个顶点
        """
        return Point(
            name=name,
            args=OrthocenterPPPArgs(point1=point1, point2=point2, point3=point3)
        )
    
    @classmethod
    def Cir(cls, circle: Circle, name: str = "") -> Point:
        """
        构造圆心

        `circle`: 圆对象
        """
        return Point(
            name=name,
            args=CirArgs(circle=circle)
        )
    
    @classmethod
    def RotatePPA(cls, point: Point, center: Point, angle: Angle, name: str = "") -> Point:
        """
        构造旋转点

        `point`: 原始点  
        `center`: 旋转中心  
        `angle`: 旋转角度
        """
        return Point(
            name=name,
            args=RotatePPAArgs(point=point, center=center, angle=angle)
        )