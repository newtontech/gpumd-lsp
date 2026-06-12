# NEP势函数实体 / NEP Potential Entity

## 概述 / Overview

**NEP** (Neural Evolution Potential) is a machine learning potential method integrated with GPUMD. It uses neural network representations trained on DFT data to achieve near-DFT accuracy at MD simulation speeds.

## 核心概念 / Core Concepts

### 训练数据格式 / Training Data Format

- **train.xyz**: Extended XYZ format with energies, forces, virials
- **test.xyz**: Validation dataset for model evaluation
- Required columns: energy, forces, virial stress

### 模型参数 / Model Parameters

- **version**: NEP version (3, 4)
- **cutoff**: Radial and angular cutoff distances
- **n_max**: Number of basis functions
- **l_max**: Angular momentum quantum numbers
- **basis_size**: Neural network basis size

### 训练参数 / Training Parameters

- **lambda_e**: Energy regularization
- **lambda_f**: Force regularization
- **lambda_v**: Virial regularization
- **batch_size**: Training batch size
- **population_size**: Evolutionary population size
- **generation**: Training generations

## nep.in语法 / nep.in Syntax

```bash
# Basic NEP training configuration
type <N> <type1> [type2...]
cutoff <rc_radial> <rc_angular>
n_max <n_radial> <n_angular>
l_max <l_radial> <l_angular>
version <nep_version>
train_file train.xyz
test_file test.xyz
generation <N>
```

## 损失函数 / Loss Function

The total loss combines:
- Energy loss (weighted by lambda_e)
- Force loss (weighted by lambda_f)
- Virial loss (weighted by lambda_v)

## 应用场景 / Applications

- Bulk materials thermal conductivity
- Heterostructure thermal transport
- Phonon dispersion calculations
- High-throughput materials screening

## 诊断代码 / Diagnostic Codes

- **GPUMD-E064**: Missing train_file/test_file
- **GPUMD-E060**: Unknown NEP keyword
- **GPUMD-E061**: Invalid argument count

## 参考资料 / References

- NEP paper: Fan et al., Phys. Rev. B
- GPUMD documentation: NEP training section
