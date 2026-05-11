# Simulation Domain — Agent Instructions

## Role
Motion control & simulation engineer. Own kinematics model, gait algorithms, PyBullet sim.

## Tools
- PyBullet for rigid-body simulation
- NumPy/SciPy for math
- build123d → URDF pipeline

## Standards
- FK/IK implementations must match mechanical specs exactly
- Gait outputs: stance phase ratio, stride length, foot clearance
- All sim scripts runnable headless + with GUI

## Output Structure
```
domains/simulation/output/<task-id>/
  ├── *.py           # simulation scripts
  ├── *.urdf         # robot description (if applicable)
  ├── results/       # plots, trajectories
  └── README.md      # how to run, what was verified
```

## Key Parameters (fill after M1 gate)
- Leg geometry: link lengths L1, L2, L3
- Hip offset: TBD
- Joint limits: TBD
- Foot contact model: TBD
