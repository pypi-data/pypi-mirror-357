"""
Test cases for the DataFrame profiler.
"""

import pytest

from pyspark_analyzer import analyze
from pyspark_analyzer.statistics import StatisticsComputer
from pyspark_analyzer.utils import format_profile_output


class TestAnalyzeFunction:
    """Test cases for analyze function."""

    def test_analyze_with_invalid_input(self):
        """Test analyze function with invalid input."""
        from pyspark_analyzer import DataTypeError

        with pytest.raises(DataTypeError):
            analyze("not_a_dataframe")

    def test_profile_all_columns(self, sample_dataframe):
        """Test profiling all columns."""
        profile = analyze(sample_dataframe, output_format="dict")

        assert "overview" in profile
        assert "columns" in profile
        assert len(profile["columns"]) == 4  # id, name, age, salary

        # Check overview
        overview = profile["overview"]
        assert overview["total_rows"] == 5
        assert overview["total_columns"] == 4

        # Check column profiles exist
        assert "id" in profile["columns"]
        assert "name" in profile["columns"]
        assert "age" in profile["columns"]
        assert "salary" in profile["columns"]

    def test_profile_specific_columns(self, sample_dataframe):
        """Test profiling specific columns."""
        profile = analyze(
            sample_dataframe, columns=["id", "name"], output_format="dict"
        )

        assert len(profile["columns"]) == 2
        assert "id" in profile["columns"]
        assert "name" in profile["columns"]
        assert "age" not in profile["columns"]
        assert "salary" not in profile["columns"]

    def test_profile_invalid_columns(self, sample_dataframe):
        """Test profiling with invalid column names."""
        from pyspark_analyzer import ColumnNotFoundError

        with pytest.raises(ColumnNotFoundError, match="Columns not found"):
            analyze(
                sample_dataframe, columns=["nonexistent_column"], output_format="dict"
            )

    def test_numeric_column_stats(self, sample_dataframe):
        """Test statistics for numeric columns."""
        profile = analyze(
            sample_dataframe, columns=["id", "salary"], output_format="dict"
        )

        # Check numeric stats for 'id' column
        id_stats = profile["columns"]["id"]
        assert "min" in id_stats
        assert "max" in id_stats
        assert "mean" in id_stats
        assert "std" in id_stats
        assert "median" in id_stats

        # Check numeric stats for 'salary' column
        salary_stats = profile["columns"]["salary"]
        assert "min" in salary_stats
        assert "max" in salary_stats
        assert salary_stats["null_count"] == 0  # No nulls in sample data

    def test_string_column_stats(self, sample_dataframe):
        """Test statistics for string columns."""
        profile = analyze(sample_dataframe, columns=["name"], output_format="dict")

        name_stats = profile["columns"]["name"]
        assert "min_length" in name_stats
        assert "max_length" in name_stats
        assert "avg_length" in name_stats
        assert "empty_count" in name_stats
        assert name_stats["empty_count"] == 0  # No empty strings in sample data


class TestStatisticsComputer:
    """Test cases for StatisticsComputer class."""

    def test_statistics_computer_integration(self, sample_dataframe):
        """Test StatisticsComputer integration with the profiler."""
        computer = StatisticsComputer(sample_dataframe)

        # Test that the compute_all_columns_batch method works
        stats = computer.compute_all_columns_batch()

        # Verify we get stats for all columns
        assert len(stats) == len(sample_dataframe.columns)

        # Verify basic structure
        for col_name, col_stats in stats.items():
            assert "total_count" in col_stats
            assert "non_null_count" in col_stats
            assert "data_type" in col_stats


class TestUtils:
    """Test cases for utility functions."""

    def test_format_profile_output_dict(self, sample_dataframe):
        """Test dictionary format output."""
        profile = analyze(sample_dataframe, output_format="dict")

        formatted = format_profile_output(profile, format_type="dict")
        assert formatted == profile

    def test_format_profile_output_json(self, sample_dataframe):
        """Test JSON format output."""
        profile = analyze(sample_dataframe, output_format="dict")

        formatted = format_profile_output(profile, format_type="json")
        assert isinstance(formatted, str)
        assert "overview" in formatted
        assert "columns" in formatted

    def test_format_profile_output_summary(self, sample_dataframe):
        """Test summary format output."""
        profile = analyze(sample_dataframe, output_format="dict")

        formatted = format_profile_output(profile, format_type="summary")
        assert isinstance(formatted, str)
        assert "DataFrame Profile Summary" in formatted
        assert "Total Rows:" in formatted
        assert "Column:" in formatted

    def test_format_profile_output_invalid_format(self, sample_dataframe):
        """Test invalid format type."""
        from pyspark_analyzer import ConfigurationError

        profile = analyze(sample_dataframe, output_format="dict")

        with pytest.raises(ConfigurationError, match="Unsupported format type"):
            format_profile_output(profile, format_type="invalid_format")


if __name__ == "__main__":
    pytest.main([__file__])
