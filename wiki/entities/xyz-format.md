# XYZ格式实体 / XYZ Format Entity

## 概述 / Overview

GPUMD uses extended XYZ format for atomic structures and training data. This format extends standard XYZ with additional properties per atom or configuration.

## 标准XYZ格式 / Standard XYZ Format

### 基本结构
```
<N_atoms>
<comment_line>
<x> <y> <z> <element> [additional_properties]
```

### 示例
```
2
C-H molecule example
0.000000 0.000000 0.000000 C
0.000000 0.000000 1.090000 H
```

## 扩展XYZ格式 / Extended XYZ Format

### 扩展关键字

#### 能量、力、维里 (NEP训练必需)
```
<NA> lattice=<ax> <ay> <az> <bx> <by> <bz> <cx> <cy> <cz> Properties=species:S:1:pos:R:3:forces:R:3:energy:R:1:virial:R:6
```

#### 分量说明
- **species**: 原子元素类型
- **pos**: 原子位置 (x, y, z)
- **forces**: 原子受力 (fx, fy, fz)
- **energy**: 总能量
- **virial**: 维里应力 (xx, yy, zz, xy, yz, zx)

### NEP训练示例
```
2
lattice=5.0 0.0 0.0 0.0 5.0 0.0 0.0 0.0 5.0 Properties=species:S:1:pos:R:3:forces:R:3:energy:R:1:virial:R:6
C 0.0 0.0 0.0 0.0 0.0 0.1 -10.5 0.0 0.0 0.0 -0.1 0.0 0.0
H 0.0 0.0 1.09 0.0 0.0 -0.1 -10.5 0.0 0.0 0.0 -0.1 0.0 0.0
```

## GPUMD输入XYZ / GPUMD Input XYZ

### 基本要求
```
<NA>
<comment_line>
<element> <x> <y> <z>
```

### 示例
```
64
Bulk silicon structure
Si 0.000 0.000 0.000
Si 0.500 0.500 0.000
...
```

## 数据类型说明 / Data Type Specifications

| 关键字 | 类型 | 维度 | 描述 |
|--------|------|------|------|
| species | S | 1 | 字符串 (元素符号) |
| pos | R | 3 | 浮点数 (位置) |
| forces | R | 3 | 浮点数 (受力) |
| energy | R | 1 | 浮点数 (能量) |
| virial | R | 6 | 浮点数 (维里) |

## 坐标系统 / Coordinate System

- 单位: 埃 (Å)
- 原子坐标: 笛卡尔坐标
- 晶格向量: 真实空间向量

## 训练数据准备 / Training Data Preparation

### DFT转换
常见DFT软件到XYZ转换工具:
- VASP → XYZ: vasp2xyz
- Quantum ESPRESSO → XYZ: qe2xyz

### 数据要求
1. 能量: 系统总能量
2. 受力: 每个原子的受力分量
3. 维里: 应力张量 (6个分量)

### 典型数据集
- **train.xyz**: 100-10000个结构
- **test.xyz**: 10-1000个结构

## 诊断检查 / Diagnostic Checks

### 格式验证
```
1. 行数匹配 (第一行 = 原子数 + 2)
2. 坐标数值 (浮点数)
3. 元素符号 (有效)
4. Properties字符串 (训练必需)
```

### GPUMD-E064: 文件不存在
当train_file或test_file引用的文件不存在时触发

## 编辑器支持 / Editor Support

### LSP功能
- 语法高亮
- 格式验证
- 悬浮信息
- 自动补全

## 参考资料 / References

- Extended XYZ规范: ASE documentation
- NEP训练数据格式: GPUMD手册
- XYZ转换工具: ase.io
