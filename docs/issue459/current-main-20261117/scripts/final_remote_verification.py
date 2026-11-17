"""Read-only verification of published PRs and the public evidence archive."""
import concurrent.futures
import datetime
import hashlib
import json
import os
import subprocess
import urllib.request
from pathlib import Path

R = Path(__file__).resolve().parents[1]
E = R / 'evidence'
env = dict(os.environ, GH_CONFIG_DIR='/home/lwx/.cache/recsys-459-submit/gh-config')
gh = '/home/lwx/.cache/recsys-459-submit/gh'

def api(endpoint):
    return json.loads(subprocess.check_output([gh, 'api', endpoint], env=env, text=True))

def verify(row):
    repo = row['url'].split('github.com/')[1].split('/pull/')[0]
    number = row['url'].rsplit('/', 1)[1]
    endpoint = f'repos/{repo}/pulls/{number}'
    pr = api(endpoint)
    assert pr['state'] == 'open' and pr['draft']
    assert pr['head']['sha'] == row['head']
    body = (R / 'deliverables' / row['file']).read_text()
    assert pr['body'] == body
    assert hashlib.sha256(body.encode()).hexdigest() == row['body_sha256']
    source_repo = pr['head']['repo']['full_name']
    sha = pr['head']['sha']
    status = api(f'repos/{source_repo}/commits/{sha}/status')
    checks = api(f'repos/{source_repo}/commits/{sha}/check-runs?per_page=100')
    reviews = api(endpoint + '/reviews?per_page=100')
    comments = api(f'repos/{repo}/issues/{number}/comments?per_page=100')
    inline = api(endpoint + '/comments?per_page=100')
    result = dict(url=row['url'], head=sha, base=pr['base']['ref'], base_sha=pr['base']['sha'],
                  draft=pr['draft'], state=pr['state'], mergeable=pr['mergeable'],
                  mergeable_state=pr['mergeable_state'], additions=pr['additions'],
                  deletions=pr['deletions'], changed_files=pr['changed_files'],
                  body_sha256=row['body_sha256'], status=status, check_runs=checks,
                  reviews=reviews, comments=comments, inline_comments=inline)
    (E / f'final-remote-{repo.split("/")[0]}-{number}.json').write_text(json.dumps(result, indent=2)+'\n')
    return result

updates = json.loads((E / 'body-updates-current.json').read_text())
assert len(updates) == 13, 'Publication must finish before final verification.'
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    prs = list(pool.map(verify, [x for x in updates if x['head']]))
rfc = api('repos/NVIDIA/recsys-examples/issues/552')
assert rfc['state'] == 'open' and rfc['body'] == (R/'deliverables/rfc-552-rewritten.md').read_text()
main = api('repos/NVIDIA/recsys-examples/commits/main')['sha']
assert main == '2995c4148346cf62d0873d346be354382085228c', main

artifact = json.loads((E / 'artifact-current.json').read_text())
url = ('https://raw.githubusercontent.com/WEIXILIN0307/recsys-examples/' + artifact['head']
       + '/docs/issue459/current-main-20261117/evidence-current.tar.gz')
download = E/'public-evidence-current.download.tar.gz'
with urllib.request.urlopen(url, timeout=60) as response, download.open('wb') as out:
    while chunk := response.read(1024*1024):
        out.write(chunk)
actual = hashlib.sha256(download.read_bytes()).hexdigest()
assert actual == artifact['archive_sha256']
assert download.stat().st_size == artifact['archive_bytes']
archive_result = dict(url=url, sha256=actual, bytes=download.stat().st_size,
                      verified_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
(E/'public-artifact-verification.json').write_text(json.dumps(archive_result,indent=2)+'\n')
summary = dict(verified_at=archive_result['verified_at'], upstream_main=main,
              rfc_body_matches=True, archive=archive_result, prs=[dict(
                  url=p['url'], head=p['head'], base=p['base'], base_sha=p['base_sha'],
                  draft=p['draft'], mergeable=p['mergeable'], mergeable_state=p['mergeable_state'],
                  status_state=p['status']['state'], statuses=p['status']['statuses'],
                  check_runs=p['check_runs']['check_runs'], review_count=len(p['reviews']),
                  comment_count=len(p['comments']), inline_comment_count=len(p['inline_comments'])
              ) for p in prs])
(E/'final-remote-verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
