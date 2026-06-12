# 热输运概念 / Thermal Transport Concepts

## 概述 / Overview

Thermal transport in materials describes how heat energy flows through a system. GPUMD specializes in calculating thermal conductivity using various MD-based methods.

## 热导率计算方法 / Thermal Conductivity Methods

### Green-Kubo (GK) Method
Uses equilibrium MD simulations and the fluctuation-dissipation theorem:

**Formula**:
```
κ = (V/kT²) ∫₀^∞ <J(t)·J(0)> dt
```

**GPUMD Implementation**:
```bash
ensemble nvt_ber 300 300 1.0
compute_hac 10 100 2000
run 1000000
```

**Output**: hac.out contains heat autocorrelation data

### HNEMD (Homogeneous Non-Equilibrium MD)
Applies a small driving force to create a heat current:

**Formula**:
```
κ = J / (Fe·T)
```

**GPUMD Implementation**:
```bash
ensemble nve
compute_hnemd 0.001
run 1000000
```

**Parameters**:
- Fe: Driving force (typically 0.001-0.01)
- Linear response regime required

### Spectral Heat Current (SHC)
Frequency-resolved thermal conductivity:

**GPUMD Implementation**:
```bash
compute_shc 10 100 2000
run 1000000
```

**Output**: Frequency-dependent κ(ω)

## 声子贡献 / Phonon Contributions

### Normal Mode Decomposition
Phonons as heat carriers in crystals:
- Acoustic phonons: Long-wavelength, high group velocity
- Optical phonons: Short-wavelength, lower contribution

### Modal Analysis
```bash
compute_phonon    # Full phonon spectrum
compute_gkma      # Modal thermal conductivity
```

## 尺寸效应 / Size Effects

### Phonon Mean Free Path (MFP)
- Long-MFP phonons require large simulation cells
- Size-dependent thermal conductivity until convergence

### Convergence Criteria
```bash
# Test different sizes
replicate 2 2 2    # 2×2×2 supercell
replicate 4 4 4    # 4×4×4 supercell
replicate 8 8 8    # 8×8×8 supercell
```

## 应用场景 / Applications

### Bulk Materials
- Isotropic thermal conductivity
- Use equilibrium Green-Kubo

### Thin Films / Nanowires
- Size-dependent κ
- Boundary scattering effects
- Use NEMD with heat_bc

### Heterostructures
- Interface thermal resistance
- Kapitza resistance
- Temperature discontinuity

## 典型工作流 / Typical Workflow

1. **Equilibration**
```bash
ensemble nvt_ber 300 300 1.0
run 100000
```

2. **Production**
```bash
compute_hac 10 100 2000
ensemble nve
run 1000000
```

3. **Analysis**
- Process hac.out
- Extract thermal conductivity
- Check convergence

## 单位 / Units

| Quantity | Unit | GPUMD |
|----------|------|-------|
| Thermal conductivity | W/m·K | output |
| Temperature | K | input |
| Time | fs | input |
| Length | Å | input |
| Energy | eV | internal |

## 参考资料 / References

- GK Method: Green-Kubo relations
- HNEMD: Fan et al., Phys. Rev. B
- SHC: Spectral decomposition methods
