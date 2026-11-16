import ast,hashlib,json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];repo=R/'00-main';g=lambda *a:subprocess.check_output(['git',*a],cwd=repo,text=True);base='4466f9d2ea34fd74105f57e1d81291798cd23690';original='8518eddaf1ac3da2cca6070215b7841ddccfe2f9';rows=json.loads((R/'evidence/branches.json').read_text());mapping={r['path']:r['owners'] for r in json.loads((R/'evidence/change-mapping.json').read_text())}
def entities(ref,path):
 try:s=g('show',ref+':'+path)
 except subprocess.CalledProcessError:return []
 if not path.endswith('.py'):return []
 t=ast.parse(s);out=[]
 def walk(node,prefix=''):
  for n in ast.iter_child_nodes(node):
   if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):
    qual=prefix+n.name;out.append((n.lineno,n.end_lineno,qual));walk(n,qual+'.')
 walk(t);return out
catalog=[]
for path,owners in mapping.items():
 delta=g('diff','--no-ext-diff','--unified=0',base,original,'--',path);ents=entities(original,path);oldents=entities(base,path)
 for line in delta.splitlines():
  m=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)',line)
  if not m:continue
  line_no=int(m[3]);hits=sorted([x for x in ents if x[0]<=line_no<=x[1]],key=lambda x:x[1]-x[0]);name=hits[0][2] if hits else m[5].strip() or '<module/global or non-Python>'
  catalog.append(dict(path=path,original_hunk=line,entity=name,owners=owners,scope='Ownership inventory; shared-function changes have multiple functional owners, see manual invariants table.'))
(R/'evidence/original-hunk-catalog.json').write_text(json.dumps(catalog,indent=2)+'\n');print(len(catalog),'original hunks catalogued')
