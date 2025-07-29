from __future__ import annotations

from pydantic import Field, ValidationError
from .base_pydantic import BaseModelN
from typing import List, Optional, Any, Generic

from .base_adapter import GeometryAdapter

# 日志
import logging
logger = logging.getLogger(__name__)

from .base_argsmodel import _ArgsModelT

class BaseGeometry(BaseModelN, Generic[_ArgsModelT]):
    """几何对象基类"""
    name: str = Field(description="几何对象名称")
    attrs: List[str] = Field(default_factory=list, description="几何对象属性列表", init=False)
    
    adapter: GeometryAdapter[Any] = Field(description="几何对象参数适配器", init=False)
    dependencies: List[BaseGeometry] = Field(default_factory=list, description="当前几何对象直接依赖的其他几何对象列表", init=False)
    dependents: List[BaseGeometry] = Field(default_factory=list, description="依赖于当前几何对象的其他几何对象列表", init=False)
    on_error: bool = Field(default=False, description="是否在更新过程中发生错误", init=False)

    def __repr__(self):
        # 原始 BaseModelN 的 __repr__ 方法开销巨大，改为简化输出
        return f"{self.__class__.__name__}(name={self.name}, adapter={self.adapter}, attrs={self.attrs}, dependencies={len(self.dependencies)}, dependents={len(self.dependents)}, on_error={self.on_error})"

    def get_name(self, default_name: str):
        """以统一方式设置几何对象名称"""
        if default_name != "":
            return default_name
        else:
            return f"{type(self).__name__}[{self.adapter.construct_type}]@{id(self) % 100000}"

    def add_dependent(self, obj: BaseGeometry):
        """
        添加依赖于当前对象的下游对象
        
        - `obj`: 下游依赖对象
        """
        if obj not in self.dependents:
            self.dependents.append(obj)

    def remove_dependent(self, obj: Optional[BaseGeometry]):
        """
        移除依赖于当前对象的下游对象
        
        - `obj`: 需要移除的下游依赖对象，如果为 None 则移除所有依赖
        """
        if obj is None:
            self.dependents.clear()
        else:
            if obj in self.dependents:
                self.dependents.remove(obj)

    def _add_dependency(self, obj: BaseGeometry):
        """
        添加当前对象直接依赖的上游几何对象

        - `obj`: 上游依赖对象
        """
        if obj not in self.dependencies:
            self.dependencies.append(obj)
            obj.add_dependent(self) # 同时将当前对象添加到上游的 dependents 列表中

    def _remove_dependency(self, obj: Optional[BaseGeometry]):
        """
        移除当前对象直接依赖的上游几何对象

        - `obj`: 需要移除的上游依赖对象，如果为 None 则移除所有依赖
        """
        if obj is None:
            for dep in self.dependencies:
                dep.remove_dependent(self)
            self.dependencies.clear()
        else:
            if obj in self.dependencies:
                self.dependencies.remove(obj)
                obj.remove_dependent(self)

    def board_update_msg(self, on_error: bool = False):
        """
        向所有下游依赖项发出更新信号
        
        - `on_error`: 是否在更新过程中发生错误，默认为 False
        """
        for dep in self.dependents:
            dep.update() # 递归更新下游
            dep.on_error = on_error

    def _extract_dependencies_from_args(self, args_model: _ArgsModelT):
        """
        从 Pydantic 参数模型中提取依赖的几何对象，并添加到当前对象的依赖列表中
        
        - `args_model`: Pydantic 参数模型实例
        """
        # 调用 ArgsModelBase 的 _get_deps 方法获取依赖几何对象列表
        deps = args_model._get_deps()
        # 添加到当前的依赖列表中
        for dep in deps:
            if isinstance(dep, BaseGeometry):
                self._add_dependency(dep)
            else:
                logger.warning(f"参数模型 {args_model.__class__.__name__} 中包含非几何对象依赖: {dep}，将被忽略")

    def update(self, new_args_model: Optional[_ArgsModelT] = None):
        """
        执行当前对象的更新
        
        - `new_args_model`: 如果需要更新构造参数，则传入新的 Pydantic 参数模型实例。如果传入，会尝试替换 adapter.args

        注意不能更改参数模型的类型，只能更改参数模型的实例
        """
        if new_args_model:
            try:
                # 检查传入的模型类型是否与当前适配器期望的 args 类型兼容
                # 简化的检查，更严格的检查可能需要比较 TypeVar ArgsModel
                if not isinstance(new_args_model, type(self.adapter.args)):
                    raise TypeError(f"传入的参数模型类型 {type(new_args_model).__name__} 与当前适配器期望的类型 {type(self.adapter.args).__name__} 不匹配。")
                
                self.adapter.args = new_args_model
            
            except (TypeError, ValidationError) as e:
                logger.error(f"更新对象 {self.name} 的参数失败: {e}")
                self.board_update_msg(True)
                self.on_error = True
                return
            
            except Exception as e:
                logger.error(f"更新对象 {self.name} 的参数时发生未知错误: {e}")
                self.board_update_msg(True)
                self.on_error = True
                return
        
        try:
            # 调用适配器进行计算
            self.adapter()
            # 将参数从适配器绑定到几何对象
            self.adapter.bind_attributes(self, self.attrs)
            
        except Exception as e:
            logger.warning(f"节点 {self.name} ({type(self).__name__}) 计算失败", exc_info=True)
            
            # 传播更新消息并标记错误
            self.board_update_msg(True)
            self.on_error = True
            raise e
        
        # 成功更新，清除错误标记
        self.on_error = False
        # 向下游广播更新信息
        self.board_update_msg()
