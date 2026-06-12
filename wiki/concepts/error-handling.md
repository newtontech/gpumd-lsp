# 错误处理概念 / Error Handling Concepts

## 概述 / Overview

Understanding common errors in GPUMD simulations and how the LSP helps identify and prevent them.

## 错误分类 / Error Categories

### 1. 输入文件错误 / Input File Errors

#### GPUMD-E063: 模型文件缺失
```bash
# 错误示例
potential missing_nep.txt

# 诊断输出
{
  "code": "GPUMD-E063",
  "severity": "error",
  "message": "potential model file 'missing_nep.txt' not found",
  "suggested_fix": {"kind": "check_file_path", "file": "missing_nep.txt"}
}
```

#### 解决方案
1. 检查文件路径
2. 确认nep.txt存在
3. 使用相对/绝对路径

#### GPUMD-E064: 训练文件缺失
```bash
# nep.in中
train_file missing_train.xyz

# 诊断输出
{
  "code": "GPUMD-E064",
  "message": "NEP training file not found"
}
```

### 2. 命令语法错误 / Command Syntax Errors

#### GPUMD-E060: 未知命令
```bash
# 拼写错误
potental nep.txt  # 错误: potential

# 诊断输出
{
  "code": "GPUMD-E060",
  "message": "unknown command 'potental'",
  "suggested_fix": {"kind": "check_keyword_spelling"}
}
```

#### GPUMD-E061: 参数数量错误
```bash
# 参数不足
ensemble nvt_ber 300  # 缺少参数

# 诊断输出
{
  "code": "GPUMD-E061",
  "message": "nvt_ber expects exactly 3 parameter(s), got 2"
}
```

#### GPUMD-E062: 参数类型错误
```bash
# 类型错误
time_step 1.5.3  # 非法浮点数

# 诊断输出
{
  "code": "GPUMD-E062",
  "message": "argument 1 should be dt (float)"
}
```

### 3. 逻辑错误 / Logic Errors

#### GPUMD010: potential顺序错误
```bash
# 错误顺序
velocity 300 12345
potential nep.txt

# 诊断输出
{
  "code": "GPUMD010",
  "message": "potential must be first command"
}
```

#### GPUMD013: ensemble顺序错误
```bash
# ensemble在run之后
run 10000
ensemble nve

# 诊断输出
{
  "code": "GPUMD013",
  "message": "ensemble should be before run"
}
```

## 运行时错误 / Runtime Errors

### GPUMD-E065: 运行时解析

#### 检测模式
```python
# LSP自动检测这些模式
"ERROR: division by zero"
"FATAL: cannot open file"
"segmentation fault"
"MPI_ERR: communication failed"
"GPUMD exited with code 1"
```

#### 日志文件
```
# LSP检查这些文件
run.out
runtime.log
gpumd.out
```

### 常见运行时问题

#### 1. 内存不足
```
症状: 模拟中途退出
日志: "out of memory" 或 "segmentation fault"

解决方案:
1. 减小系统尺寸
2. 使用多GPU
3. 检查GPU内存
```

#### 2. 能量发散
```
症状: 能量急剧上升
日志: "ERROR: energy NaN"

解决方案:
1. 减小time_step
2. 检查势函数
3. 延长平衡时间
```

#### 3. 文件访问错误
```
症状: 无法读取/写入文件
日志: "ERROR: cannot open file"

解决方案:
1. 检查文件权限
2. 确认路径正确
3. 检查磁盘空间
```

## LSP错误预防 / LSP Error Prevention

### 编辑时检查
```
1. 实时诊断
   ├─ 语法高亮
   ├─ 参数验证
   └─ 文件存在检查

2. 悬浮文档
   ├─ 命令说明
   ├─ 参数要求
   └─ 使用示例

3. 自动补全
   ├─ 关键字提示
   ├─ 参数引导
   └─ 文件路径提示
```

### 运行前检查
```bash
# 综合检查
gpumd-lint ./case --json

# 返回所有诊断
{
  "diagnostics": [...],
  "summary": {
    "errors": N,
    "warnings": M,
    "blocking": true/false
  }
}
```

## 错误处理工作流 / Error Handling Workflow

```
1. 编写输入
   └─ 使用LSP辅助

2. 运行前检查
   └─ gpumd-lint

3. 执行模拟
   └─ GPUMD

4. 检查日志
   └─ LSP自动解析run.out

5. 分析错误
   └─ 查看诊断

6. 修复问题
   └─ 参考suggested_fix

7. 重新检查
   └─ 返回步骤2
```

## 调试技巧 / Debugging Tips

### 最小化问题
```bash
# 从最简单的run.in开始
potential nep.txt
ensemble nve
run 100

# 逐步添加功能
```

### 验证势函数
```bash
# 使用小系统测试
velocity 0 12345
run 0  # 单点能量计算
```

### 检查能量守恒
```bash
# NVE模拟能量应守恒
ensemble nve
dump_thermo 10
run 10000

# 检查thermo.out中总能量变化
```

## 参考资料 / References

- 诊断代码: wiki/entities/diagnostic-codes.md
- 命令参考: wiki/synthesis/command-reference.md
- GPUMD错误手册
