# Diagnostic Engine v1

GPUMD diagnostics use `DiagnosticEnvelope/v1` with `error`, `warning`, `information`, and `hint` severities. Blocking behavior is controlled by `lsp-capabilities.json`, not by OpenQC guesswork.

## Source

- Contract spec: `raw/assets/DIAGNOSTIC_ENGINE_V1.md`
- Schema: `diagnostics/diagnostic-engine-v1.schema.json`
- Implementation: `src/gpumd_lsp/lint.py`, `src/gpumd_lsp/rich_diagnostics.py`

## Diagnostic Codes (GPUMD prefix)

| Code | Severity | Description |
|------|----------|-------------|
| GPUMD-E060 | error | Unknown command |
| GPUMD-E061 | error | Invalid argument count |
| GPUMD-E062 | error | Invalid argument type |
| GPUMD-E063 | error | Missing model file |
| GPUMD-E064 | error | Missing NEP training file |
| GPUMD-E065 | error | Runtime error from log |
| GPUMD-W060 | warning | Invalid thermostat |
| GPUMD010 | error | potential must be first command |
| GPUMD011 | warning | compute/dump before run |
| GPUMD012 | warning | At least one run required |
| GPUMD013 | warning | ensemble before run |
| GPUMD014 | info | NEP train_file recommended |

## Related Pages

- [Diagnostic codes](wiki/entities/diagnostic-codes.md) — Full code catalog with examples
- [GPUMD software](wiki/entities/gpumd-software.md) — Software overview
- [Error handling](wiki/concepts/error-handling.md) — Error handling patterns
- [OpenQC agent context](wiki/synthesis/openqc-agent-context.md) — Agent integration
