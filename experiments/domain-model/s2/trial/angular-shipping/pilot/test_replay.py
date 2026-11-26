"""Offline table regressions using archived shipping grades."""
from contextlib import redirect_stdout
from io import StringIO
import unittest

from replay import OUT, load, print_tables


class SubmissionTableTest(unittest.TestCase):
    def render(self, control):
        grade = load(OUT.parent / '2026-11-26-shipping-grading-fix/results.json')['results'][control]
        output = StringIO()
        with redirect_stdout(output):
            print_tables([
                ('A', 'finished', ['충족', '충족'], grade['patchSha256'], grade),
                ('B', 'request-limit', ['미제출', '미제출'], None, None),
                ('C', 'request-limit', ['미제출', '미제출'], None, None),
            ], [], [])
        return grade, output.getvalue()

    def test_rejected_first_patch(self):
        grade, text = self.render('rejected')
        self.assertIn('최종 제출 1건 · 적용 거부 1건 · 사례 실행 0건', text)
        self.assertNotIn('최종 제출 0건', text)
        self.assertIn('| A | finished | 충족 | 충족 | 제출 | 적용 거부 | 0 | — | — | — |', text)
        for arm in 'BC':
            self.assertIn(f'| {arm} | request-limit | 미제출 | 미제출 | 미제출 | — | 0 |', text)
        self.assertIn('\n'.join('    ' + line for line in grade['reason'].splitlines()), text)

    def test_applied_patch_with_six_unexecuted_rows(self):
        grade, text = self.render('unobserved-service')
        self.assertEqual(len(grade['rows']), 6)
        self.assertIn('| 제출 | 적용 완료 | 0 | 0 | 0 | 6 |', text)
        self.assertIn('최종 제출 1건 · 적용 거부 0건 · 사례 실행 0건', text)

    def test_applied_patch_with_six_executed_cases(self):
        _, text = self.render('upstream')
        self.assertIn('| 제출 | 적용 완료 | 6 | 6 | 0 | 0 |', text)
        self.assertIn('최종 제출 1건 · 적용 거부 0건 · 사례 실행 6건', text)


if __name__ == '__main__':
    unittest.main()
