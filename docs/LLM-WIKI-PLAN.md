# GPUMD LSP Wiki 计划 / LLM Wiki Plan

## 概述 / Overview

本计划描述了gpumd-lsp项目的LLM Wiki结构,遵循Karpathy-style知识库模式。

## Wiki结构 / Wiki Structure

```
gpumd-lsp/
├── raw/
│   └── assets/              # 原始证据文件
│       ├── README.md
│       ├── DIAGNOSTIC_ENGINE_V1.md
│       ├── AGENTS.md
│       ├── pyproject.toml
│       ├── run.in
│       └── nep.in
│
├── wiki/
│   ├── entities/            # GPUMD特定实体
│   │   ├── gpumd-software.md
│   │   ├── nep-potential.md
│   │   ├── run-in-format.md
│   │   ├── ensemble-thermostat.md
│   │   ├── compute-commands.md
│   │   ├── dump-commands.md
│   │   ├── diagnostic-codes.md
│   │   ├── xyz-format.md
│   │   ├── phonon-analysis.md
│   │   └── output-files.md
│   │
│   ├── concepts/            # 跨领域概念
│   │   ├── thermal-transport.md
│   │   ├── lsp-architecture.md
│   │   ├── matmaster-integration.md
│   │   ├── performance-optimization.md
│   │   └── error-handling.md
│   │
│   └── synthesis/           # 综合参考
│       ├── command-reference.md
│       ├── input-format-guide.md
│       ├── workflow-guide.md
│       └── api-reference.md
│
├── index.md                 # 导航中心
└── log.md                   # 变更日志
```

## 内容规划 / Content Planning

### 实体知识 (Entity Knowledge) - 10个文件

| 文件 | 主题 | 关键内容 |
|------|------|----------|
| gpumd-software.md | 软件概述 | GPU加速, NEP势, 热输运 |
| nep-potential.md | NEP势函数 | 训练参数, 损失函数, 模型参数 |
| run-in-format.md | run.in格式 | 命令顺序, 语法规则 |
| ensemble-thermostat.md | 系综控制 | NVE/NVT/NPT, 恒温器 |
| compute-commands.md | 计算命令 | hac, hnemd, shc, dos等 |
| dump-commands.md | 输出命令 | thermo, position, exyz |
| diagnostic-codes.md | 诊断代码 | GPUMD-E06*, GPUMD010-014 |
| xyz-format.md | XYZ格式 | 扩展XYZ, NEP训练数据 |
| phonon-analysis.md | 声子分析 | DOS, 模态分解 |
| output-files.md | 输出文件 | thermo.out, hac.out等 |

### 概念知识 (Concept Knowledge) - 5个文件

| 文件 | 主题 | 关键内容 |
|------|------|----------|
| thermal-transport.md | 热输运 | Green-Kubo, HNEMD, SHC |
| lsp-architecture.md | LSP架构 | 分析器, 诊断, 提供者 |
| matmaster-integration.md | MatMaster | 执行守卫, 工作流 |
| performance-optimization.md | 性能优化 | GPU加速, 参数调优 |
| error-handling.md | 错误处理 | 常见错误, 调试 |

### 综合知识 (Synthesis Knowledge) - 4个文件

| 文件 | 主题 | 关键内容 |
|------|------|----------|
| command-reference.md | 命令参考 | 完整命令列表 |
| input-format-guide.md | 格式指南 | 语法规则, 格式化 |
| workflow-guide.md | 工作流 | 典型流程 |
| api-reference.md | API参考 | LSP/CLI接口 |

## GPUMD领域覆盖 / GPUMD Domain Coverage

### 核心概念
- [x] GPU加速MD模拟
- [x] NEP机器学习势
- [x] 热导率计算
- [x] 声子分析

### 输入文件
- [x] run.in语法和验证
- [x] nep.in训练参数
- [x] XYZ数据格式

### 命令类别
- [x] 系统设置 (potential, velocity, time_step)
- [x] 系综控制 (ensemble, run)
- [x] 计算命令 (compute_*)
- [x] 输出命令 (dump_*)

### LSP功能
- [x] 诊断引擎
- [x] 命令补全
- [x] 悬浮文档
- [x] CLI工具

## 文件统计 / File Statistics

- 总文件数: 21
- 实体页面: 10
- 概念页面: 5
- 综合页面: 4
- 原始资料: 6
- 导航文件: 2

## 使用指南 / Usage Guide

### LLM查询
```python
# 查询GPUMD命令
query: "run.in potential命令"
→ wiki/entities/run-in-format.md

# 查询NEP训练
query: "NEP lambda参数"
→ wiki/entities/nep-potential.md

# 查询热导率
query: "Green-Kubo热导率"
→ wiki/concepts/thermal-transport.md
```

### 编辑器集成
- LSP服务器: gpumd-lsp --stdio
- CLI验证: gpumd-lint ./case
- 格式化: gpumd-fmt input.in

## 维护计划 / Maintenance Plan

### 定期更新
- 每月检查GPUMD新版本
- 每季度审查LSP功能
- 根据用户反馈调整

### 扩展区域
1. 更多示例和最佳实践
2. PLUMED集成细节
3. DFT-D3使用指南
4. 故障排除案例

## 参考资料 / References

- GPUMD官方文档
- NEP势函数论文
- LSP规范
- MatMaster工作流
