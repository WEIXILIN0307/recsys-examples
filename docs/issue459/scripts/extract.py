import ast
from pathlib import Path
source=Path('/home/lwx/recsys-examples/corelib/dynamicemb')
def node(text,name,cls=None):
 tree=ast.parse(text);items=tree.body if cls is None else next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls).body
 return next(n for n in items if getattr(n,'name',None)==name)
def part(text,name,cls=None):
 n=node(text,name,cls);start=min([n.lineno]+[d.lineno for d in getattr(n,'decorator_list',[])]);return '\n'.join(text.splitlines()[start-1:n.end_lineno])+'\n'
def replace(text,name,new,cls=None):
 n=node(text,name,cls);start=min([n.lineno]+[d.lineno for d in getattr(n,'decorator_list',[])]);lines=text.splitlines(keepends=True);return ''.join(lines[:start-1])+new+''.join(lines[n.end_lineno:])
def final(path,name,cls=None):return part((source/path).read_text(),name,cls)
