#!/usr/bin/env python3
"""Offline scorer for exercises. Matches provided teaching answers; not a productivity benchmark."""
import csv, sys
from pathlib import Path
def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))
def score(pred, gold, label_col, allowed, id_col="编号"):
    problems=[]; seen={}; answers={}
    for row in pred:
        key=(row.get(id_col) or "").strip(); value=(row.get(label_col) or "").strip()
        if not key: problems.append("缺失编号"); continue
        if key in seen: problems.append("重复编号: "+key)
        if value not in allowed: problems.append("非法分类: "+key+" "+value)
        seen[key]=value
    for row in gold:
        answers[row[id_col]]=(row.get("参考标签") or row.get("异常标签") or "").strip()
    missing=sorted(set(answers)-set(seen)); extra=sorted(set(seen)-set(answers))
    if missing: problems.append("缺失: "+",".join(missing))
    if extra: problems.append("多出: "+",".join(extra))
    problems += [f"{k}: 参考 {v}, 实际 {seen.get(k)}" for k,v in answers.items() if k in seen and seen[k]!=v]
    count=sum(seen.get(k)==v for k,v in answers.items())
    return count,len(answers),problems
def main(mode):
    if len(sys.argv)!=2:
        print("用法：python3 check_"+mode+".py 输出结果.csv"); sys.exit(2)
    root=Path(__file__).resolve().parents[1]/"可直接填写的表格"
    if mode=="comments":
        answers=read_csv(root/"24条评论_参考答案.csv"); label="分类"; allowed={"质量","物流","价格","功能","其他"}; id_col="编号"
    else:
        answers=read_csv(root/"模拟财务对账_标准答案.csv"); label="异常标签"; allowed={"重复发票号","缺少付款","金额不符","缺少发票"}; id_col="记录ID"
    pred=read_csv(Path(sys.argv[1]))
    correct,total,problems=score(pred,answers,label,allowed,id_col)
    print(f"与教学参考答案一致：{correct}/{total} 条")
    for error in problems:print(" - "+error)
    sys.exit(1 if problems else 0)
