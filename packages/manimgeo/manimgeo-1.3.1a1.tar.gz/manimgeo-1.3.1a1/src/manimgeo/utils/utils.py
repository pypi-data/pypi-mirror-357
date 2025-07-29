from __future__ import annotations

from typing import Iterable

class GeoUtils:
    GEO_PRINT_EXC: bool = True
    
    @staticmethod
    def flatten(iterable: Iterable):
        """展平对象"""
        for item in iterable:
            if isinstance(item, list):
                yield from GeoUtils.flatten(item)
            else:
                yield item

    from ..components import BaseGeometry
    @staticmethod
    def print_dependencies(root: "BaseGeometry", depth: int = 0, max_depth: int = 20):
        """绘制依赖关系"""
        from ..utils.output import color_text, generate_color_from_id
        
        if root is None:
            print("  "*depth + "· None")
            return
            
        if depth > max_depth:
            print("  "*depth + "· ... (max depth reached)")
            return
        
        name_str = f" - ({root.name})" if hasattr(root, 'name') and root.name else ""
        print("  "*depth + f"· {color_text(type(root).__name__, *generate_color_from_id(root))}{name_str}")
        
        if not hasattr(root, 'dependents'):
            return
            
        for dep in root.dependents:
            GeoUtils.print_dependencies(dep, depth+1, max_depth)

    @staticmethod
    def set_debug(debug: bool = True):
        """输出错误信息"""
        GeoUtils.GEO_PRINT_EXC = debug