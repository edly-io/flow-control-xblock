"""
Unit tests for flow-control
"""

import ddt
import unittest

from mock import MagicMock, patch, mock_open
# from xblock.core import XBlock
from xblock.field_data import DictFieldData
from flow_control.flow import FlowCheckPointXblock
from flow_control.flow import (_actions_generator, _conditions_generator,
                               _operators_generator, load)


@ddt.ddt
class TestBuilderBlocks(unittest.TestCase):
    """ Unit tests for flow-control """

    def setUp(self):
        """
        Set up a instance of FlowCheckPointXblock for testing
        """
        self.runtime_mock = MagicMock()
        scope_ids_mock = MagicMock()
        scope_ids_mock.usage_id = u'0'
        self.block = FlowCheckPointXblock(
            self.runtime_mock,
            field_data=DictFieldData({}),
            scope_ids=scope_ids_mock)

    def test_actions_generator(self):
        """
        It should return a list with allowed actions
        """
        actions_allowed = _actions_generator(self.block)
        actions = [
            {"display_name": "Display a message",
             "value": "display_message"},
            {"display_name": "Redirect using jump_to_id",
             "value": "to_jump"},
            {"display_name": "Redirect to a given URL",
             "value": "to_url"}
        ]
        self.assertEqual(actions, actions_allowed)

    def test_conditions_generator(self):
        """
        It should return a list with allowed conditions
        """
        conditions_allowed = _conditions_generator(self.block)
        conditions = [
            {"display_name": "Grade of a problem",
             "value": "single_problem"},
            {"display_name": "Average grade of a list of problems",
             "value": "average_problems"}
        ]
        self.assertEqual(conditions, conditions_allowed)

    def test_operators_generator(self):
        """
        It should return list with allowed operators
        """
        operators_allowed = _operators_generator(self.block)
        operators = [
            {"display_name": "equal to",
             "value": "eq"},
            {"display_name": "not equal to",
             "value": "noeq"},
            {"display_name": "less than or equal to",
             "value": "lte"},
            {"display_name": "less than",
             "value": "lt"},
            {"display_name": "greater than or equal to",
             "value": "gte"},
            {"display_name": "greater than",
             "value": "gt"},
            {"display_name": "none of the problems have been answered",
             "value": "all_null"},
            {"display_name": "all problems have been answered",
                "value": "all_not_null"},
            {"display_name": "some problem has not been answered",
                "value": "has_null"}
        ]
        self.assertEqual(operators, operators_allowed)

    def test_load(self):
        """It should return the corresponding resource"""
        path_mock = "test_resource.txt"
        mock_content = "mocked content"

        with patch("pathlib.Path.open", mock_open(read_data=mock_content)):
            result = load(path_mock)
            self.assertEqual(result, mock_content)

    @patch('flow_control.flow.get_modulestore')
    def test_get_usage_key_for_block_id(self, get_modulestore_mock):
        """
        It should return the usage key for a block given its bare id,
        regardless of the block's category (e.g. problem, openassessment).
        """

        # prepare
        block_id = 'hbdf3883be0935'
        self.block.course_id = MagicMock()
        found_item = MagicMock()
        get_modulestore_mock.return_value.get_items.return_value = [found_item]

        # execute code
        result = self.block.get_usage_key_for_block_id(block_id)

        # asserts
        get_modulestore_mock.return_value.get_items.assert_called_with(
            self.block.course_id, qualifiers={'name': block_id})
        self.assertEqual(found_item.location, result)

    @patch('flow_control.flow.get_modulestore')
    def test_get_usage_key_for_block_id_not_found(self, get_modulestore_mock):
        """
        It should return None when no block matches the given id.
        """

        # prepare
        self.block.course_id = MagicMock()
        get_modulestore_mock.return_value.get_items.return_value = []

        # execute code
        result = self.block.get_usage_key_for_block_id('missing-id')

        # asserts
        self.assertIsNone(result)

    def test_get_condition_status(self):
        """
        It should return the actual condition status
        """

        # prepare
        self.block.condition = 'single_problem'
        self.block.condition_on_problem_list = MagicMock()
        self.block.problem_id = '    ndsjkjhgs78768346  '
        self.block.list_of_problems = 'ndsjkjhg8768346fd  njhgs78ikdgshuhg46  '
        problems = self.block.problem_id.split()
        # execute code
        self.block.get_condition_status()

        # asserts
        self.block.condition_on_problem_list.assert_called_with((problems))

        # prepare for a different condifiton
        self.block.condition = 'average_problems'

        # execute code
        self.block.get_condition_status()

        # asserts
        problems = self.block.list_of_problems.split()
        self.block.condition_on_problem_list.assert_called_with((problems))

    @patch('flow_control.flow.Fragment')
    def test_student_view(self, fragment_mock):
        """
        It should return the student view
        """

        # prepare
        fragment_instance = MagicMock()
        fragment_mock.return_value = fragment_instance
        self.block.xmodule_runtime = MagicMock()
        # execute code
        self.block.student_view(context=None)

        # asserts
        fragment_mock.assert_called()
        fragment_instance.add_javascript.assert_called()
        fragment_instance.initialize_js.assert_called()

    @patch('flow_control.flow.Fragment')
    def test_author_view(self, fragment_mock):
        """
        It should return the author view
        """

        # prepare
        fragment_instance = MagicMock()
        fragment_mock.return_value = fragment_instance

        # execute code
        self.block.author_view(context=None)

        # asserts
        fragment_mock.assert_called()
        fragment_instance.add_javascript.assert_called()
        fragment_instance.initialize_js.assert_called()

    def test_has_null(self):
        """
        Test the conditions of which it passes the has_null check
        Description: some problem has not been answered
        """
        self.assertFalse(self.block.has_null([1.0]))
        self.assertFalse(self.block.has_null([1.0, 1.0]))
        self.assertFalse(self.block.has_null([1.0, 1.0, 1.0]))
        self.assertFalse(self.block.has_null([1.0, 0.0]))
        self.assertFalse(self.block.has_null([0.0]))

        self.assertTrue(self.block.has_null([1.0, None]))
        self.assertTrue(self.block.has_null([0.0, None]))
        self.assertTrue(self.block.has_null([None]))
        self.assertTrue(self.block.has_null([None, None]))
        self.assertTrue(self.block.has_null([]))

    def test_are_all_null(self):
        """
        Test the conditions of which it passes the are_all_null check
        Description: none of the problems have been answered
        """
        self.assertFalse(self.block.are_all_null([1.0]))
        self.assertFalse(self.block.are_all_null([1.0, 1.0]))
        self.assertFalse(self.block.are_all_null([1.0, 1.0, 1.0]))
        self.assertFalse(self.block.are_all_null([1.0, 0.0]))
        self.assertFalse(self.block.are_all_null([1.0, None]))
        self.assertFalse(self.block.are_all_null([0.0]))
        self.assertFalse(self.block.are_all_null([0.0, None]))

        self.assertTrue(self.block.are_all_null([None]))
        self.assertTrue(self.block.are_all_null([None, None]))
        self.assertTrue(self.block.are_all_null([]))

    def test_are_all_not_null(self):
        """
        Test the conditions of which it passes the are_all_not_null check
        Description: all problems have been answered
        """
        self.assertFalse(self.block.are_all_not_null([1.0, None]))
        self.assertFalse(self.block.are_all_not_null([None, None]))
        self.assertFalse(self.block.are_all_not_null([None]))
        self.assertFalse(self.block.are_all_not_null([0.0, None]))
        self.assertFalse(self.block.are_all_not_null([]))

        self.assertTrue(self.block.are_all_not_null([1.0]))
        self.assertTrue(self.block.are_all_not_null([1.0, 1.0]))
        self.assertTrue(self.block.are_all_not_null([1.0, 1.0, 1.0]))
        self.assertTrue(self.block.are_all_not_null([1.0, 0.0]))
        self.assertTrue(self.block.are_all_not_null([0.0]))
