# 命令参考 / Command Reference

## run.in 命令 / run.in Commands

### 系统设置 / System Setup

| 命令 | 语法 | 参数 | 描述 |
|------|------|------|------|
| potential | `potential <filename>` | filepath (1-2) | NEP模型文件 (必须是第一条命令) |
| velocity | `velocity <T> <seed>` | float, int (1-2) | 初始温度和随机种子 |
| time_step | `time_step <dt>` | float (1) | 时间步长 (fs) |
| neighbor | `neighbor <skin> <freq>` | float, int (2) | Verlet邻居表参数 |

### 系综控制 / Ensemble Control

| 命令 | 语法 | 参数 | 描述 |
|------|------|------|------|
| ensemble | `ensemble <method> [params...]` | thermostat (1-) | 热浴/压浴控制 |
| run | `run <N_steps>` | int (1) | 执行MD步数 |
| minimize | `minimize <method> <tol> <steps>` | path, float, int (3) | 能量最小化 |

### 属性计算 / Property Calculation

| 命令 | 语法 | 参数 | 描述 |
|------|------|------|------|
| compute_hac | `compute_hac <sample> <out> <Nc>` | int, int, int (3) | 热自相关 (Green-Kubo) |
| compute_hnemd | `compute_hnemd <Fe>` | float (1) | HNEMD热导率 |
| compute_shc | `compute_shc <sample> <out> <Nc> [si]` | int, int, int, int (3-4) | 谱热流 |
| compute_msd | `compute_msd <sample> <interval>` | int, int (2) | 均方位移 |
| compute_dos | `compute_dos <sample> <Nc>` | int, int (2) | 声子态密度 |
| compute_phonon | `compute_phonon` | (0) | 完整声子性质 |
| compute_sdc | `compute_sdc <sample> <interval>` | int, int (2) | 自扩散系数 |
| compute_gkma | `compute_gkma <sample> <int> <Nc>` | int, int, int (3) | Green-Kubo模态分析 |
| compute_heat | `compute_heat <sample> <interval>` | int, int (2) | 热流计算 |

### 输出控制 / Output Control

| 命令 | 语法 | 参数 | 描述 |
|------|------|------|------|
| dump_thermo | `dump_thermo <interval>` | int (1) | 热力学输出 |
| dump_position | `dump_position <interval> <group>` | int, int (2) | 原子位置 |
| dump_velocity | `dump_velocity <interval> <group>` | int, int (2) | 原子速度 |
| dump_force | `dump_force <interval> <group>` | int, int (2) | 原子受力 |
| dump_exyz | `dump_exyz <interval> <group>` | int, int (2) | 扩展XYZ轨迹 |

### 结构操作 / Structure Manipulation

| 命令 | 语法 | 参数 | 描述 |
|------|------|------|------|
| fix | `fix <group>` | int (1) | 固定原子组 |
| deform | `deform <dir> <rate> <steps>` | int, float, int (3) | 形变模拟 |
| change_box | `change_box [params...]` | (0-) | 修改盒子尺寸 |
| replicate | `replicate <nx> <ny> <nz>` | int, int, int (3) | 复制晶胞 |
| group | `group <id> <type...>` | int, int (2-) | 定义原子组 |
| space | `space <group>` | int (1) | 设置空间群 |

### 外部工具 / External Tools

| 命令 | 语法 | 参数 | 描述 |
|------|------|------|------|
| plumed | `plumed <file>` | path (1) | PLUMED增强采样 |
| dftd3 | `dftd3 [params...]` | (0-) | DFT-D3色散校正 |

## nep.in 命令 / nep.in Commands

### 基本设置 / Basic Setup

| 命令 | 语法 | 参数 | 描述 |
|------|------|------|------|
| type | `type <N> <type1> [type2...]` | int, path (2-) | 原子类型定义 |
| version | `version <n>` | int (1) | NEP版本 |

### 模型参数 / Model Parameters

| 命令 | 语法 | 参数 | 描述 |
|------|------|------|------|
| cutoff | `cutoff <rc_radial> <rc_angular>` | float, float (2) | 截断半径 |
| n_max | `n_max <n_radial> <n_angular>` | int, int (2) | 基函数数量 |
| l_max | `l_max <l_radial> <l_angular>` | int, int (2) | 角动量量子数 |
| basis_size | `basis_size <size>` | int (1) | 神经网络基大小 |

### 训练参数 / Training Parameters

| 命令 | 语法 | 参数 | 描述 |
|------|------|------|------|
| lambda_e | `lambda_e <value>` | float (1) | 能量正则化 |
| lambda_f | `lambda_f <value>` | float (1) | 力正则化 |
| lambda_v | `lambda_v <value>` | float (1) | 维里正则化 |
| batch_size | `batch_size <N>` | int (1) | 批大小 |
| population_size | `population_size <N>` | int (1) | 种群大小 |
| generation | `generation <N>` | int (1) | 训练代数 |

### 数据文件 / Data Files

| 命令 | 语法 | 参数 | 描述 |
|------|------|------|------|
| train_file | `train_file <path>` | path (1) | 训练数据文件 |
| test_file | `test_file <path>` | path (1) | 测试数据文件 |

### 高级选项 / Advanced Options

| 命令 | 语法 | 参数 | 描述 |
|------|------|------|------|
| zbl | `zbl <r_inner> <r_outer>` | float, float (2) | ZBL短程排斥 |
| weight | `weight <E> <F> <V>` | float, float, float (3) | 损失权重 |
| prediction_csv | `prediction_csv` | (0) | CSV输出 |

## 诊断代码 / Diagnostic Codes

| 代码 | 严重程度 | 描述 |
|------|----------|------|
| GPUMD-E060 | error | 未知命令 |
| GPUMD-E061 | error | 参数数量错误 |
| GPUMD-E062 | error | 参数类型错误 |
| GPUMD-E063 | error | 模型文件缺失 |
| GPUMD-E064 | error | 训练文件缺失 |
| GPUMD-E065 | error | 运行时错误 |
| GPUMD-W060 | warning | 恒温器无效 |
| GPUMD010 | error | potential非首行 |
| GPUMD011 | warning | compute/dump应在run前 |
| GPUMD012 | warning | 缺少run命令 |
| GPUMD013 | warning | ensemble应在run前 |

## 参考资料 / References

- GPUMD用户手册
- NEP势函数文档
- MatMaster工作流
