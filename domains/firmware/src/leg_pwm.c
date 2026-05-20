/*
 * leg_pwm.c — ESP32-S3 + MG996R PWM 驱动(robot-dog v1 单腿 2-DOF)
 *
 * 接线(见 domains/firmware/wiring.json):
 *   GPIO13 → MG996R Hip 信号(PWM 50Hz)
 *   GPIO14 → MG996R Knee 信号(PWM 50Hz)
 *   GPIO21 → MPU6050 SDA (I2C)
 *   GPIO22 → MPU6050 SCL (I2C)
 *
 * 算法: 接收 algo/ik_2dof.py 算出的 (hip_deg, knee_deg) 写入舵机
 */
#include <Arduino.h>
#include <ESP32Servo.h>
#include <Wire.h>

#define HIP_PIN  13
#define KNEE_PIN 14
#define I2C_SDA  21
#define I2C_SCL  22

#define HIP_MIN_DEG  60   // 安全角度下限(髋:+30°→站立正前)
#define HIP_MAX_DEG  120
#define KNEE_MIN_DEG 0
#define KNEE_MAX_DEG 90

Servo hipServo, kneeServo;

static int clamp_deg(int v, int lo, int hi) {
    return v < lo ? lo : (v > hi ? hi : v);
}

void setup() {
    Serial.begin(115200);
    Wire.begin(I2C_SDA, I2C_SCL);

    hipServo.setPeriodHertz(50);
    kneeServo.setPeriodHertz(50);
    hipServo.attach(HIP_PIN, 500, 2400);
    kneeServo.attach(KNEE_PIN, 500, 2400);

    hipServo.write(90);   // 中位
    kneeServo.write(45);
    Serial.println("PWM ready, IMU on I2C 0x68");
}

/* 由 algorithm/ik_2dof.py 推送目标角度时调用 */
void set_leg_angles(int hip_deg, int knee_deg) {
    int h = clamp_deg(hip_deg, HIP_MIN_DEG, HIP_MAX_DEG);
    int k = clamp_deg(knee_deg, KNEE_MIN_DEG, KNEE_MAX_DEG);
    hipServo.write(h);
    kneeServo.write(k);
    Serial.printf("hip=%d knee=%d\n", h, k);
}

void loop() {
    /* 接 BLE/串口 / 主控板下发目标 */
    delay(20);
}
