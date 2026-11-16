from pathlib import Path
import subprocess,shutil
R=Path(__file__).resolve().parents[1]
for name in ['04-cache','05-storage']:
 p=R/name/'corelib/dynamicemb/test/unit_tests/test_cache_receiver.py';s=p.read_text().replace('import torch\n','import torch\nimport torch.distributed as dist\n');p.write_text(s)
p=R/'05-storage/corelib/dynamicemb/test/unit_tests/test_storage_receiver.py';s=p.read_text().replace('import gc\n','import gc\nfrom unittest.mock import patch\n').replace('import torch\n','import torch\nimport torch.distributed as dist\nfrom dynamicemb.shard.resolved_input import ResolvedEmbeddingInput\nfrom dynamicemb.types import CopyMode\n');p.write_text(s)
for name in ['04-cache','05-storage']:
 w=R/name;fs=[str(p.relative_to(w)) for p in (w/'corelib/dynamicemb/test/unit_tests').glob('test_*receiver.py') if p.name!='test_hbm_receiver.py']
 for tool,args in [('isort',['--profile','black']),('black',[])]:subprocess.run(['/home/lwx/.cache/recsys-459-venv/bin/'+tool,*args,*fs],cwd=w,check=True)
 # Only undefined names are errors here; imported pytest fixtures are intentional.
 out=subprocess.run(['/home/lwx/.cache/recsys-459-venv/bin/python','-m','pyflakes',*fs],cwd=w,text=True,capture_output=True);assert 'undefined name' not in out.stdout,out.stdout
old_to_new={};parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R/'03-hbm',text=True).strip()
for name in ['04-cache','05-storage']:
 w=R/name;g=lambda *a:subprocess.check_output(['git',*a],cwd=w,text=True).strip();old=g('rev-parse','HEAD');g('branch','reference/'+name+'-initial-corpus',old);msg=g('show','-s','--format=%B',old);p=R/'evidence'/(name+'-message.txt');p.write_text(msg+'\n');g('add','-A');tree=g('write-tree');new=g('-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit-tree',tree,'-p',parent,'-F',str(p));g('update-ref',g('symbolic-ref','HEAD'),new,old);print(name,new);parent=new
