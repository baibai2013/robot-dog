"""2-DOF IK 求解器:髋关节 + 膝关节(robot-dog v1)。

坐标系: 原点在髋关节中心,X 朝前,Y 朝下。
- l1 = femur 长度 = 80mm
- l2 = tibia 长度 = 70mm

调用方:固件主循环或上位机通过串口/BLE 下发 (x, y) 目标足端位置,
        求解 (hip_deg, knee_deg) 后写舵机。
"""
from __future__ import annotations

import math


L1 = 80.0   # femur 长度 (mm)
L2 = 70.0   # tibia 长度 (mm)


def ik_2dof(x: float, y: float, l1: float = L1, l2: float = L2) -> tuple[float, float]:
    """足端目标位置 (x, y) → (hip_deg, knee_deg)。

    返回的角度范围匹配 firmware/src/leg_pwm.c 里的安全限位:
      HIP   ∈ [60, 120]   (90 = 站立正前,30 度幅度对应 ±30°)
      KNEE  ∈ [0, 90]     (0 = 完全伸直)

    Raises:
        ValueError: 目标超出 (l1+l2) 球半径或落在 (l1-l2) 死区内。
    """
    d2 = x * x + y * y
    d = math.sqrt(d2)
    if d > l1 + l2:
        raise ValueError(f"target ({x},{y}) out of reach: d={d:.1f} > l1+l2={l1+l2}")
    if d < abs(l1 - l2):
        raise ValueError(f"target ({x},{y}) inside dead zone: d={d:.1f} < |l1-l2|={abs(l1-l2)}")

    cos_knee = (l1 * l1 + l2 * l2 - d2) / (2 * l1 * l2)
    cos_knee = max(-1.0, min(1.0, cos_knee))
    knee_inner = math.degrees(math.acos(cos_knee))   # 0=完全伸直时为 180°,这里返回的是 femur-tibia 的内夹角
    knee_deg = 180.0 - knee_inner                    # 转成 0=直、90=直角的舵机角

    alpha = math.atan2(y, x)
    cos_hip = (l1 * l1 + d2 - l2 * l2) / (2 * l1 * d)
    cos_hip = max(-1.0, min(1.0, cos_hip))
    beta = math.acos(cos_hip)
    hip_deg = 90.0 - math.degrees(alpha - beta)      # 90 度对齐固件中位

    return hip_deg, knee_deg


if __name__ == "__main__":
    # 自检:三组目标点应能解
    for tx, ty in [(80.0, 60.0), (60.0, 80.0), (40.0, 100.0)]:
        try:
            h, k = ik_2dof(tx, ty)
            print(f"target=({tx},{ty}) → hip={h:.1f}° knee={k:.1f}°")
        except ValueError as exc:
            print(f"target=({tx},{ty}) → {exc}")
