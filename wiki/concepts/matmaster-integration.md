# MatMaster集成概念 / MatMaster Integration Concepts

## 概述 / Overview

gpumd-lsp is designed to integrate with MatMaster workflows, providing validation and diagnostics for GPUMD simulation inputs used in materials science automation pipelines.

## MatMaster执行守卫 / MatMaster Execution Guards

The LSP enforces MatMaster-specific execution rules derived from workflow contracts:

### Guard Rules

1. **potential_first**
```python
"potential must be the first non-comment command in run.in"
```
- **Severity**: Error (GPUMD010)
- **Check**: First meaningful line must be `potential`
- **Confidence**: 0.9

2. **run_required**
```python
"at least one 'run' command is required for simulation"
```
- **Severity**: Warning (GPUMD012)
- **Check**: At least one `run` command present
- **Confidence**: 0.85

3. **ensemble_before_run**
```python
"ensemble must be declared before run"
```
- **Severity**: Warning (GPUMD013)
- **Check**: `ensemble` appears before first `run`
- **Confidence**: 0.80

4. **compute_before_run**
```python
"compute_*/dump_* commands must appear before run"
```
- **Severity**: Warning (GPUMD011)
- **Check**: Compute/dump before `run`
- **Confidence**: 0.80

5. **model_file_exists**
```python
"potential model file must exist on disk"
```
- **Severity**: Error (GPUMD-E063)
- **Check**: File path validation
- **Confidence**: 0.75

6. **nep_train_file_exists**
```python
"train_file must exist for NEP training"
```
- **Severity**: Error (GPUMD-E064)
- **Check**: train_file path validation
- **Confidence**: 0.80

## 工作流集成 / Workflow Integration

### MatMaster Pipeline
```
1. Input generation
   ├─ LSP validation
   └─ Pre-flight checks

2. Simulation execution
   ├─ GPUMD runtime
   └─ log file parsing

3. Output analysis
   ├─ Result validation
   └─ Post-processing
```

### LSP Role
- **Pre-execution**: Validate inputs
- **During execution**: Parse runtime logs
- **Post-execution**: Diagnose failures

## 诊断合约 / Diagnostic Contract

The LSP follows the shared newtontech Scientific LSP diagnostics contract:

### Rich Diagnostic Shape
```json
{
  "code": "STABLE_CODE",
  "severity": "error",
  "category": "schema",
  "confidence": 1.0,
  "source": "gpumd-lsp",
  "range": {
    "start": {"line": 0, "character": 0},
    "end": {"line": 0, "character": 1}
  },
  "software": "gpumd",
  "file_type": "input",
  "path": "input",
  "expected": null,
  "actual": null,
  "manual_ref": null,
  "fix_hints": [],
  "blocking": true
}
```

### Agent-Facing JSON
Deterministic JSON output for automation:
- `--format json` flag
- Stable structure
- Machine-readable
- Includes fix suggestions

## 运行时日志解析 / Runtime Log Parsing

### Supported Patterns
```python
_RUNTIME_ERROR_PATTERNS = [
    "ERROR[:\\s]+(.+)",
    "FATAL[:\\s]+(.+)",
    "segmentation fault",
    "MPI_ERR",
    "GPUMD exited with code (\\d+)"
]
```

### Log File Detection
```python
RUNTIME_LOG_PATTERNS = [
    "run.out",
    "runtime.log",
    "gpumd.out"
]
```

## 自动化工作流 / Automation Workflows

### Check/Repair/Recheck Loop
```bash
# 1. Check
gpumd-lsp-tool check path/to/input --format json

# 2. Fix (manual or automated)
# Apply suggested fixes from diagnostics

# 3. Recheck
gpumd-lsp-tool check path/to/input --format json
```

### Pre-flight Validation
```bash
# Validate entire case directory
gpumd-lint ./case --json

# Returns:
# - File analysis
# - Diagnostics
# - Blocking issues
# - Fix suggestions
```

## 参考资料 / References

- DIAGNOSTIC_ENGINE_V1.md: Full diagnostic contract
- MatMaster workflow contracts
- Scientific LSP provider model
