# Robot Dog Project — Global Context

## Project Goal
Build a bionic quadruped robot dog. Full stack: mechanical design → PCB → firmware → simulation → integration.

## How This Project Works
This project runs as a **virtual engineering company**.  
- `system/orchestrate.py` is the driver — it reads state, picks the next unblocked task, and dispatches an agent.
- `system/state.yaml` is the single source of truth for all task statuses.
- `roadmap/roadmap.yaml` defines milestones, tasks, and inter-task dependencies.
- `domains/*/AGENT.md` contains each domain's working instructions.
- `reports/` gets auto-generated progress reports after each task.

## Human-in-the-Loop Gates
Tasks marked `status: blocked_human` require explicit user approval before proceeding.  
These gates sit at cross-domain interfaces: finalized specs that downstream domains depend on.

## Domain Ownership
| Domain | Responsibility |
|---|---|
| mechanical | CAD design (build123d), kinematic specs, BOM |
| electronics | Schematics (KiCad), PCB layout, component selection |
| firmware | Embedded code, communication protocols, motor control |
| simulation | PyBullet/ROS, gait algorithms, FK/IK |
| integration | Cross-domain consistency, final assembly verification |

## Output Conventions
- Every task writes its primary artifact to `domains/<domain>/output/<task-id>/`
- Every task appends a brief completion summary to `reports/log.md`
- Specs that other domains depend on go to `domains/<domain>/specs/`
