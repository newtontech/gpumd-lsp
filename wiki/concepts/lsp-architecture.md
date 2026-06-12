# LSP架构概念 / LSP Architecture Concepts

## 概述 / Overview

The gpumd-lsp implements a Language Server Protocol (LSP) server for GPUMD input files, providing editor integration features like syntax validation, completion, and hover documentation.

## 架构组件 / Architecture Components

### Core Modules

#### 1. Analyzer (analyzer.py)
- **Purpose**: File analysis and diagnostic generation
- **Functions**:
  - `analyze_path()`: Directory/file analysis
  - `analyze_file()`: Single file processing
  - `analyze_text()`: In-memory text analysis
- **Scope**: run.in and nep.in files

#### 2. Lint Rules (lint.py)
- **Purpose**: GPUMD-specific validation
- **Rule Types**:
  - Command signatures
  - Argument counts
  - Type checking
  - File existence
  - Runtime log parsing

#### 3. Diagnostics (diagnostics.py)
- **Purpose**: Standardized diagnostic format
- **Rich Diagnostic Shape**:
```json
{
  "code": "GPUMD-E061",
  "severity": "error",
  "category": "schema",
  "confidence": 0.92,
  "message": "...",
  "suggested_fix": {...}
}
```

### LSP Providers

#### Completion Provider
- **File**: completion.py
- **Scope**: run.in and nep.in keywords
- **Features**:
  - Command labels
  - Parameter hints
  - Documentation strings

#### Hover Provider
- **File**: hover.py
- **Scope**: Command documentation
- **Format**: Markdown with parameter descriptions

#### Code Actions
- **Future**: Auto-fix suggestions
- **Integration**: Rich diagnostic fix hints

## CLI Surface / CLI接口

### Main Commands
```bash
# LSP server (stdio mode)
gpumd-lsp --stdio

# Linting
gpumd-lint ./case --json

# Formatting
gpumd-fmt -w input.file

# Testing
gpumd-test static ./case --json
```

### Agent Tool
```bash
gpumd-lsp-tool check path/to/input --format json
gpumd-lsp-tool context path/to/input --format json
gpumd-lsp-tool complete path/to/input --format json
gpumd-lsp-tool hover path/to/input --format json
gpumd-lsp-tool symbols path/to/input --format json
gpumd-lsp-tool fix path/to/input --format json
```

## 诊断流程 / Diagnostic Flow

```
1. File Detection
   ├─ FILE_PATTERNS: ["run.in", "nep.in"]
   └─ Supported files check

2. Token Extraction
   ├─ Meaningful lines (no comments)
   └─ Command token identification

3. Validation
   ├─ Required token checks
   ├─ Unknown keyword detection
   ├─ Command signature validation
   ├─ Argument type checking
   ├─ File existence checks
   └─ MatMaster guard rules

4. Diagnostic Generation
   ├─ Code assignment (GPUMD-*)
   ├─ Severity classification
   └─ Suggested fix hints
```

## 严重程度策略 / Severity Policy

| Severity | Criteria | Blocking |
|----------|----------|----------|
| error | High-confidence syntax/schema issues | Yes |
| warning | High-risk/suspicious input | No |
| information | Style/documentation | No |
| hint | Optional optimizations | No |

## 诊断类别 / Diagnostic Categories

1. **syntax**: Parsing errors
2. **schema**: Structure violations
3. **type/value**: Invalid arguments
4. **cross-file reference**: Missing files
5. **semantic consistency**: Logical errors
6. **preflight/runtime-risk**: Execution risks
7. **style/deprecation**: Coding style

## 扩展性 / Extensibility

### Adding New Commands
1. Add to `COMMAND_SIGNATURES` or `NEP_SIGNATURES`
2. Add completion item in completion.py
3. Add hover documentation in hover.py
4. Update tests

### Adding New Rules
1. Implement lint function in lint.py
2. Register with GPUMD-prefixed code
3. Add validation logic
4. Document in wiki

## 参考资料 / References

- LSP Specification: https://microsoft.github.io/language-server-protocol/
- pygls documentation: Python LSP framework
- Diagnostic Engine V1: docs/DIAGNOSTIC_ENGINE_V1.md
