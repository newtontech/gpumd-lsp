# GPUMD 实体 / GPUMD Software Entity

## 概述 / Overview

**GPUMD** (GPU-accelerated Molecular Dynamics) is a high-performance molecular dynamics simulation software specifically designed for GPU acceleration. It specializes in materials science applications, particularly for thermal transport and phonon-related calculations.

## 核心特性 / Core Features

- **GPU加速**: Optimized for NVIDIA GPUs using CUDA
- **NEP势函数**: Neural Evolution Potential (NEP) machine learning potentials
- **热输运计算**: Specialized in thermal conductivity calculations
- **声子分析**: Comprehensive phonon property analysis tools
- **高性能**: Can handle large systems (100k+ atoms) efficiently

## 输入文件格式 / Input File Formats

GPUMD uses two primary input files:

1. **run.in**: Main simulation control file
2. **nep.in**: NEP potential training/evaluation configuration

## 典型工作流 / Typical Workflow

```
1. Prepare structure (XYZ format)
2. Train NEP potential (nep.in + train.xyz)
3. Configure simulation (run.in)
4. Run simulation
5. Analyze output (dump files, thermo.out)
```

## 相关命令 / Related Commands

- `potential`: Specify NEP model file
- `ensemble`: Set thermodynamic ensemble
- `run`: Execute MD steps
- `compute_*`: Various property calculations

## 参考资料 / References

- Official docs: <https://gpumd.org/>
- GitHub: <https://github.com/brucefan1983/GPUMD>
- NEP potential: <https://gpumd.org/nep.html>
- 参见: [upstream-sources.md](raw/assets/upstream-sources.md) for complete command→URL mapping
- 参见: [run.in format](wiki/entities/run-in-format.md) for input syntax
- 参见: [NEP potential](wiki/entities/nep-potential.md) for NEP training
- 参见: [diagnostic codes](wiki/entities/diagnostic-codes.md) for LSP error codes

## LSP支持 / LSP Support

The `gpumd-lsp` provides:
- Syntax validation for run.in and nep.in
- Command completion
- Hover documentation
- Diagnostic error checking
- Runtime log parsing
