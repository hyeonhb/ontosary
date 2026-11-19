import unittest
from holdout import summarize


def attempt(arm, passed, tokens, repeat=1, status=None):
    return {'task':'fixture','repeat':repeat,'condition':arm,'status':status or ('passed' if passed else 'behavior-failed'),
            'success':passed,'elapsedSeconds':2,'usage':None if tokens is None else
            {'input_tokens':tokens,'output_tokens':4,'cached_input_tokens':5,'reasoning_output_tokens':2}}


class CostContract(unittest.TestCase):
    def test_counts_failures_and_divides_only_positive_gains(self):
        rows=[attempt('A',False,20),attempt('B',True,30),attempt('C',False,22),
              attempt('A',True,18,2),attempt('B',True,27,2),attempt('C',False,21,2)]
        report=summarize(rows)
        self.assertEqual(report['allScheduled']['A']['input_tokens']['total'],38)
        self.assertEqual(report['allScheduled']['A']['output_tokens']['total'],8)
        self.assertEqual(report['effects']['B-A']['input_tokens']['perAdditionalSuccess'],19)
        self.assertIsNone(report['effects']['C-A']['input_tokens']['perAdditionalSuccess'])
        self.assertEqual(report['pairedFirstSubmissions']['fixture/2']['A'],'passed')

    def test_same_success_count_and_missing_usage(self):
        report=summarize([attempt('A',True,20),attempt('B',True,31),attempt('C',False,None)])
        self.assertEqual(report['effects']['B-A']['additionalSuccesses'],0)
        self.assertIsNone(report['effects']['B-A']['output_tokens']['perAdditionalSuccess'])
        self.assertIsNone(report['allScheduled']['C']['input_tokens']['total'])
        self.assertIsNone(report['effects']['C-A']['input_tokens']['difference'])

    def test_infrastructure_retains_denominator_but_withholds_ratio(self):
        report=summarize([attempt('A',False,20,status='infrastructure-error'),attempt('B',True,30),attempt('C',True,29)])
        self.assertEqual(report['allScheduled']['A']['scheduled'],1)
        self.assertFalse(report['effects']['B-A']['comparable'])
        self.assertIsNone(report['effects']['B-A']['input_tokens']['perAdditionalSuccess'])


if __name__=='__main__':
    unittest.main()
