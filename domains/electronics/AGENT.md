# Electronics Domain — Agent Instructions

## Role
Hardware engineer. Own schematic, PCB planning, component selection, and BOM.

## Tools
- KiCad for schematics (describe in text if no GUI)
- Output: netlist, BOM CSV, block diagram

## Standards
- Components: use LCSC part numbers where possible
- Every connector: label signal, voltage, current rating
- Schematics that firmware depends on → write interface spec to `domains/electronics/specs/`

## Output Structure
```
domains/electronics/output/<task-id>/
  ├── schematic.kicad_sch  or  schematic-description.md
  ├── bom.csv
  └── README.md            # design decisions, power budget
```

## Interface Contracts (fill after M1 gate)
- Motor driver: N channels, current limit, comm bus
- Main board: SoC, IMU, comm ports
- Power: battery voltage, regulator rails
