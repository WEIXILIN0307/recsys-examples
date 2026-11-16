#!/usr/bin/env bash
set -euo pipefail
# Existing Drafts are already published. Do not run pr create blindly.
# After prerequisites merge and latest-main tests pass, publish NEW replacement branches.
# Example for a future upstream HBM proposal:
# git push fork HEAD:refs/heads/fea-459-hbm-rw-receiver-current-main
# gh pr create --repo NVIDIA/recsys-examples --base main --head WEIXILIN0307:fea-459-hbm-rw-receiver-current-main --draft --title "[FEA] Resolve HBM RW sequence rows at receiver completion" --body-file pr-03-hbm.md
# Current previews and parent branches are listed in published-stack.json.
# Published bug-459-row-lifetime at ee3618ea47a3348cb0b63136bd6943c925ff6f3e
# Published enh-459-lookup-adapter at 9a1d450fffce83021ecbbeccc2620870abf7d741
# Published fea-459-hbm-rw-receiver at 94fd32f5618f7888606970f55b8ca1b04c27a293
# Published fea-459-cache-receiver at de9225bd5decc1493bf70627d3e79a10bce7b8e8
# Published fea-459-storage-receiver at d9d793e9e3aca328c07c54926a90c75313efb181
# Published fea-459-pooled-receiver at c678535a5a9082a345799c0303f0d204a58ff6c1
# Published fea-459-twrw-receiver at 6496114eb5c6e1829b736c5b82e5498094dcd50d
# Published fea-459-hier-receiver at 6bef728fc51dc8c6ddc7d26afff5b40e8d5889a1
