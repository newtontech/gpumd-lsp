# 声子分析实体 / Phonon Analysis Entity

## 概述 / Overview

GPUMD provides comprehensive phonon analysis capabilities for understanding vibrational properties of materials and their contribution to thermal transport.

## 声子计算命令 / Phonon Calculation Commands

### compute_dos - 声子态密度
```bash
compute_dos <sample> <Nc>
```
- **方法**: 速度自相关函数
- **输出**: dos.out (频率 vs DOS)
- **单位**: THz
- **参数**:
  - sample: 采样频率
  - Nc: 相关步数

### compute_phonon - 完整声子性质
```bash
compute_phonon
```
- **输出**:
  - phonon.out: 声子频率
  - mode_vel.out: 群速度
  - mode_heat.out: 模态热容
  - lifetime.out: 声子寿命

### compute_gkma - Green-Kubo模态分析
```bash
compute_gkma <sample> <interval> <Nc>
```
- **目的**: 模态热导率分解
- **输出**: gkma.out
- **信息**: 每个模态的热导率贡献

## 声子性质 / Phonon Properties

### 声子模式分类

#### 声学声子
- 低频 (< 2 THz)
- 高群速度
- 热输运主要贡献者
- 3个声学分支 (1个纵波, 2个横波)

#### 光学声子
- 高频 (> 5 THz)
- 低群速度
- 对热导率贡献较小
- 3N-3个光学分支 (N = 原子数)

### 声子散射机制
1. **声子-声子散射**
   - Umklapp过程
   - Normal过程

2. **边界散射**
   - 有限尺寸效应
   - 粗糙度散射

3. **缺陷散射**
   - 点缺陷
   - 同位素散射

## 典型工作流 / Typical Workflow

### 1. 平衡模拟
```bash
potential nep.txt
velocity 300 12345
time_step 1
ensemble nvt_ber 300 300 1.0
run 200000
```

### 2. 声子分析
```bash
ensemble nve
compute_dos 10 1000
compute_phonon
run 100000
```

### 3. 模态分解 (可选)
```bash
compute_gkma 10 100 500
run 500000
```

## 输出文件解析 / Output File Analysis

### dos.out格式
```
# Frequency(THz) DOS
0.0 0.001
0.1 0.002
...
```

### phonon.out格式
```
# Mode Frequency(THz) Group_Velocity
1 2.5 1500.0
2 3.1 1200.0
...
```

### gkma.out格式
```
# Mode k_alpha kappa(W/mK)
1 0.5 10.2
2 0.3 8.5
...
```

## 应用场景 / Applications

### 体材料热导率
- 声子态密度分析
- 模态热导率分解
- 散射机制研究

### 界面热输运
- 声子透射系数
- 界面热阻
- 声子匹配分析

### 低维材料
- 纳米线热导率
- 二维材料声子性质
- 尺寸效应

## 参数建议 / Parameter Recommendations

| 计算 | sample | Nc | 运行步数 |
|------|--------|-----|---------|
| compute_dos | 10-100 | 500-2000 | 100k-500k |
| compute_phonon | 10-50 | 1000-5000 | 200k-1M |
| compute_gkma | 10-50 | 500-2000 | 500k-2M |

## 收敛性检查 / Convergence Checks

### 系统尺寸
- 测试不同超胞尺寸
- 检查声子谱收敛

### 时间步长
- 确保1 fs稳定性
- 检查能量守恒

### 采样参数
- sample: 足够的统计采样
- Nc: 充分的相关长度

## 参考资料 / References

- GPUMD声子分析文档
- 声子热输运理论
- 晶格动力学基础
