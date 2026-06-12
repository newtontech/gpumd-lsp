# 输出命令实体 / Dump Commands Entity

## 概述 / Overview

The `dump_*` commands in GPUMD control what simulation data is written to disk and at what frequency. These are essential for analysis and visualization of MD trajectories.

## 输出命令列表 / Dump Commands

### dump_thermo - Thermodynamics Output
```bash
dump_thermo <interval>
```
- **Output file**: thermo.out
- **Contents**: Temperature, pressure, energy, volume
- **Parameters**:
  - interval: Output every N steps
- **Typical values**: 100-10000

### dump_position - Atomic Positions
```bash
dump_position <interval> <group>
```
- **Output file**: pos.out
- **Contents**: Atomic positions per atom
- **Parameters**:
  - interval: Output frequency
  - group: Atom group ID
- **Format**: Binary or text

### dump_velocity - Atomic Velocities
```bash
dump_velocity <interval> <group>
```
- **Output file**: vel.out
- **Contents**: Atomic velocities per atom
- **Parameters**:
  - interval: Output frequency
  - group: Atom group ID
- **Use**: Kinetic energy analysis, temperature distribution

### dump_force - Atomic Forces
```bash
dump_force <interval> <group>
```
- **Output file**: force.out
- **Contents**: Forces on each atom
- **Parameters**:
  - interval: Output frequency
  - group: Atom group ID
- **Use**: Force analysis, stress calculation

### dump_exyz - Extended XYZ Trajectory
```bash
dump_exyz <interval> <group>
```
- **Output file**: exyz.out
- **Contents**: Extended XYZ format trajectory
- **Parameters**:
  - interval: Output frequency
  - group: Atom group ID
- **Format**: Standard extended XYZ with properties

## 参数验证 / Parameter Validation

### GPUMD-E061: Invalid Argument Count
All dump commands require exactly 2 arguments:
- interval: Integer (positive)
- group: Integer (valid group ID)

```bash
# Correct
dump_thermo 100
dump_position 1000 1
dump_exyz 500 1

# Incorrect (GPUMD-E061)
dump_thermo
dump_position 1000
```

### GPUMD-E062: Invalid Argument Type
Arguments must be integers:

| Command | Arg 1 | Arg 2 |
|---------|-------|-------|
| dump_thermo | int | N/A |
| dump_position | int | int |
| dump_velocity | int | int |
| dump_force | int | int |
| dump_exyz | int | int |

## 原子组 / Atom Groups

Dump commands use group IDs defined by the `group` command:

```bash
# Define groups first
group 1 1        # Group 1 = type 1 atoms
group 2 2        # Group 2 = type 2 atoms

# Then use in dumps
dump_position 1000 1    # Dump group 1
dump_velocity 1000 2    # Dump group 2
```

## 输出策略 / Output Strategy

### 性能考虑 / Performance Considerations
- Large intervals reduce I/O overhead
- Small intervals give better temporal resolution
- Binary formats are more compact
- exyz.out is human-readable but larger

### 典型间隔 / Typical Intervals
| Property | Equilibration | Production | Analysis |
|----------|---------------|------------|----------|
| thermo | 100-1000 | 1000-10000 | 100 |
| position | 1000+ | 1000+ | 100-1000 |
| velocity | 1000+ | 1000+ | 1000+ |
| force | 1000+ | 1000+ | 1000+ |
| exyz | 1000+ | 1000-5000 | 100-1000 |

## 输出文件大小 / Output File Size

File size depends on:
- Number of atoms
- Output interval
- Total simulation steps
- Output format

**Example**: 1000 atoms, 1M steps, interval 1000
- ~1000 frames
- ~10 MB (position) to ~50 MB (exyz)

## 诊断代码 / Diagnostic Codes

- **GPUMD-E061**: Invalid argument count
- **GPUMD-E062**: Invalid argument type
- **GPUMD011**: dump should be declared before run

## 参考资料 / References

- GPUMD output documentation
- Extended XYZ format specification
