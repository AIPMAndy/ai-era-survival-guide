from pathlib import Path
import csv
r=Path(__file__).resolve().parent
comments=[
('这个价格比上周高了二十块，预算不够。','价格'),('结账页面的运费算错了。','履约'),('点保存以后页面一直转圈，没反应。','功能'),('客服回复挺快，但页面里找不到退货入口。','功能'),('昨天付的钱，今天看到有新人优惠券。','价格'),('包裹显示已送达，但门卫说没收到。','履约'),('搜索框输入中文以后结果为空。','功能'),('包装完好，使用没有问题。','其他'),('同样的规格，为什么不同颜色价钱不同？','价格'),('约好周二上门，周四还没联系。','履约'),('发票抬头输入后无法确认。','功能'),('做工和描述基本一致。','其他'),('退货物流三天没更新，希望确认进度。','履约'),('赠品比之前少了，宣传页也没说明。','价格'),('手机端每次登录都要求重新验证。','功能'),('客服态度很好，已经解决我的问题。','其他'),('首页写满减，购物车却没生效。','价格'),('预约安装的师傅没有按时间到。','履约'),('打开订单页出现白屏。','功能'),('我只想留下建议，颜色很好看。','其他'),('商品跟图差异有点大，但配送很准时。','其他'),('付款失败，还显示已扣款，请帮我确认。','需人工复核'),('这个收费贵不贵我说不清，先观望。','需人工复核'),('包装破了，东西没坏，想问能不能换。','需人工复核')
]
with (r/'feedback-24.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['id','comment']);w.writerows([(i+1,text) for i,(text,_) in enumerate(comments)])
with (r/'feedback-24-gold.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['id','category']);w.writerows([(i+1,label) for i,(_,label) in enumerate(comments)])
# Deliberately wrong example for demonstrating quality checks; cannot be marketed as AI model observed performance.
with (r/'sample-predictions-not-a-model-result.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['id','category'])
 for i,(_,gold) in enumerate(comments,1):w.writerow([i,'其他' if i in (2,6,11,22) else gold])
print('data generated',len(comments))
