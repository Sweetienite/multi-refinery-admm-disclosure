#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def get(obj,path):
 for key in path.split('.'):
  obj=obj[key]
 return obj

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--expected',required=True); ap.add_argument('--actual',required=True); ap.add_argument('--report',default='key_result_check.json'); ap.add_argument('--atol',type=float,default=1e-9)
 a=ap.parse_args(); exp=json.loads(Path(a.expected).read_text()); act=json.loads(Path(a.actual).read_text()); checks=[]
 fields=['standalone_total_CNY','centralized_total_CNY','coordination_value_CNY','admm_total_CNY','admm_iterations','objective_difference_CNY','positive_allocation_increment_kt','s391_increment_kt','s391_increment_share_percent']
 for f in fields:
  ev=exp[f]; av=act.get(f)
  ok=(av is not None and (ev==av if isinstance(ev,int) else math.isclose(float(ev),float(av),abs_tol=a.atol,rel_tol=0)))
  checks.append({'field':f,'expected':ev,'actual':av,'ok':ok})
 out={'status':'PASS' if all(c['ok'] for c in checks) else 'FAIL','checks':checks}
 Path(a.report).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out['status']); return 0 if out['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
