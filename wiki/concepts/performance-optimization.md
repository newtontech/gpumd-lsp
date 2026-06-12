# 性能优化概念 / Performance Optimization Concepts

## 概述 / Overview

GPUMD is designed for GPU acceleration. Understanding performance characteristics helps achieve optimal simulation throughput.

## GPU加速 / GPU Acceleration

### 架构优势
- 大规模并行: 数千原子同时计算
- 内存带宽: GPU显存远超CPU
- 计算密集: 力计算完全在GPU上

### 典型性能
| 系统 | CPU核数 | GPU | 加速比 |
|------|---------|-----|--------|
| 1000原子 | 8 | RTX 3080 | ~50x |
| 10000原子 | 16 | RTX 3080 | ~100x |
| 100000原子 | 32 | A100 | ~200x |

## 关键参数 / Key Parameters

### time_step (时间步长)

#### 推荐值
```bash
# NEP势函数
time_step 1    # 1 fs, 最常用
time_step 0.5  # 0.5 fs, 高精度

# 经验势
time_step 1    # 1 fs
time_step 2    # 2 fs, 谨慎使用
```

#### 平衡性
- 太大: 能量不守恒
- 太小: 模拟时间长

### neighbor (邻居表)

#### 参数设置
```bash
neighbor <skin> <update_freq>
```

#### 推荐值
| 系统 | skin | update_freq |
|------|------|-------------|
| 小系统 (<1000) | 0.5-1.0 | 10 |
| 中系统 (1000-10000) | 1.0-2.0 | 10-20 |
| 大系统 (>10000) | 2.0-5.0 | 20-50 |

#### 性能影响
- skin越大: 更新越少, 但内存占用多
- update_freq越大: 邻居表更新越少

## 批处理优化 / Batch Processing

### 单GPU多任务
```bash
# 同时运行多个小系统
gpumd case1/ &
gpumd case2/ &
gpumd case3/ &
wait
```

### 参数调整
- 减小update_freq (每个系统独立)
- 适当增大time_step (平衡精度)

## 内存管理 / Memory Management

### GPU内存需求
```
内存 ≈ 原子数 × (100-200) bytes
```

### 示例
| 原子数 | 内存需求 |
|--------|----------|
| 1,000 | ~200 MB |
| 10,000 | ~2 GB |
| 100,000 | ~20 GB |
| 1,000,000 | ~200 GB |

### 优化策略
- 多GPU: 分布式计算
- 内存回收: 定期清理
- 批大小控制

## 输出优化 / Output Optimization

### I/O瓶颈
```bash
# 不推荐 - 太频繁
dump_exyz 10 1    # 可能成为瓶颈

# 推荐 - 合理间隔
dump_exyz 1000 1
```

### 策略
- 平衡阶段: 较大interval
- 生产运行: 根据需要调整
- 仅输出必要数据

## 并行效率 / Parallel Efficiency

### 强扩展
```
加速比 = T(1核) / T(N核)
```

### 弱扩展
```
效率 = (1核时间×问题规模) / (N核时间×N倍问题规模)
```

### 最佳实践
- 单GPU: 充分利用
- 多GPU: 负载均衡
- 混合并行: MPI + GPU

## 性能分析 / Performance Analysis

### 监控指标
- 每步时间 (ns/step)
- 内存使用 (GB)
- GPU利用率 (%)

### 诊断
```bash
# 查看GPU使用
nvidia-smi

# 检查性能瓶颈
gpumd --benchmark
```

## 常见问题 / Common Issues

### 内存不足
```
症状: 模拟启动失败
解决:
1. 减小系统尺寸
2. 使用多GPU
3. 减少输出
```

### 速度慢
```
症状: 每步时间过长
解决:
1. 检查update_freq
2. 减少输出频率
3. 优化neighbor参数
```

### 能量漂移
```
症状: 总能不守恒
解决:
1. 减小time_step
2. 检查势函数
3. 延长平衡时间
```

## 参考资料 / References

- GPU性能优化指南
- CUDA最佳实践
- GPUMD性能调优
