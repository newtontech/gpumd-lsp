# 输入格式指南 / Input Format Guide

## 文件类型概览 / File Type Overview

GPUMD uses two primary input file types:

| 文件 | 用途 | 必需 | 扩展 |
|------|------|------|------|
| run.in | 模拟控制 | 是 | .in |
| nep.in | NEP训练 | 否* | .in |

*仅当训练/使用NEP势函数时需要

## run.in 格式 / run.in Format

### 基本结构
```
# 注释行 (以 #, !, 或 ; 开头)
potential <model_file>      # 必须是第一条命令
<系统设置命令>
<系综控制命令>
<计算命令>
<输出命令>
run <步数>
```

### 最小示例
```bash
# 最小run.in示例
potential nep.txt
ensemble nve
run 1000
```

### 完整示例
```bash
# 热导率计算示例
potential nep.txt
velocity 300 12345
time_step 1
neighbor 0.5 10

# 定义原子组
group 1 1
group 2 2

# 系综设置
ensemble nve

# 计算设置
compute_hac 10 100 2000
dump_thermo 100
dump_exyz 1000 1

# 运行模拟
run 1000000
```

## nep.in 格式 / nep.in Format

### 基本结构
```
# 原子类型定义
type <N> <type1> [type2...]

# 模型参数
cutoff <rc_radial> <rc_angular>
n_max <n_radial> <n_angular>
l_max <l_radial> <l_angular>
version <nep_version>

# 训练参数
lambda_e <value>
lambda_f <value>
lambda_v <value>
batch_size <N>
population_size <N>
generation <N>

# 数据文件
train_file <path>
test_file <path>
```

### 训练示例
```bash
# C-H系统NEP训练
type 2 C H
cutoff 5 4
n_max 6 6
l_max 4 4
version 4
basis_size 12

lambda_e 0.1
lambda_f 0.1
lambda_v 0.1
batch_size 100
population_size 50
generation 100000

train_file train.xyz
test_file test.xyz
```

### 推理示例
```bash
# 仅用于模型评估
type 2 C H
cutoff 5 4
n_max 6 6
l_max 4 4
version 4
basis_size 12
```

## 语法规则 / Syntax Rules

### 注释 / Comments
```
# 这是注释
! 这也是注释
; 这还是注释
```

### 参数分隔 / Parameter Separation
- 空格分隔参数
- 制表符也可用
- 不支持逗号分隔

### 大小写敏感性 / Case Sensitivity
- 命令: 不区分大小写 (POTENTIAL = potential)
- 原子类型: 区分大小写 (C ≠ c)
- 文件路径: 遵循操作系统规则

### 行 continuation
- 当前版本不支持多行命令
- 每条命令必须在一行内

## 诊断检查 / Diagnostic Checks

### run.in 检查
1. GPUMD010: potential必须是第一条命令
2. GPUMD012: 必须有run命令
3. GPUMD013: ensemble应在run之前
4. GPUMD011: compute/dump应在run之前
5. GPUMD-E063: potential文件必须存在

### nep.in 检查
1. GPUMD-E060: 未知关键字
2. GPUMD-E061: 参数数量错误
3. GPUMD-E062: 参数类型错误
4. GPUMD-E064: train_file/test_file必须存在

## 格式化规则 / Formatting Rules

### 对齐 (gpumd-fmt)
```bash
# 未格式化
potential nep.txt
velocity 300 12345

# 格式化后
potential                  nep.txt
velocity                   300 12345
```

### 关键字对齐
- 关键字左对齐
- 参数24列对齐
- 等号格式化: key = value

## 文件编码 / File Encoding
- 必须: UTF-8
- 不支持: UTF-16, Latin-1等

## 参考资料 / References

- GPUMD用户手册
- NEP训练指南
- LSP格式化工具
