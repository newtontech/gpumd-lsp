# GPUMD LSP 知识库索引 / GPUMD LSP Knowledge Base Index

## 概述 / Overview

This is a Karpathy-style LLM Wiki for the gpumd-lsp project, containing domain knowledge about GPUMD molecular dynamics simulations and the Language Server Protocol implementation.

## 导航 / Navigation

### 快速开始 / Quick Start
- [项目README](raw/assets/README.md) - 项目概述
- [输入格式指南](wiki/synthesis/input-format-guide.md) - run.in/nep.in格式
- [命令参考](wiki/synthesis/command-reference.md) - 完整命令列表
- [工作流指南](wiki/synthesis/workflow-guide.md) - 典型工作流程

### 实体知识 / Entity Knowledge
- [GPUMD软件](wiki/entities/gpumd-software.md) - GPUMD概述
- [NEP势函数](wiki/entities/nep-potential.md) - 神经演化势函数
- [run.in格式](wiki/entities/run-in-format.md) - 主输入文件
- [系综恒温器](wiki/entities/ensemble-thermostat.md) - 热浴/压浴控制
- [计算命令](wiki/entities/compute-commands.md) - 属性计算
- [输出命令](wiki/entities/dump-commands.md) - 输出控制
- [诊断代码](wiki/entities/diagnostic-codes.md) - 错误代码说明
- [XYZ格式](wiki/entities/xyz-format.md) - 结构文件格式
- [声子分析](wiki/entities/phonon-analysis.md) - 声子性质计算
- [输出文件](wiki/entities/output-files.md) - 输出文件说明

### 概念知识 / Concept Knowledge
- [热输运](wiki/concepts/thermal-transport.md) - 热导率计算方法
- [LSP架构](wiki/concepts/lsp-architecture.md) - 语言服务器架构
- [MatMaster集成](wiki/concepts/matmaster-integration.md) - 工作流集成
- [性能优化](wiki/concepts/performance-optimization.md) - GPU加速优化
- [错误处理](wiki/concepts/error-handling.md) - 错误诊断和处理

### 综合知识 / Synthesis Knowledge
- [命令参考](wiki/synthesis/command-reference.md) - 完整命令参考
- [输入格式指南](wiki/synthesis/input-format-guide.md) - 格式规范
- [工作流指南](wiki/synthesis/workflow-guide.md) - 模拟工作流
- [API参考](wiki/synthesis/api-reference.md) - LSP/CLI API

## 原始资料 / Raw Sources

### 项目文档
- [README.md](raw/assets/README.md) - 项目说明
- [DIAGNOSTIC_ENGINE_V1.md](raw/assets/DIAGNOSTIC_ENGINE_V1.md) - 诊断引擎规范
- [AGENTS.md](raw/assets/AGENTS.md) - Agent工作流指南
- [pyproject.toml](raw/assets/pyproject.toml) - 项目配置

### 示例文件
- [run.in示例](raw/assets/run.in) - 有效的run.in文件
- [nep.in示例](raw/assets/nep.in) - 有效的nep.in文件

## 更新日志 / Change Log

参见 [log.md](log.md)

## 搜索指南 / Search Guide

### 按主题搜索

#### 模拟设置
- 关键词: potential, velocity, time_step, ensemble
- 相关: run.in格式, 系综恒温器

#### 热导率计算
- 关键词: hac, hnemd, shc, thermal_conductivity
- 相关: 热输运, 计算命令

#### 声子分析
- 关键词: phonon, dos, gkma
- 相关: 声子分析

#### NEP训练
- 关键词: nep, train_file, lambda
- 相关: NEP势函数, nep.in格式

#### 诊断和调试
- 关键词: error, warning, diagnostic
- 相关: 诊断代码, 错误处理

### 按文件类型搜索

#### run.in相关
- 命令参考
- 输入格式指南
- 工作流指南

#### nep.in相关
- NEP势函数
- 输入格式指南
- XYZ格式

#### LSP功能
- LSP架构
- API参考
- 诊断引擎

## 贡献指南 / Contributing

### 更新知识库
1. 在raw/assets/中添加原始资料
2. 在wiki/中创建/更新页面
3. 更新index.md和log.md
4. 保持中英双语格式

### 文档风格
- 使用中文标题 + 英文术语
- 提供代码示例
- 包含参考链接
- 保持简洁准确

## 参考资料 / External References

- GPUMD官方: https://github.com/brucefan1983/GPUMD
- NEP势函数: 相关论文
- LSP规范: https://microsoft.github.io/language-server-protocol/
- MatMaster: 内部工作流文档
