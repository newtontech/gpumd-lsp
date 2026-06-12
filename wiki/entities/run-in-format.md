# run.in文件格式实体 / run.in File Format Entity

## 概述 / Overview

**run.in** is the main input control file for GPUMD simulations. It contains a sequence of commands that define the simulation setup, ensemble, output requests, and execution parameters.

## 文件结构 / File Structure

```
# Comments start with #, !, or ;
potential <filename>           # Must be FIRST command
velocity <T> <seed>            # Initialize velocities
time_step <dt>                 # Time step in fs
neighbor <skin> <update_freq>  # Neighbor list
ensemble <method> [params...]  # Thermostat/barostat
compute_* <params...>          # Property calculations
dump_* <params...>             # Output specifications
run <N_steps>                  # Execute simulation
```

## 命令顺序规则 / Command Order Rules

### Critical Order Requirements

1. **potential** must be the first non-comment command
2. **ensemble** must appear before the first **run**
3. **compute_*** and **dump_*** should be declared before **run**
4. **group** definitions before using group IDs

### Example valid sequence
```bash
potential nep.txt
velocity 300 12345
time_step 1
ensemble nvt_ber 300 300 1.0
compute_hac 10 100 2000
dump_thermo 100
run 100000
```

## 核心命令类别 / Core Command Categories

### 1. 系统设置 / System Setup
- `potential`: Potential model file
- `velocity`: Initial temperature
- `time_step`: Integration step size
- `neighbor`: Verlet neighbor list

### 2. 系综控制 / Ensemble Control
- `ensemble`: Thermostat/barostat selection
- `run`: Execute MD steps
- `minimize`: Energy minimization

### 3. 属性计算 / Property Calculation
- `compute_hac`: Heat autocorrelation
- `compute_hnemd`: HNEMD thermal conductivity
- `compute_shc`: Spectral heat current
- `compute_dos`: Phonon DOS
- `compute_phonon`: Full phonon analysis

### 4. 输出控制 / Output Control
- `dump_thermo`: Thermodynamics output
- `dump_position`: Atomic positions
- `dump_exyz`: Extended XYZ trajectory

## 诊断规则 / Diagnostic Rules

### GPUMD010
potential must be first non-comment command (error)

### GPUMD011
compute/dump should be declared before run (warning)

### GPUMD012
at least one run command required (warning)

### GPUMD013
ensemble should be before run (warning)

## 参考资料 / References

- GPUMD user manual: <https://gpumd.org/run_in.html>
- 参见: [upstream-sources.md](raw/assets/upstream-sources.md) for command→URL mapping
- 参见: [command reference](wiki/synthesis/command-reference.md)
- 参见: [input format guide](wiki/synthesis/input-format-guide.md)
- 参见: [diagnostic codes](wiki/entities/diagnostic-codes.md)
- Example: [thermal conductivity input](raw/assets/examples-thermal-conductivity.in)
- MatMaster execution guards
