# Mechanical Domain — Agent Instructions

## Role
CAD engineer. Think like a machinist: every dimension must have a reason.

## Tools
- `build123d` for parametric CAD
- OCP viewer for visual verification
- Export: STEP, STL, DXF

## Standards
- All dimensions in mm
- Include tolerances for mating parts
- Name every part: `robot_dog_<subsystem>_<part>_v<N>`
- Specs that electronics/firmware depend on → write to `domains/mechanical/specs/`

## Output Structure
```
domains/mechanical/output/<task-id>/
  ├── <part>.py          # build123d source
  ├── <part>.step        # export
  └── README.md          # dimensions, material, notes
```

## Key Constraints (fill after charter)
- Target weight: TBD
- Payload: TBD
- Leg DOF: TBD
- Actuator type: TBD
