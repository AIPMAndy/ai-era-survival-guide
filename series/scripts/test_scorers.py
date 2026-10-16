from pathlib import Path
from score_common import read_csv, score
root=Path(__file__).resolve().parents[1]/"可直接填写的表格"
for ans,label,allowed,id_col in [
 ("24条评论_参考答案.csv","分类",{"质量","物流","价格","功能","其他"},"编号"),
 ("模拟财务对账_标准答案.csv","异常标签",{"重复发票号","缺少付款","金额不符","缺少发票"},"记录ID")]:
    truth=read_csv(root/ans)
    rows=[{id_col:x[id_col],label:x["参考标签"] if "参考标签" in x else x["异常标签"]} for x in truth]
    n,total,err=score(rows,truth,label,allowed,id_col)
    assert n==total and not err
    rows[0][label]="无效"
    n,total,err=score(rows,truth,label,allowed,id_col)
    assert n<total and err
print("PASS: baseline and bad label for two teaching datasets")
