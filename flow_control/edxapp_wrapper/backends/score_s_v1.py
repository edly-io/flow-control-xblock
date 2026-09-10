"""
Score module definitions for Open edX Sumac release.
"""
# pylint: disable=import-error
from collections import namedtuple

from django.contrib.auth import get_user_model
from lms.djangoapps.grades.api import CourseGradeFactory

Score = namedtuple('Score', ['correct', 'total'])


class GradesApiScoresClient:
    """
    Scores client backed by the Grades subsystem (CourseGradeFactory).

    This works uniformly for any graded block type (capa problems, ORA,
    etc), unlike the legacy courseware_studentmodule table, which ORA no
    longer publishes scores to.
    """

    def __init__(self, course_id, user_id):
        self.course_id = course_id
        self.user_id = user_id
        self._course_grade = None

    def fetch_scores(self, usage_keys):  # pylint: disable=unused-argument
        """Pre-load the course grade for this user."""
        user = get_user_model().objects.get(id=self.user_id)
        self._course_grade = CourseGradeFactory().read(user, course_key=self.course_id)

    def get(self, usage_key):
        """
        Return the Score for the given usage key, or None if the block
        has not been attempted yet.
        """
        problem_score = self._course_grade.problem_scores.get(usage_key)
        if problem_score is None or problem_score.first_attempted is None:
            return None
        return Score(correct=problem_score.earned, total=problem_score.possible)


def get_score_module(*args, **kwargs):
    """
    Get a scores client backed by the Grades subsystem.

    Returns:
        GradesApiScoresClient: scores client object.
    """
    return GradesApiScoresClient(*args, **kwargs)
