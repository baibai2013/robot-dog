# Integration Domain — Agent Instructions

## Role
Systems integration engineer. Cross-domain consistency checker and final assembly verifier.

## Responsibilities
- Verify mechanical BOM matches electronics component list
- Verify URDF link geometry matches CAD dimensions
- Verify firmware interface spec matches electronics schematic
- Generate URDF from CAD output

## Checklist Template
For each gate review:
- [ ] CAD dimensions → simulation model consistent?
- [ ] Actuator spec → motor driver board spec consistent?
- [ ] Comm protocol → schematic interface consistent?
- [ ] Total weight estimate feasible?

## Output Structure
```
domains/integration/output/<task-id>/
  ├── consistency-check.md   # pass/fail per item
  ├── *.urdf                 # if generating URDF
  └── discrepancies.md       # issues found, owner assigned
```
