# OpenQC Agent Context

OpenQC consumes `gpumd-lsp-tool` and `lsp-capabilities.json` to assemble diagnostics, hover, completion, symbols, examples, next-token guidance, and repair-plan hints for `gpumd` documents.

## Agent CLI Surface

```bash
gpumd-lsp-tool capabilities    # Report supported operations
gpumd-lsp-tool check <path>    # Run diagnostics with DiagnosticEnvelope/v1
gpumd-lsp-tool context <path>  # Position-aware context (token, symbols, diagnostics)
gpumd-lsp-tool complete <path> # Command completion (run.in and nep.in)
gpumd-lsp-tool hover <path>    # Hover documentation
gpumd-lsp-tool symbols <path>  # Document symbols
gpumd-lsp-tool fix <path>      # Quick-fix actions
```

## Capabilities from lsp-capabilities.json

- `agent-envelope` — DiagnosticEnvelope/v1 JSON output
- `blocking-gate` — Error diagnostics block run-gate and Bohrium submission
- `completion` — 26 run.in + 16 nep.in keywords documented
- `diagnostics` — 12 lint codes (GPUMD-E060 through GPUMD014)
- `hover` — Source-grounded command documentation
- `source-provenance` — Official GPUMD docs links
- `output-log-diagnostics` — Parse runtime errors from run.out

## Source Provenance

Hover and completion documentation in `src/gpumd_lsp/completion.py` and
`src/gpumd_lsp/hover.py` reference:
- GPUMD docs: <https://gpumd.org/>
- NEP docs: <https://gpumd.org/nep.html>
- See `raw/assets/upstream-sources.md` for complete command→URL mapping

## Related Pages

- [GPUMD software](wiki/entities/gpumd-software.md) — Software overview
- [run.in format](wiki/entities/run-in-format.md) — Main input file
- [NEP potential](wiki/entities/nep-potential.md) — NEP training config
- [Diagnostic codes](wiki/entities/diagnostic-codes.md) — Error code catalog
- [Diagnostic engine](wiki/concepts/diagnostic-engine-v1.md) — Engine contract
