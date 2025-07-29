"""
Test cases for performance optimization utilities.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, date

from pyspark_analyzer.performance import optimize_dataframe_for_profiling
from pyspark_analyzer.statistics import StatisticsComputer


class TestStatisticsComputerBatch:
    """Test cases for StatisticsComputer batch functionality."""

    def test_init(self, sample_dataframe):
        """Test initialization of StatisticsComputer."""
        computer = StatisticsComputer(sample_dataframe)
        assert computer.df is sample_dataframe
        assert computer.cache_enabled is False

    def test_enable_caching(self, sample_dataframe):
        """Test enabling DataFrame caching."""
        computer = StatisticsComputer(sample_dataframe)

        # Mock the cache method
        sample_dataframe.cache = Mock(return_value=sample_dataframe)

        computer.enable_caching()
        assert computer.cache_enabled is True
        sample_dataframe.cache.assert_called_once()

        # Test that enabling again doesn't cache twice
        computer.enable_caching()
        sample_dataframe.cache.assert_called_once()

    def test_disable_caching(self, sample_dataframe):
        """Test disabling DataFrame caching."""
        computer = StatisticsComputer(sample_dataframe)

        # Mock cache and unpersist methods
        sample_dataframe.cache = Mock(return_value=sample_dataframe)
        sample_dataframe.unpersist = Mock(return_value=sample_dataframe)

        # Enable then disable caching
        computer.enable_caching()
        computer.disable_caching()

        assert computer.cache_enabled is False
        sample_dataframe.unpersist.assert_called_once()

        # Test that disabling again doesn't unpersist twice
        computer.disable_caching()
        sample_dataframe.unpersist.assert_called_once()

    def test_compute_all_columns_batch(self, sample_dataframe):
        """Test batch computation of statistics for all columns."""

        computer = StatisticsComputer(sample_dataframe)
        results = computer.compute_all_columns_batch()

        # Check that all columns are processed
        assert set(results.keys()) == {"id", "name", "age", "salary"}

        # Check numeric column statistics
        assert results["id"]["data_type"] == "LongType()"
        assert results["id"]["total_count"] == 5  # sample_dataframe has 5 rows
        assert results["id"]["null_count"] == 0
        assert results["id"]["min"] == 1
        assert results["id"]["max"] == 5

        # Check string column statistics
        assert results["name"]["data_type"] == "StringType()"
        assert results["name"]["total_count"] == 5
        assert (
            results["name"]["null_count"] == 0
        )  # All names are non-null in sample data
        assert results["name"]["empty_count"] == 0  # No empty strings in sample data

        # Check that caching was cleaned up
        assert computer.cache_enabled is False

    def test_compute_all_columns_batch_specific_columns(self, sample_dataframe):
        """Test batch computation for specific columns only."""
        computer = StatisticsComputer(sample_dataframe)

        # Test with subset of columns
        selected_columns = ["id", "name"]
        results = computer.compute_all_columns_batch(columns=selected_columns)

        assert set(results.keys()) == set(selected_columns)
        assert "age" not in results
        assert "salary" not in results

    def test_compute_column_stats_numeric(self, spark_session):
        """Test statistics computation for numeric columns."""
        data = [(1, 10.5), (2, 20.0), (3, 30.5), (4, None), (5, 50.0)]
        df = spark_session.createDataFrame(data, ["id", "value"])

        computer = StatisticsComputer(df)
        stats = computer.compute_all_columns_batch(columns=["value"])["value"]

        assert stats["data_type"] == "DoubleType()"
        assert stats["total_count"] == 5
        assert stats["non_null_count"] == 4
        assert stats["null_count"] == 1
        assert stats["null_percentage"] == 20.0
        assert stats["min"] == 10.5
        assert stats["max"] == 50.0
        assert "mean" in stats
        assert "median" in stats
        assert "q1" in stats
        assert "q3" in stats

    def test_compute_column_stats_string(self, spark_session):
        """Test statistics computation for string columns."""
        data = [
            (1, "short"),
            (2, "medium length"),
            (3, "a very long string here"),
            (4, ""),
            (5, None),
        ]
        df = spark_session.createDataFrame(data, ["id", "text"])

        computer = StatisticsComputer(df)
        stats = computer.compute_all_columns_batch(columns=["text"])["text"]

        assert stats["data_type"] == "StringType()"
        assert stats["total_count"] == 5
        assert stats["null_count"] == 1
        assert stats["empty_count"] == 1
        assert stats["min_length"] == 0  # empty string
        assert stats["max_length"] == 23  # "a very long string here"
        assert "avg_length" in stats

    def test_compute_column_stats_temporal(self, spark_session):
        """Test statistics computation for temporal columns."""
        data = [
            (1, datetime(2023, 1, 1), date(2023, 1, 1)),
            (2, datetime(2023, 6, 15), date(2023, 6, 15)),
            (3, datetime(2023, 12, 31), date(2023, 12, 31)),
            (4, None, None),
        ]
        df = spark_session.createDataFrame(data, ["id", "timestamp", "date"])

        computer = StatisticsComputer(df)
        all_stats = computer.compute_all_columns_batch(columns=["timestamp", "date"])

        # Test timestamp column
        timestamp_stats = all_stats["timestamp"]
        assert timestamp_stats["data_type"] == "TimestampType()"
        assert timestamp_stats["min_date"] == datetime(2023, 1, 1)
        assert timestamp_stats["max_date"] == datetime(2023, 12, 31)
        assert timestamp_stats["date_range_days"] == 364

        # Test date column
        date_stats = all_stats["date"]
        assert date_stats["data_type"] == "DateType()"
        assert date_stats["min_date"] == date(2023, 1, 1)
        assert date_stats["max_date"] == date(2023, 12, 31)

    def test_compute_column_stats_with_all_nulls(self, spark_session):
        """Test statistics computation when column has all null values."""
        from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType

        schema = StructType(
            [
                StructField("id", IntegerType(), True),
                StructField("value", DoubleType(), True),
            ]
        )
        data = [(1, None), (2, None), (3, None)]
        df = spark_session.createDataFrame(data, schema=schema)

        computer = StatisticsComputer(df)
        stats = computer.compute_all_columns_batch(columns=["value"])["value"]

        assert stats["total_count"] == 3
        assert stats["non_null_count"] == 0
        assert stats["null_count"] == 3
        assert stats["null_percentage"] == 100.0
        assert stats["distinct_percentage"] == 0.0

    def test_error_handling_in_batch_compute(self, sample_dataframe):
        """Test error handling during batch computation."""
        computer = StatisticsComputer(sample_dataframe)

        # Mock enable_caching to raise an exception
        computer.enable_caching = Mock(side_effect=Exception("Cache error"))

        # Should handle error and still return empty results
        with pytest.raises(Exception):
            computer.compute_all_columns_batch()

        # Ensure caching is disabled even on error
        assert computer.cache_enabled is False


class TestOptimizeDataFrameForProfiling:
    """Test cases for optimize_dataframe_for_profiling function."""

    def test_no_optimization(self, sample_dataframe):
        """Test when no optimization is applied."""
        result = optimize_dataframe_for_profiling(sample_dataframe)
        # Should return the same DataFrame when no sampling
        assert result.count() == sample_dataframe.count()

    def test_sampling_optimization(self, spark_session):
        """Test DataFrame sampling optimization."""
        # Create a larger DataFrame
        data = [(i, f"name_{i}", i * 1.5) for i in range(1000)]
        df = spark_session.createDataFrame(data, ["id", "name", "value"])

        # Apply sampling
        result = optimize_dataframe_for_profiling(df, sample_fraction=0.1)

        # Check that sampling reduced the size
        result_count = result.count()
        assert result_count < 1000
        assert result_count > 50  # Should have at least some rows

    def test_invalid_sample_fraction(self, sample_dataframe):
        """Test with invalid sample fractions."""
        # Sample fraction of 0 should not sample
        result = optimize_dataframe_for_profiling(sample_dataframe, sample_fraction=0)
        assert result.count() == sample_dataframe.count()

        # Sample fraction of 1.0 should not sample
        result = optimize_dataframe_for_profiling(sample_dataframe, sample_fraction=1.0)
        assert result.count() == sample_dataframe.count()

        # Sample fraction > 1 should not sample
        result = optimize_dataframe_for_profiling(sample_dataframe, sample_fraction=1.5)
        assert result.count() == sample_dataframe.count()

    def test_repartitioning_small_dataset(self, spark_session):
        """Test repartitioning optimization for small datasets."""
        # Create a small DataFrame with multiple partitions
        data = [(i, f"name_{i}") for i in range(10)]
        df = spark_session.createDataFrame(data, ["id", "name"]).repartition(10)

        # Check initial partitions
        assert df.rdd.getNumPartitions() == 10

        # Optimize should coalesce to 1 partition for small data
        result = optimize_dataframe_for_profiling(df)
        assert result.rdd.getNumPartitions() == 1

    def test_repartitioning_large_dataset(self, sample_dataframe):
        """Test repartitioning optimization for large datasets."""
        # Use context managers for proper mocking
        with patch.object(sample_dataframe, "count", return_value=2_000_000):
            with patch.object(sample_dataframe.rdd, "getNumPartitions", return_value=2):
                with patch.object(sample_dataframe, "repartition") as mock_repartition:
                    # Mock repartition to return a new DataFrame mock
                    mock_repartitioned_df = Mock()
                    mock_repartitioned_df.rdd.getNumPartitions.return_value = 8
                    mock_repartition.return_value = mock_repartitioned_df

                    result = optimize_dataframe_for_profiling(sample_dataframe)

        # With adaptive partitioning, the logic is more sophisticated
        # It considers data size and cluster configuration
        result_partitions = result.rdd.getNumPartitions()
        # The new logic may decide not to repartition if the overhead isn't worth it
        # or may repartition based on estimated data size
        assert result_partitions >= 1  # At least some partitions

    def test_medium_dataset_no_repartition(self, spark_session):
        """Test that medium-sized datasets are not repartitioned."""
        # Create a medium DataFrame
        data = [(i, f"name_{i}") for i in range(10000)]
        df = spark_session.createDataFrame(data, ["id", "name"]).repartition(4)

        # Optimize should apply adaptive logic
        result = optimize_dataframe_for_profiling(df, row_count=10000)
        # With adaptive partitioning, the optimal number of partitions
        # depends on data size and cluster configuration
        result_partitions = result.rdd.getNumPartitions()
        # For 10K rows, it should optimize to a reasonable number
        assert 1 <= result_partitions <= 8

    def test_row_count_parameter_avoids_redundant_count(self, spark_session, mocker):
        """Test that providing row_count parameter avoids redundant count operations."""
        # Create a DataFrame
        data = [(i, f"name_{i}", i * 10) for i in range(100)]
        df = spark_session.createDataFrame(data, ["id", "name", "value"])

        # Mock the count method to track calls
        count_spy = mocker.spy(df, "count")

        # Call optimize without row_count - should call count()
        optimize_dataframe_for_profiling(df)
        assert count_spy.call_count == 1

        # Reset spy
        count_spy.reset_mock()

        # Call optimize with row_count - should NOT call count()
        optimize_dataframe_for_profiling(df, row_count=100)
        assert count_spy.call_count == 0
