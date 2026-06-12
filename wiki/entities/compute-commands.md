# 计算命令实体 / Compute Commands Entity

## 概述 / Overview

GPUMD provides various `compute_*` commands for calculating material properties during molecular dynamics simulations. These are particularly focused on thermal transport and phonon-related properties.

## 热输运计算 / Thermal Transport Calculations

### compute_hac - Heat Autocorrelation
```bash
compute_hac <sample> <output_interval> <Nc>
```
- **Purpose**: Green-Kubo thermal conductivity
- **sample**: Sampling frequency
- **output_interval**: Output period
- **Nc**: Correlation length

### compute_hnemd - HNEMD Method
```bash
compute_hnemd <Fe>
```
- **Purpose**: Homogeneous nonequilibrium MD
- **Fe**: Driving force parameter
- **Output**: Thermal conductivity tensor

### compute_shc - Spectral Heat Current
```bash
compute_shc <sample> <output_interval> <Nc> [sample_interval]
```
- **Purpose**: Frequency-dependent thermal conductivity
- **Nc**: Number of correlation steps
- **Optional**: sample_interval parameter

## 扩散性质 / Diffusion Properties

### compute_msd - Mean Square Displacement
```bash
compute_msd <sample> <interval>
```
- **Purpose**: Diffusion coefficient calculation
- **Output**: MSD vs time data

### compute_sdc - Self Diffusion Coefficient
```bash
compute_sdc <sample> <interval>
```
- **Purpose**: Velocity autocorrelation analysis
- **Output**: Diffusion coefficients per atom type

## 声子分析 / Phonon Analysis

### compute_dos - Density of States
```bash
compute_dos <sample> <Nc>
```
- **Purpose**: Phonon density of states
- **Method**: Velocity autocorrelation
- **Nc**: Correlation steps

### compute_phonon - Full Phonon Properties
```bash
compute_phonon
```
- **Purpose**: Complete phonon dispersion
- **Output**: Frequencies, eigenvectors, group velocities

### compute_gkma - Green-Kubo Modal Analysis
```bash
compute_gkma <sample> <interval> <Nc>
```
- **Purpose**: Modal thermal conductivity
- **Method**: Modal decomposition of heat current

## 其他计算 / Other Calculations

### compute_heat - Heat Current
```bash
compute_heat <sample> <interval>
```
- **Purpose**: Per-atom heat current
- **Output**: Heat flux data

## 参数验证 / Parameter Validation

### GPUMD-E061: Invalid Argument Count
Each compute command requires specific argument counts:

| Command | Min Args | Max Args |
|---------|----------|----------|
| compute_hac | 3 | 3 |
| compute_hnemd | 1 | 1 |
| compute_shc | 3 | 4 |
| compute_msd | 2 | 2 |
| compute_dos | 2 | 2 |
| compute_phonon | 0 | 0 |
| compute_sdc | 2 | 2 |
| compute_gkma | 3 | 3 |
| compute_heat | 2 | 2 |

### GPUMD-E062: Invalid Argument Type
Arguments must match expected types:
- Integer: sample, interval, Nc, generation
- Float: Fe, tau_T, cutoff

## 使用建议 / Usage Recommendations

1. **Pre-run placement**: Declare compute commands before first `run`
2. **Appropriate intervals**: Balance output frequency vs performance
3. **Correlation length**: Choose Nc based on system relaxation time
4. **Multiple computes**: Can use multiple compute commands simultaneously

## 输出文件 / Output Files

- **hac.out**: Heat autocorrelation data
- **shc.out**: Spectral heat current
- **msd.out**: Mean square displacement
- **dos.out**: Density of states
- **phonon.out**: Full phonon properties

## 参考资料 / References

- GPUMD compute commands documentation
- Green-Kubo formalism for thermal conductivity
- HNEMD method: heat current driving force approach
