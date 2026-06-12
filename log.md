# GPUMD LSP Wiki 更新日志 / Change Log

## 2026-06-13 - Upstream Docs Closeout (#28)

**Scope**: Fill upstream documentation coverage gaps, add official examples, cross-reference wiki pages, create wiki lint.

**Content Added**:
- `raw/assets/upstream-sources.md` — Official GPUMD docs link manifest (gpumd.org)
- `raw/assets/examples-thermal-conductivity.in` — Green-Kubo thermal conductivity example
- `raw/assets/examples-nep-training.in` — NEP training configuration example
- `scripts/wiki-lint.sh` — Lightweight wiki integrity checker

**Pages Updated**:
- `wiki/entities/gpumd-software.md` — Added official reference links and cross-references
- `wiki/entities/run-in-format.md` — Added official docs links and example references
- `wiki/entities/diagnostic-codes.md` — Added cross-references to related pages
- `wiki/concepts/diagnostic-engine-v1.md` — Expanded with code table and cross-references
- `wiki/synthesis/openqc-agent-context.md` — Expanded with CLI surface and capabilities
- `index.md` — Added raw asset listings for new files
- `log.md` — This entry

**LSP-facing Update**:
- Updated `lsp-capabilities.json` sourceProvenance with additional upstream URLs
- Hover docs in `completion.py`/`hover.py` now traceable to wiki via upstream-sources.md manifest

## 2026-06-12 - 初始创建 / Initial Creation

### 创建的文件 / Files Created (21个)

#### 原始资料 / Raw Assets (6个)
- raw/assets/README.md - 项目概述
- raw/assets/DIAGNOSTIC_ENGINE_V1.md - 诊断引擎规范
- raw/assets/AGENTS.md - Agent工作流指南
- raw/assets/pyproject.toml - 项目配置
- raw/assets/run.in - 有效示例
- raw/assets/nep.in - 有效示例

#### 实体页面 / Entity Pages (10个)
1. wiki/entities/gpumd-software.md - GPUMD软件概述
2. wiki/entities/nep-potential.md - NEP势函数详解
3. wiki/entities/run-in-format.md - run.in文件格式
4. wiki/entities/ensemble-thermostat.md - 系综和恒温器
5. wiki/entities/compute-commands.md - 计算命令
6. wiki/entities/dump-commands.md - 输出命令
7. wiki/entities/diagnostic-codes.md - 诊断代码
8. wiki/entities/xyz-format.md - XYZ格式
9. wiki/entities/phonon-analysis.md - 声子分析
10. wiki/entities/output-files.md - 输出文件

#### 概念页面 / Concept Pages (5个)
1. wiki/concepts/thermal-transport.md - 热输运概念
2. wiki/concepts/lsp-architecture.md - LSP架构
3. wiki/concepts/matmaster-integration.md - MatMaster集成
4. wiki/concepts/performance-optimization.md - 性能优化
5. wiki/concepts/error-handling.md - 错误处理

#### 综合页面 / Synthesis Pages (4个)
1. wiki/synthesis/command-reference.md - 命令参考
2. wiki/synthesis/input-format-guide.md - 输入格式指南
3. wiki/synthesis/workflow-guide.md - 工作流指南
4. wiki/synthesis/api-reference.md - API参考

#### 导航文件 / Navigation (2个)
- index.md - 知识库索引
- log.md - 本文件

### 覆盖主题 / Covered Topics

#### GPUMD领域知识
- 软件概述和特性
- NEP势函数训练
- run.in/nep.in文件格式
- 系综控制 (NVE, NVT, NPT)
- 热输运计算 (GK, HNEMD, SHC)
- 声子分析
- 输出文件格式

#### LSP功能
- 诊断引擎
- 命令补全
- 悬浮文档
- CLI工具
- API接口

#### 工作流
- NEP训练流程
- MD模拟流程
- 热导率计算
- MatMaster集成

### 待扩展区域 / Areas for Expansion

1. 更多compute_*命令详细说明
2. PLUMED集成细节
3. DFT-D3色散校正
4. 更多示例和最佳实践
5. 故障排除指南
6. 性能基准测试

## 维护指南 / Maintenance Guide

### 更新流程
1. 在raw/assets/中添加新证据
2. 在适当分类下创建新页面
3. 更新index.md
4. 在此文件添加条目

### 审查周期
- 每月检查GPUMD更新
- 每季度审查LSP功能
- 根据用户反馈调整
