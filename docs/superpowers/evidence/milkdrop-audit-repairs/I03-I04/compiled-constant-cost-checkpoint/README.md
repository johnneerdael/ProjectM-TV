# Compiled-constant workload observations

These three12-run ABBA comparisons use literal expressions folded by the evaluator at preset load time. They are valid frozen whole-engine measurements for those compiled presets, but do not isolate repaired runtime arithmetic callback cost. Do not adopt or defer I03/I04 based on a supposed per-node callback increase from these numbers. Runtime-Q input variants and compiler/runtime verification are required.

Division/remainder workload:1.478911→1.496395ms (+1.182%); tiny-power workload:1.514549→1.554497ms (+2.638%); ordinary workload:1.557408→1.553208ms (−.270%). These differing patterns and the compiled-constant scope remain visible. No shipping code was changed.
