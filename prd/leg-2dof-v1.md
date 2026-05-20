# 四足机器狗 — 左前腿 2-DOF v1

**版本**: v1.0 · 2026-05-19
**所有人**: product_manager(小米)
**状态**: ✅ 实施完成,待 v2 整机扩展

## 用户故事

> 「先实现一条腿,跑通 PRD → CAD → 电子 → 固件 → 算法 → 成本 → 装配指南 →
>   contract lint → 4 视图展示页 全链路。」

## 功能要求

- **2-DOF 单腿**:髋关节(hip) + 膝关节(knee)
- 髋关节摆角 60°-120°(中位 90°,即站立正前;±30° 幅度)
- 膝关节摆角 0°-90°(0° 伸直,90° 直角)
- 单腿质量 < 100g(本版 88g:femur 42g + tibia 28g + hip-bracket 18g)
- 控制器: ESP32-S3-DevKitC-1
- 执行器: 2× MG996R 舵机
- 反馈: MPU6050 IMU(I2C 0x68)

## 选型约束(对应 BOM)

- 主控:[esp32_main](../domains/electronics/bom.json) — ESP32-S3,3 路 PWM + I2C
- 舵机:[mg996r_hip / mg996r_knee](../domains/electronics/bom.json) — MG996R(13kg·cm 扭矩)
- 电源:[battery_lipo](../domains/electronics/bom.json) 3S 18650 + DCDC 12→5V
- 结构:PETG 3D 打印(femur / tibia / hip-bracket)

## 验收清单

- [x] CAD: 3 部件 STEP + GLB 双导出([domains/mechanical/parts/](../domains/mechanical/parts/))
- [x] BOM: 12 类强枚举,每行 ≥2 vendors([domains/electronics/bom.json](../domains/electronics/bom.json))
- [x] 原理图: KiCad 源 + SVG 渲染([domains/electronics/cad/exports/](../domains/electronics/cad/exports/))
- [x] 固件: PWM 驱动 + IMU 读取([domains/firmware/src/leg_pwm.c](../domains/firmware/src/leg_pwm.c))
- [x] 算法: IK + FK 自检通过([domains/firmware/algo/](../domains/firmware/algo/))
- [x] 接线: wiring.json 9 connections([domains/firmware/wiring.json](../domains/firmware/wiring.json))
- [x] 成本: ¥183 单腿 budget 价([domains/integration/cost_summary.json](../domains/integration/cost_summary.json))
- [x] 装配指南: 5 phase 18 step([../assembly.json](../assembly.json))
- [x] connectivity 互连图: 自动 merge([../connectivity.json](../connectivity.json))
- [x] contract lint 通过

## 下一步(v2)

- 扩展到 4 腿 8-DOF(8 个 MG996R)
- 步态:trot / walk / pronk
- 仿真:URDF + MuJoCo 步态视频
