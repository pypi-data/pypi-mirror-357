import re

import numpy as np
import pytest
import test_aide as ta

import tests.test_data as d
from tests.base_tests import (
    ColumnStrListInitTests,
    DropOriginalInitMixinTests,
    GenericFitTests,
    GenericTransformTests,
    OtherBaseBehaviourTests,
)
from tests.dates.test_BaseDatetimeTransformer import DatetimeMixinTransformTests
from tubular.dates import DatetimeSinusoidCalculator


@pytest.fixture(scope="module", autouse=True)
def example_transformer():
    return DatetimeSinusoidCalculator("a", "cos", "hour", 24)


class TestInit(
    ColumnStrListInitTests,
    DropOriginalInitMixinTests,
):
    """Tests for DatetimeSinusoidCalculator.init()."""

    @classmethod
    def setup_class(cls):
        cls.transformer_name = "DatetimeSinusoidCalculator"

    @pytest.mark.parametrize("incorrect_type_method", [2, 2.0, True, {"a": 4}])
    def test_method_type_error(self, incorrect_type_method):
        """Test that an exception is raised if method is not a str or a list."""
        with pytest.raises(
            TypeError,
            match="method must be a string or list but got {}".format(
                type(incorrect_type_method),
            ),
        ):
            DatetimeSinusoidCalculator(
                "a",
                incorrect_type_method,
                "hour",
                24,
            )

    @pytest.mark.parametrize("incorrect_type_units", [2, 2.0, True, ["help"]])
    def test_units_type_error(self, incorrect_type_units):
        """Test that an exception is raised if units is not a str or a dict."""
        with pytest.raises(
            TypeError,
            match=f"units must be a string or dict but got {type(incorrect_type_units)}",
        ):
            DatetimeSinusoidCalculator(
                "a",
                "cos",
                incorrect_type_units,
                24,
            )

    @pytest.mark.parametrize("incorrect_type_period", ["2", True, ["help"]])
    def test_period_type_error(self, incorrect_type_period):
        """Test that an error is raised if period is not an int or a float or a dictionary."""
        with pytest.raises(
            TypeError,
            match="period must be an int, float or dict but got {}".format(
                type(incorrect_type_period),
            ),
        ):
            DatetimeSinusoidCalculator(
                "a",
                "cos",
                "hour",
                incorrect_type_period,
            )

    @pytest.mark.parametrize(
        "incorrect_dict_types_period",
        [{"str": True}, {2: "str"}, {2: 2}, {"str": ["str"]}],
    )
    def test_period_dict_type_error(self, incorrect_dict_types_period):
        """Test that an error is raised if period dict is not a str:int or str:float kv pair."""
        with pytest.raises(
            TypeError,
            match="period dictionary key value pair must be str:int or str:float but got keys: {} and values: {}".format(
                {type(k) for k in incorrect_dict_types_period},
                {type(v) for v in incorrect_dict_types_period.values()},
            ),
        ):
            DatetimeSinusoidCalculator(
                "a",
                "cos",
                "hour",
                incorrect_dict_types_period,
            )

    @pytest.mark.parametrize(
        "incorrect_dict_types_units",
        [
            {"str": True},
            {2: "str"},
            {"str": 2},
            {2: 2},
            {"str": True},
            {"str": ["str"]},
        ],
    )
    def test_units_dict_type_error(self, incorrect_dict_types_units):
        """Test that an error is raised if units dict is not a str:str kv pair."""
        with pytest.raises(
            TypeError,
            match="units dictionary key value pair must be strings but got keys: {} and values: {}".format(
                {type(k) for k in incorrect_dict_types_units},
                {type(v) for v in incorrect_dict_types_units.values()},
            ),
        ):
            DatetimeSinusoidCalculator(
                "a",
                "cos",
                incorrect_dict_types_units,
                24,
            )

    @pytest.mark.parametrize("incorrect_dict_units", [{"str": "tweet"}])
    def test_units_dict_value_error(self, incorrect_dict_units):
        """Test that an error is raised if units dict value is not from the valid units list."""
        with pytest.raises(
            ValueError,
            match="units dictionary values must be one of 'year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond' but got {}".format(
                set(incorrect_dict_units.values()),
            ),
        ):
            DatetimeSinusoidCalculator(
                "a",
                "cos",
                incorrect_dict_units,
                24,
            )

    @pytest.mark.parametrize(
        "incorrect_dict_columns_period",
        [{"ham": 24}, {"str": 34.0}],
    )
    def test_period_dict_col_error(self, incorrect_dict_columns_period):
        """Test that an error is raised if period dict keys are not equal to columns."""
        with pytest.raises(
            ValueError,
            match="period dictionary keys must be the same as columns but got {}".format(
                set(incorrect_dict_columns_period.keys()),
            ),
        ):
            DatetimeSinusoidCalculator(
                ["vegan_sausages", "carrots", "peas"],
                "cos",
                "hour",
                incorrect_dict_columns_period,
            )

    @pytest.mark.parametrize(
        "incorrect_dict_columns_unit",
        [{"sausage_roll": "hour"}],
    )
    def test_unit_dict_col_error(self, incorrect_dict_columns_unit):
        """Test that an error is raised if unit dict keys is not equal to columns."""
        with pytest.raises(
            ValueError,
            match="unit dictionary keys must be the same as columns but got {}".format(
                set(incorrect_dict_columns_unit.keys()),
            ),
        ):
            DatetimeSinusoidCalculator(
                ["vegan_sausages", "carrots", "peas"],
                "cos",
                incorrect_dict_columns_unit,
                6,
            )

    def test_valid_method_value_error(self):
        """Test that a value error is raised if method is not sin, cos or a list containing both."""
        method = "tan"

        with pytest.raises(
            ValueError,
            match=f'Invalid method {method} supplied, should be "sin", "cos" or a list containing both',
        ):
            DatetimeSinusoidCalculator(
                "a",
                method,
                "year",
                24,
            )

    def test_valid_units_value_error(self):
        """Test that a value error is raised if the unit supplied is not in the valid units list."""
        units = "five"
        valid_unit_list = [
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
            "microsecond",
        ]

        with pytest.raises(
            ValueError,
            match=re.escape(
                f"Invalid units {units} supplied, should be in {valid_unit_list}",
            ),
        ):
            DatetimeSinusoidCalculator(
                "a",
                "cos",
                units,
                24,
            )


class TestFit(GenericFitTests):
    """Generic tests for transformer.fit()"""

    @classmethod
    def setup_class(cls):
        cls.transformer_name = "DatetimeSinusoidCalculator"


class TestTransform(GenericTransformTests, DatetimeMixinTransformTests):
    """Tests for BaseTwoColumnDateTransformer.transform."""

    @classmethod
    def setup_class(cls):
        cls.transformer_name = "DatetimeSinusoidCalculator"

    @pytest.mark.parametrize(
        "transformer",
        [
            DatetimeSinusoidCalculator(
                "a",
                "cos",
                "month",
                12,
            ),
            DatetimeSinusoidCalculator(
                [
                    "a",
                    "b",
                ],
                "cos",
                "month",
                12,
            ),
        ],
    )
    def test_expected_output_single_method(self, transformer):
        expected = d.create_datediff_test_df()
        for column in transformer.columns:
            column_in_desired_unit = expected[column].dt.month
            cos_argument = column_in_desired_unit * (2.0 * np.pi / 12)
            new_col_name = "cos_12_month_" + column
            expected[new_col_name] = cos_argument.apply(np.cos)

        x = transformer
        actual = x.transform(d.create_datediff_test_df())
        ta.equality.assert_frame_equal_msg(
            actual=actual,
            expected=expected,
            msg_tag="DatetimeSinusoidCalculator transformer does not produce the expected output",
        )

    def test_expected_output_both_methods(self):
        expected = d.create_datediff_test_df()
        columns = ["a", "b"]
        transformer = DatetimeSinusoidCalculator(
            method=["sin", "cos"],
            units="month",
            period=12,
            columns=columns,
        )

        for column in transformer.columns:
            column_in_desired_unit = expected[column].dt.month
            method_ready_column = column_in_desired_unit * (2.0 * np.pi / 12)
            new_cos_col_name = "cos_12_month_" + column
            new_sin_col_name = "sin_12_month_" + column
            expected[new_sin_col_name] = method_ready_column.apply(np.sin)
            expected[new_cos_col_name] = method_ready_column.apply(np.cos)

        df = d.create_datediff_test_df()
        actual = transformer.transform(df)
        ta.equality.assert_frame_equal_msg(
            actual=actual,
            expected=expected,
            msg_tag="DatetimeSinusoidCalculator transformer does not produce the expected output",
        )

    def test_expected_output_dict_units(self):
        expected = d.create_datediff_test_df()
        columns = ["a", "b"]
        transformer = DatetimeSinusoidCalculator(
            columns=columns,
            method=["sin"],
            units={"a": "month", "b": "day"},
            period=12,
        )

        a_in_desired_unit = expected["a"].dt.month
        b_in_desired_unit = expected["b"].dt.day
        a_method_ready_column = a_in_desired_unit * (2.0 * np.pi / 12)
        b_method_ready_column = b_in_desired_unit * (2.0 * np.pi / 12)
        a_col_name = "sin_12_month_a"
        b_col_name = "sin_12_day_b"
        expected[a_col_name] = a_method_ready_column.apply(np.sin)
        expected[b_col_name] = b_method_ready_column.apply(np.sin)
        df = d.create_datediff_test_df()
        actual = transformer.transform(df)
        ta.equality.assert_frame_equal_msg(
            actual=actual,
            expected=expected,
            msg_tag="DatetimeSinusoidCalculator transformer does not produce the expected output",
        )

    def test_expected_output_dict_period(self):
        expected = d.create_datediff_test_df()

        transformer = DatetimeSinusoidCalculator(
            columns=[
                "a",
                "b",
            ],
            method=["sin"],
            units="month",
            period={"a": 12, "b": 24},
        )

        a_in_desired_unit = expected["a"].dt.month
        b_in_desired_unit = expected["b"].dt.month
        a_method_ready_column = a_in_desired_unit * (2.0 * np.pi / 12)
        b_method_ready_column = b_in_desired_unit * (2.0 * np.pi / 24)
        a_col_name = "sin_12_month_a"
        b_col_name = "sin_24_month_b"
        expected[a_col_name] = a_method_ready_column.apply(np.sin)
        expected[b_col_name] = b_method_ready_column.apply(np.sin)

        actual = transformer.transform(d.create_datediff_test_df())
        ta.equality.assert_frame_equal_msg(
            actual=actual,
            expected=expected,
            msg_tag="DatetimeSinusoidCalculator transformer does not produce the expected output",
        )

    def test_expected_output_dict_both(self):
        expected = d.create_datediff_test_df()
        columns = ["a", "b"]
        transformer = DatetimeSinusoidCalculator(
            columns=columns,
            method=["sin"],
            units={"a": "month", "b": "day"},
            period={"a": 12, "b": 24},
        )

        a_in_desired_unit = expected["a"].dt.month
        b_in_desired_unit = expected["b"].dt.day
        a_method_ready_column = a_in_desired_unit * (2.0 * np.pi / 12)
        b_method_ready_column = b_in_desired_unit * (2.0 * np.pi / 24)
        a_col_name = "sin_12_month_a"
        b_col_name = "sin_24_day_b"
        expected[a_col_name] = a_method_ready_column.apply(np.sin)
        expected[b_col_name] = b_method_ready_column.apply(np.sin)
        df = d.create_datediff_test_df()

        actual = transformer.transform(df)
        ta.equality.assert_frame_equal_msg(
            actual=actual,
            expected=expected,
            msg_tag="DatetimeSinusoidCalculator transformer does not produce the expected output",
        )


class TestOtherBaseBehaviour(OtherBaseBehaviourTests):
    """
    Class to run tests for BaseTransformerBehaviour outside the three standard methods.

    May need to overwite specific tests in this class if the tested transformer modifies this behaviour.
    """

    @classmethod
    def setup_class(cls):
        cls.transformer_name = "DatetimeSinusoidCalculator"
