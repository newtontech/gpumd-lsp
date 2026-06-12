# 输出文件实体 / Output Files Entity

## 概述 / Overview

GPUMD generates various output files during simulation, containing thermodynamic data, atomic trajectories, and calculated properties. Understanding these files is crucial for analysis.

## 主要输出文件 / Main Output Files

### thermo.out - 热力学输出

#### 触发命令
```bash
dump_thermo <interval>
```

#### 文件格式
```
# timestep temperature kinetic_energy potential_energy total_energy pressure volume
100 300.5 123.4 -456.7 -333.3 1.2 1000.0
200 299.8 122.9 -456.1 -333.2 1.1 1000.1
...
```

#### 列说明
| 列 | 含义 | 单位 |
|----|------|------|
| 1 | 时间步 | - |
| 2 | 温度 | K |
| 3 | 动能 | eV |
| 4 | 势能 | eV |
| 5 | 总能 | eV |
| 6 | 压力 | bar |
| 7 | 体积 | Å³ |

### pos.out - 原子位置

#### 触发命令
```bash
dump_position <interval> <group>
```

#### 文件格式
```
# timestep natoms
<position_data>
```

#### 用途
- 轨迹分析
- 结构演化
- 可视化 (OVITO, VMD)

### vel.out - 原子速度

#### 触发命令
```bash
dump_velocity <interval> <group>
```

#### 文件格式
```
# timestep natoms
<velocity_data>
```

#### 用途
- 速度分布分析
- 温度分布
- 动能计算

### force.out - 原子受力

#### 触发命令
```bash
dump_force <interval> <group>
```

#### 文件格式
```
# timestep natoms
<force_data>
```

#### 用途
- 力分析
- 应力计算
- 原子受力分布

### exyz.out - 扩展XYZ轨迹

#### 触发命令
```bash
dump_exyz <interval> <group>
```

#### 文件格式
```
<natoms>
lattice=... Properties=...
<element> <x> <y> <z> [properties]
...
```

#### 用途
- 可视化 (标准XYZ格式)
- 后处理工具兼容
- 共享数据

## 计算输出文件 / Computation Output Files

### hac.out - 热自相关

#### 触发命令
```bash
compute_hac <sample> <out> <Nc>
```

#### 文件格式
```
# time corr(Jx) corr(Jy) corr(Jz) corr(J)
0.0 1.0 1.0 1.0 1.0
0.1 0.8 0.79 0.81 0.8
...
```

#### 用途
- Green-Kubo热导率计算
- 积分得到κ

### shc.out - 谱热流

#### 触发命令
```bash
compute_shc <sample> <out> <Nc>
```

#### 文件格式
```
# frequency kappa_x kappa_y kappa_z kappa_total
0.0 0.0 0.0 0.0 0.0
0.1 0.5 0.48 0.52 1.0
...
```

#### 用途
- 频率依赖热导率
- 声子贡献分析

### msd.out - 均方位移

#### 触发命令
```bash
compute_msd <sample> <interval>
```

#### 文件格式
```
# time MSD(x) MSD(y) MSD(z) MSD_total
0.0 0.0 0.0 0.0 0.0
1.0 0.01 0.009 0.011 0.03
...
```

#### 用途
- 扩散系数计算
- MSD ∝ 6Dt

### dos.out - 声子态密度

#### 触发命令
```bash
compute_dos <sample> <Nc>
```

#### 文件格式
```
# frequency DOS
0.0 0.0
0.1 0.001
...
```

#### 用途
- 声子谱分析
- 振动性质

## 运行时日志 / Runtime Logs

### run.out / gpumd.out

#### 内容
- 启动信息
- 进度输出
- 错误信息
- 性能统计

#### LSP解析
- 自动检测ERROR/FATAL
- 生成GPUMD-E065诊断
- 帮助错误定位

## 文件大小估算 / File Size Estimation

### 近似计算
```
文件大小 = (帧数) × (原子数) × (每原子字节数)
```

### 典型值
| 文件 | 1000原子/1000帧 | 1000原子/10000帧 |
|------|----------------|------------------|
| thermo.out | ~50 KB | ~500 KB |
| exyz.out | ~10 MB | ~100 MB |
| pos.out | ~8 MB | ~80 MB |

### 优化建议
- 增加interval减少输出
- 生产运行使用较大interval
- 平衡阶段用小interval

## 后处理工具 / Post-processing Tools

### 可视化
- **OVITO**: 支持XYZ格式
- **VMD**: 通用轨迹查看
- **MATLAB/Python**: 自定义分析

### 分析脚本
- Python + NumPy/Matplotlib
- MATLAB数据处理
- GPUMD自带分析工具

## 参考资料 / References

- GPUMD输出格式文档
- OVITO可视化指南
