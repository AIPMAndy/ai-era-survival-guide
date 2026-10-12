#!/usr/bin/env python3
"""Offline deterministic evaluation of practice classifications. No networking, no deps."""
import csv,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'价格','履约','功能','其他','需人工复核'}
def read_csv(path):
 with open(path,encoding='utf-8-sig',newline='') as f:
  rows=csv.DictReader(f)
  if not {'id','category'}.issubset(rows.fieldnames or []):raise ValueError(f'{path}: expected columns id,category')
  result={}
  for line,row in enumerate(rows,2):
   idx=row.get('id','').strip()
   c=row.get('category','').strip()
   if not idx.isdigit():raise ValueError(f'{path}: row {line} invalid id')
   if idx in result:raise ValueError(f'{path}: duplicate id {idx}')
   if c not in ALLOWED:raise ValueError(f'{path}: row {line} invalid category: {c}')
   result[idx]=c
  return result
def grade(pred,gold):
 missing=sorted(set(gold)-set(pred),key=int)
 extra=sorted(set(pred)-set(gold),key=int)
 wrong=[(i,gold[i],pred[i]) for i in gold if i in pred and pred[i]!=gold[i]]
 correct=sum(1 for i in gold if i in pred and pred[i]==gold[i])
 return {'total':len(gold),'submitted':len(pred),'correct':correct,'accuracy':correct/len(gold) if gold else 0,'missing':missing,'extra':extra,'wrong':wrong}
def main():
 if len(sys.argv)!=2:
  print('Usage: python3 scripts/grade_feedback.py YOUR_PREDICTIONS.csv');sys.exit(2)
 gold=read_csv(ROOT/'labs/feedback-24-gold.csv');pred=read_csv(Path(sys.argv[1]));score=grade(pred,gold)
 print(f"正确 {score['correct']}/{score['total']}；总体准确率 {score['accuracy']:.1%}；漏行 {len(score['missing'])}；额外行 {len(score['extra'])}")
 for i,expected,actual in score['wrong']:print(f'{i}: 应为「{expected}」，填写「{actual}」')
 if score['missing']:print('漏行:',','.join(score['missing']))
 if score['extra']:print('多余行:',','.join(score['extra']))
 print('注：24 条均为人工编制的教学练习数据；分类包含预先定义的主观边界，不能当作模型实际业务准确率。')
if __name__=='__main__':main()
