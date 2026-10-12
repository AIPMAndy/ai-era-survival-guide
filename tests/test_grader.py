import importlib.util,tempfile,unittest,csv
from pathlib import Path
P=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('grade_feedback',P/'scripts/grade_feedback.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def setUp(self):self.gold=m.read_csv(P/'labs/feedback-24-gold.csv')
 def test_size_and_labels(self):self.assertEqual(len(self.gold),24);self.assertTrue(set(self.gold.values()).issubset(m.ALLOWED))
 def test_deliberate_errors(self):
  p=m.read_csv(P/'labs/sample-predictions-not-a-model-result.csv');r=m.grade(p,self.gold)
  self.assertEqual(r['correct'],20);self.assertEqual(len(r['wrong']),4);self.assertEqual(r['missing'],[])
 def test_missing_and_extra(self):
  p=dict(self.gold);p.pop('1');p['999']='其他';r=m.grade(p,self.gold)
  self.assertEqual(r['correct'],23);self.assertEqual(r['missing'],['1']);self.assertEqual(r['extra'],['999'])
 def test_duplicate_and_wrong_label_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'a.csv';p.write_text('id,category\n1,其他\n1,价格\n',encoding='utf-8')
   with self.assertRaisesRegex(ValueError,'duplicate'):m.read_csv(p)
   p.write_text('id,category\n1,百分百放心\n',encoding='utf-8')
   with self.assertRaisesRegex(ValueError,'invalid category'):m.read_csv(p)
if __name__=='__main__':unittest.main()
