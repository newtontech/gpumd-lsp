# API参考 / API Reference

## LSP服务器API / LSP Server API

### 启动方式
```bash
# stdio模式 (编辑器使用)
gpumd-lsp --stdio

# JSON-RPC over stdin/stdout
```

### 支持的LSP功能

#### 1. initialize
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "processId": 12345,
    "rootUri": "file:///path/to/project",
    "capabilities": {}
  }
}
```

#### 2. textDocument/didOpen
```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/didOpen",
  "params": {
    "textDocument": {
      "uri": "file:///path/to/run.in",
      "languageId": "gpumd",
      "version": 1,
      "text": "potential nep.txt\nensemble nve\n"
    }
  }
}
```

#### 3. textDocument/didChange
```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/didChange",
  "params": {
    "textDocument": {
      "uri": "file:///path/to/run.in",
      "version": 2
    },
    "contentChanges": [...]
  }
}
```

#### 4. textDocument/completion
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "textDocument/completion",
  "params": {
    "textDocument": {
      "uri": "file:///path/to/run.in"
    },
    "position": {
      "line": 0,
      "character": 5
    }
  }
}
```

**响应**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "isIncomplete": false,
    "items": [
      {
        "label": "potential",
        "kind": 2,
        "detail": "potential <filename>",
        "documentation": "Set potential file; must be first in run.in.",
        "insertText": "potential "
      }
    ]
  }
}
```

#### 5. textDocument/hover
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "textDocument/hover",
  "params": {
    "textDocument": {
      "uri": "file:///path/to/run.in"
    },
    "position": {
      "line": 0,
      "character": 3
    }
  }
}
```

**响应**:
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "contents": {
      "kind": "markdown",
      "value": "**potential** <filename>\n\nSpecify the potential file..."
    }
  }
}
```

## CLI API / CLI API

### gpumd-lint
```bash
# 基本用法
gpumd-lint <path> [--json]

# 示例
gpumd-lint ./case
gpumd-lint ./run.in --json

# 输出格式 (JSON)
{
  "diagnostics": [
    {
      "code": "GPUMD010",
      "severity": "error",
      "message": "...",
      "file": "...",
      "line": 1
    }
  ],
  "summary": {
    "errors": 1,
    "warnings": 0
  }
}
```

### gpumd-fmt
```bash
# 基本用法
gpumd-fmt [-w] <file>

# 示例
gpumd-fmt run.in           # 输出格式化结果
gpumd-fmt -w run.in        # 写入文件

# 格式化规则
1. 关键字对齐 (24字符)
2. 参数格式化
3. 保留注释
4. 末尾换行
```

### gpumd-test
```bash
# 静态检查
gpumd-test static <path> [--json]

# 示例
gpumd-test static ./case --json
```

### gpumd-lsp-tool
```bash
# 检查
gpumd-lsp-tool check <path> --format json

# 上下文
gpumd-lsp-tool context <path> --format json

# 补全
gpumd-lsp-tool complete <path> --format json

# 悬浮
gpumd-lsp-tool hover <path> --format json

# 符号
gpumd-lsp-tool symbols <path> --format json

# 修复
gpumd-lsp-tool fix <path> --format json
```

## Python API / Python API

### 直接导入
```python
from pathlib import Path
from gpumd_lsp.analyzer import analyze_file, analyze_text

# 分析文件
diagnostics = analyze_file(Path("run.in"))

# 分析文本
content = "potential nep.txt\nensemble nve\n"
diagnostics = analyze_text(Path("run.in"), content)

# 结果
for diag in diagnostics:
    print(f"{diag.code}: {diag.message}")
```

### 诊断对象
```python
from gpumd_lsp.diagnostics import Diagnostic

# 属性
diag.code           # 诊断代码
diag.severity       # 严重程度
diag.message        # 消息
diag.file           # 文件路径
diag.line           # 行号
diag.confidence     # 置信度
diag.suggested_fix  # 修复建议
```

### Lint规则
```python
from gpumd_lsp.lint import lint_run_in_line

# 使用lint规则
diagnostics = lint_run_in_line(
    path=Path("run.in"),
    line_no=1,
    line="potential nep.txt",
    base_dir=Path(".")
)
```

## 数据结构 / Data Structures

### Diagnostic
```python
class Diagnostic:
    code: str           # GPUMD-XXX
    severity: str       # error/warning/information/hint
    message: str       # 描述信息
    file: str          # 文件路径
    line: int          # 行号
    confidence: float  # 0-1
    suggested_fix: dict | None
```

### Completion Item
```python
class CompletionItem:
    label: str         # 显示文本
    detail: str        # 详细信息
    documentation: str  # 文档
    insertText: str    # 插入文本
```

### Command Signature
```python
# COMMAND_SIGNATURES结构
{
    "command": (
        min_args,      # 最少参数
        max_args,      # 最多参数 (-1表示无限制)
        [(check_fn, label), ...]  # 类型检查函数
    )
}
```

## 错误处理 / Error Handling

### 异常类型
```python
# 文件不存在
FileNotFoundError

# 编码错误
UnicodeDecodeError

# 解析错误
# → 返回Diagnostic, 不抛异常
```

### 返回约定
```python
# 成功: 返回list[Diagnostic]
# 失败: 返回包含错误码的Diagnostic

analyze_file(path)  # 永不抛异常
```

## 参考资料 / References

- LSP规范: https://microsoft.github.io/language-server-protocol/
- pygls文档: Python LSP框架
