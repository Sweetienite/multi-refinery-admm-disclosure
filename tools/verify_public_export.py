#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path
HIGH_PATH_PATTERNS=[
 'raw_private_trace','private_trace','frozen_evidence','local_reproductions','FORENSIC',
 '.env','id_rsa','id_ed25519','credentials','secret','token'
]
FORBIDDEN_SUFFIX={'.docx','.doc','.xls','.xlsx','.ppt','.pptx','.key','.pem','.p12'}
CONTENT_PATTERNS={
 'absolute_user_path': re.compile(r'(/Users/[^\s"\']+|/home/[^\s"\']+|[A-Za-z]:\\Users\\[^\s"\']+)'),
 'github_token': re.compile(r'gh[pousr]_[A-Za-z0-9_]{20,}'),
 'aws_key': re.compile(r'AKIA[0-9A-Z]{16}'),
 'private_key': re.compile(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----'),
 'old_authority_branch': re.compile(r'rebuild/missing-evidence-20260715'),
}
TEXT_SUFFIX={'.md','.txt','.rst','.yaml','.yml','.json','.toml','.ini','.py','.sh','.csv','.cff'}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--strict',action='store_true'); ap.add_argument('--scan-existing',action='store_true'); ap.add_argument('--report',default='public_export_scan.json')
 a=ap.parse_args(); root=Path(a.root).resolve(); findings=[]
 for p in root.rglob('*'):
  if not p.is_file() or '.git' in p.parts: continue
  rel=p.relative_to(root).as_posix()
  lower=rel.lower()
  for q in HIGH_PATH_PATTERNS:
   if q.lower() in lower: findings.append({'severity':'HIGH','type':'path','pattern':q,'path':rel})
  if p.suffix.lower() in FORBIDDEN_SUFFIX: findings.append({'severity':'HIGH','type':'suffix','pattern':p.suffix.lower(),'path':rel})
  # The scanner contains detection regexes (including absolute-path examples);
  # do not report those implementation literals as repository leaks.
  if p.resolve() == Path(__file__).resolve():
   continue
  if p.suffix.lower() in TEXT_SUFFIX and p.stat().st_size < 20*1024*1024:
   try:text=p.read_text(encoding='utf-8',errors='replace')
   except OSError:continue
   for name,pat in CONTENT_PATTERNS.items():
    for m in pat.finditer(text):
     sev='HIGH' if name in {'github_token','aws_key','private_key','absolute_user_path'} else 'WARN'
     findings.append({'severity':sev,'type':'content','pattern':name,'path':rel,'line':text.count('\n',0,m.start())+1})
 report={'root':str(root),'high_count':sum(x['severity']=='HIGH' for x in findings),'warn_count':sum(x['severity']=='WARN' for x in findings),'findings':findings}
 Path(a.report).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'high_count':report['high_count'],'warn_count':report['warn_count'],'report':a.report},ensure_ascii=False))
 return 1 if a.strict and report['high_count'] else 0
if __name__=='__main__': raise SystemExit(main())
