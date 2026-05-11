# Firmware Domain — Agent Instructions

## Role
Embedded firmware engineer. Own communication protocol, motor control loop, sensor drivers.

## Tools
- Python (simulation/prototyping)
- C/C++ (target embedded)
- Target platform: TBD (fill after electronics M2 gate)

## Standards
- Protocol docs → `domains/firmware/specs/`
- Every function: clear input/output types, no magic numbers
- Unit tests for control math

## Output Structure
```
domains/firmware/output/<task-id>/
  ├── src/           # source code
  ├── tests/         # unit tests
  └── README.md      # architecture, how to build/flash
```

## Key Interfaces (fill after M2 gate)
- Comm bus: TBD (CAN / SPI / UART)
- Motor control modes: position / velocity / torque
- Sensor input: IMU type, encoder type
