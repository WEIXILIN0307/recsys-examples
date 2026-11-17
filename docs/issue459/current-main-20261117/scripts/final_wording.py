"""Polish outward prose without changing commands, URLs, or evidence data."""
import re
from pathlib import Path

R = Path(__file__).resolve().parents[1]
for p in (R / 'deliverables').glob('*.md'):
    parts = re.split(r'(```[\s\S]*?```|`[^`\n]+`|https?://[^\s)<>]+)', p.read_text())
    for i in range(0, len(parts), 2):
        s = parts[i]
        s = re.sub(r'\b(main|Current|current|Original|original|base|baseline|integrated|integration|merged|superseded|includes|reports|has|passed|cases|existing|plus|isolated|time|raw|Host|Hybrid|by|and|before|after|close)(?=\d)', r'\1 ', s)
        s = re.sub(r'\.(?=(459|548|551|557|558|563)\b)', '. ', s)
        s = re.sub(r'\b(merged|independent|includes|follows|review|before|with|by|close) (459|528|548|551|552|557|558|559|560|562|563)\b', r'\1 #\2', s, flags=re.I)
        s = s.replace('Issue459', 'Issue #459').replace('Issue 459', 'Issue #459')
        s = s.replace('64-bit', '64-bit').replace('state and64', 'state and 64')
        s = s.replace('step time11', 'step time 11').replace('loses0.25', 'loses 0.25')
        s = s.replace('the existing3', 'the existing 3').replace('plus8', 'plus 8')
        s = s.replace('native/JIT', 'native and JIT').replace('root pre-commit', 'root pre-commit')
        s = s.replace('Current-main2995', 'Current main 2995')
        s = s.replace('integration:NVIDIA', 'integration: NVIDIA')
        parts[i] = s
    p.write_text(''.join(parts))
print('Polished Markdown prose; structured evidence and source files unchanged.')
