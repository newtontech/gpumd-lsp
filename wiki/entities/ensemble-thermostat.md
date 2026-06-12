# 系综与恒温器实体 / Ensemble and Thermostat Entity

## 概述 / Overview

GPUMD supports multiple thermodynamic ensembles through various thermostat and barostat implementations. The choice of ensemble determines which thermodynamic variables are conserved during simulation.

## 支持的系综 / Supported Ensembles

### 微正则系综 / Microcanonical (NVE)
```bash
ensemble nve
```
- Conserves: Energy (E), Volume (V), Number (N)
- No temperature control
- Used for energy conservation tests

### 正则系综 / Canonical (NVT) Thermostats

#### Berendsen Thermostat
```bash
ensemble nvt_ber <T> <T_last> <tau_T>
```
- Weak coupling thermostat
- tau_T: Time constant (fs)
- Good for equilibration

#### Nosé-Hoover Thermostat
```bash
ensemble nvt_nose_hoover <T> <T_last> <tau_T>
```
- Canonical ensemble thermostat
- Better for production runs
- Produces correct fluctuations

### 等温等压系综 / Isothermal-Isobaric (NPT) Barostats

#### Berendsen Barostat
```bash
ensemble npt_ber <T> <T_last> <tau_T> <pxx> <pyy> <pzz> <tau_p>
```
- Anisotropic pressure control
- Separate pressures for each direction

#### MTK Barostat
```bash
ensemble npt_mtk <T> <T_last> <tau_T> <pxx> <pyy> <pzz> <tau_p>
```
- Martyna-Klein-Tuckerman barostat
- Correct ensemble for NPT

### 热边界条件 / Heat Boundary Condition
```bash
ensemble heat_bc <T1> <T2> <width>
```
- Fixed temperature boundaries
- Used for thermal conductivity calculations
- T1, T2: Boundary temperatures
- width: Boundary region width

## 参数说明 / Parameter Description

| 参数 | 含义 | 典型值 |
|------|------|--------|
| T | Target temperature (K) | 300 |
| T_last | Last temperature (K) | Same as T |
| tau_T | Temperature coupling (fs) | 100-1000 |
| pxx/pyy/pzz | Pressure (bar) | 1 |
| tau_p | Pressure coupling (fs) | 1000 |

## 验证规则 / Validation Rules

### GPUMD-W060
Invalid thermostat in ensemble command

Known thermostats:
- nve
- nvt_ber / nvt_berendsen
- nvt_nose_hoover
- npt_ber / npt_berendsen
- npt_mtk
- heat_bc

### GPUMD-E061
Invalid argument count for thermostat

Each thermostat requires specific number of parameters:
- nve: 0 parameters
- nvt_*: 3 parameters
- npt_*: 7 parameters
- heat_bc: 3 parameters

## 典型应用 / Typical Applications

- **NVE**: Energy conservation validation
- **NVT**: Structure equilibration
- **NPT**: Cell optimization
- **heat_bc**: Thermal conductivity calculation

## 参考资料 / References

- GPUMD documentation: Ensemble methods
- Thermostat algorithms: Berendsen, Nosé-Hoover, MTK
