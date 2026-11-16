# Evidence archive and provenance

Feature PRs contain no raw experiment JSON. No unique experiment has been deleted. The original integrated branch and its public immutable commit remain available, plus local backup ref/bundle. The full current run archive contains commands, final/failed run logs, source/native manifests,42 benchmark processes and profiler traces; it is an evidence artifact, not a source-feature dependency.

## Historical raw data (original551, not current-head runs)

| File | Lines | SHA256 | Immutable public reference |
|---|---:|---|---|
| benchmark_results.json | 362 | `0c37807faf37adb9cd0c475d0dd8a01c45018da50a5836b44589acf69e87e1df` | [original data](https://github.com/WEIXILIN0307/recsys-examples/blob/8518eddaf1ac3da2cca6070215b7841ddccfe2f9/corelib/dynamicemb/benchmark/benchmark_results.json) |
| input_dist_dense_lookup_results.json | 7267 | `cccdfb1ef3c2a3b6149fb43556c19ad07160b754879606c6a1d53ed0c1f4ba58` | [original data](https://github.com/WEIXILIN0307/recsys-examples/blob/8518eddaf1ac3da2cca6070215b7841ddccfe2f9/corelib/dynamicemb/benchmark/input_dist_dense_lookup_results.json) |
| input_dist_optimization_results.json | 10034 | `3a7b83d75ecf5f6e3cf3518076bb3df9c6240ae84b515abc28ccd479ba8a7489` | [original data](https://github.com/WEIXILIN0307/recsys-examples/blob/8518eddaf1ac3da2cca6070215b7841ddccfe2f9/corelib/dynamicemb/benchmark/input_dist_optimization_results.json) |
| input_dist_review_results.json | 7481 | `ea80ae5627d357e88d7be32e25e355b46ccef73ca766aba0030cbe23f2208528` | [original data](https://github.com/WEIXILIN0307/recsys-examples/blob/8518eddaf1ac3da2cca6070215b7841ddccfe2f9/corelib/dynamicemb/benchmark/input_dist_review_results.json) |
| resolved_lookup_results.json | 309 | `f17ad05b58f304b7b82dc00f71f195dee1a07c8eaf686bd279652c13e5462685` | [original data](https://github.com/WEIXILIN0307/recsys-examples/blob/8518eddaf1ac3da2cca6070215b7841ddccfe2f9/corelib/dynamicemb/benchmark/resolved_lookup_results.json) |

## Current experiment artifact

`evidence-current.tar.gz` is accompanied by a SHA256 sidecar and a file-by-file SHA256 manifest. It contains the evidence/ and build/*/manifest.json records; it does not contain authentication config, credentials or dependency/GPU binaries. `performance.jsonl` and summarized tables are also directly readable. Some records intentionally capture failed intermediate or combined-module commands; PR_VALIDATION_MATRIX distinguishes them from final successful invocations.

All final prefix commits, own-parent stats, original207-hunk ownership inventory, full41-file mapping, production equivalence and native compile argv are recorded. Newer main08eed12 is a separate fetched source with a saved semantic merge conflict; no build/runtime pass is claimed for it. Original source8518edd and the previous all-backend split remain unchanged.

See PR_SPLIT_PLAN for exact PR URLs. The local integration-reference branch is pushed solely as test evidence, not opened as an interface/implementation/tests-only feature PR. Optional row-projection optimization remains at original8518edd. The archive deliberately stays outside every feature diff.
