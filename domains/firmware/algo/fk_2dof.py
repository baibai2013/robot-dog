"""正向运动学:(hip_deg, knee_deg) → 足端位置 (x, y)。"""
from __future__ import annotations

import math

from .ik_2dof import L1, L2


def fk_2dof(hip_deg: float, knee_deg: float) -> tuple[float, float]:
    """已知关节角度,求足端坐标。"""
    hip_rad = math.radians(90.0 - hip_deg)
    # tibia 相对 femur 的角度
    tibia_rad_global = hip_rad + math.radians(180.0 - knee_deg) - math.pi
    x = L1 * math.cos(hip_rad) + L2 * math.cos(tibia_rad_global)
    y = L1 * math.sin(hip_rad) + L2 * math.sin(tibia_rad_global)
    return x, y


if __name__ == "__main__":
    for h, k in [(90, 0), (90, 90), (60, 45), (120, 45)]:
        x, y = fk_2dof(h, k)
        print(f"hip={h}° knee={k}° → ({x:.1f}, {y:.1f})")
