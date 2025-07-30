from __future__ import annotations

from pydantic import Field
from ..base import ArgsModelBase
from typing import TYPE_CHECKING, Union, Literal

type Number = Union[float, int]

if TYPE_CHECKING:
    from ..point import Point
    from ..vector import Vector
    from .line import LineSegment, Ray, InfinityLine

type LineConcrete = Union["LineSegment", "Ray", "InfinityLine"]

class PPArgs(ArgsModelBase):
    construct_type: Literal["PP"] = "PP"
    point1: Point
    point2: Point

class PVArgs(ArgsModelBase):
    construct_type: Literal["PV"] = "PV"
    start: Point
    vector: Vector

class TranslationLVArgs(ArgsModelBase):
    construct_type: Literal["TranslationLV"] = "TranslationLV"
    line: LineConcrete = Field(discriminator='line_type')
    vector: Vector

class VerticalPLArgs(ArgsModelBase):
    construct_type: Literal["VerticalPL"] = "VerticalPL"
    point: Point
    line: LineConcrete = Field(discriminator='line_type')

class ParallelPLArgs(ArgsModelBase):
    construct_type: Literal["ParallelPL"] = "ParallelPL"
    point: Point
    line: LineConcrete = Field(discriminator='line_type')
    distance: Number

# 所有单线参数模型的联合类型
type LineConstructArgs = Union[
    PPArgs, PVArgs, TranslationLVArgs, VerticalPLArgs, ParallelPLArgs
]

LineConstructArgsList = [
    PPArgs, PVArgs, TranslationLVArgs, VerticalPLArgs, ParallelPLArgs
]

type LineConstructType = Literal[
    "PP", "PV", "TranslationLV", "VerticalPL", "ParallelPL"
]