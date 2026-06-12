# 诊断代码实体 / Diagnostic Codes Entity

## 概述 / Overview

gpumd-lsp uses GPUMD-prefixed diagnostic codes to classify issues found in GPUMD input files. Each code has a specific severity level and suggested fix.

## 错误代码 / Error Codes

### GPUMD-E060: 未知命令
```json
{
  "code": "GPUMD-E060",
  "severity": "error",
  "message": "unknown command '{token}'",
  "confidence": 0.85
}
```
**检查**: 命令是否在COMMAND_SIGNATURES或NEP_SIGNATURES中
**修复**: 检查拼写或查看有效命令列表

### GPUMD-E061: 参数数量错误
```json
{
  "code": "GPUMD-E061",
  "severity": "error",
  "message": "command '{cmd}' expects {n} argument(s), got {actual}",
  "confidence": 0.92
}
```
**检查**: 命令签名中的min_args和max_args
**修复**: 添加或删除参数

### GPUMD-E062: 参数类型错误
```json
{
  "code": "GPUMD-E062",
  "severity": "error",
  "message": "argument {i} should be {type}",
  "confidence": 0.88
}
```
**类型**:
- int: 整数
- float: 浮点数
- filepath: 文件路径

### GPUMD-E063: 模型文件缺失
```json
{
  "code": "GPUMD-E063",
  "severity": "error",
  "message": "potential model file not found",
  "confidence": 0.75
}
```
**检查**: potential命令中的文件路径
**修复**: 创建文件或修正路径

### GPUMD-E064: 训练文件缺失
```json
{
  "code": "GPUMD-E064",
  "severity": "error",
  "message": "NEP training file not found",
  "confidence": 0.80
}
```
**检查**: train_file和test_file路径
**修复**: 创建数据文件

### GPUMD-E065: 运行时错误
```json
{
  "code": "GPUMD-E065",
  "severity": "error",
  "message": "GPUMD runtime error: {msg}",
  "confidence": 0.90
}
```
**来源**: 解析run.out或runtime.log
**模式**: ERROR, FATAL, segmentation fault, MPI_ERR

## 警告代码 / Warning Codes

### GPUMD-W060: 恒温器无效
```json
{
  "code": "GPUMD-W060",
  "severity": "warning",
  "message": "unrecognized thermostat '{name}'",
  "confidence": 0.82
}
```
**已知恒温器**:
- nve
- nvt_ber / nvt_berendsen
- nvt_nose_hoover
- npt_ber / npt_berendsen
- npt_mtk
- heat_bc

### GPUMD001: 未知关键字 (遗留)
```json
{
  "code": "GPUMD001",
  "severity": "warning",
  "message": "unknown keyword",
  "confidence": 0.55
}
```
**注意**: 为向后兼容保留，新代码使用GPUMD-E060

## MatMaster守卫代码 / MatMaster Guard Codes

### GPUMD010: potential首行检查
```json
{
  "code": "GPUMD010",
  "severity": "error",
  "message": "potential must be first command",
  "confidence": 0.90
}
```
**规则**: potential必须是第一条非注释命令

### GPUMD011: compute/dump顺序
```json
{
  "code": "GPUMD011",
  "severity": "warning",
  "message": "compute/dump should be before run",
  "confidence": 0.80
}
```
**规则**: 声明在run之前

### GPUMD012: run命令必需
```json
{
  "code": "GPUMD012",
  "severity": "warning",
  "message": "no run command found",
  "confidence": 0.85
}
```
**规则**: 至少需要一个run命令

### GPUMD013: ensemble顺序
```json
{
  "code": "GPUMD013",
  "severity": "warning",
  "message": "ensemble should be before run",
  "confidence": 0.80
}
```
**规则**: ensemble在第一个run之前

### GPUMD014: nep训练文件
```json
{
  "code": "GPUMD014",
  "severity": "information",
  "message": "should specify train_file",
  "confidence": 0.70
}
```
**规则**: nep.in应该有train_file

## 其他代码 / Other Codes

### GPUMD101: 必需令牌缺失
```json
{
  "code": "GPUMD101",
  "severity": "warning",
  "message": "expected token not found",
  "confidence": 0.72
}
```
**检查**: REQUIRED_TOKENS列表

### GPUMD201: 无支持文件
```json
{
  "code": "GPUMD201",
  "severity": "error",
  "message": "no supported files found",
  "confidence": 1.00
}
```
**检查**: 目录中是否有run.in或nep.in

### GPUMD202: 编码错误
```json
{
  "code": "GPUMD202",
  "severity": "error",
  "message": "file is not valid UTF-8",
  "confidence": 1.00
}
```
**修复**: 转换为UTF-8编码

## 严重程度映射 / Severity Mapping

| 严重程度 | 含义 | 阻止 |
|----------|------|------|
| error | 高置信度问题 | 是 |
| warning | 高风险输入 | 否 |
| information | 信息提示 | 否 |
| hint | 优化建议 | 否 |

## 类别映射 / Category Mapping

| 类别 | 描述 |
|------|------|
| syntax | 解析错误 |
| schema | 结构违规 |
| type/value | 无效参数 |
| cross-file reference | 文件引用 |
| semantic consistency | 逻辑错误 |
| preflight/runtime-risk | 执行风险 |
| style/deprecation | 编码风格 |

## 参考资料 / References

- DIAGNOSTIC_ENGINE_V1.md: 完整诊断合约
- lint.py: 诊断规则实现
