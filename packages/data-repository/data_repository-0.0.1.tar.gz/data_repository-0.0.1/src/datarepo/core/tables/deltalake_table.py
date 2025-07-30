# mypy: disable-error-code=override

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import os
from typing import Any, TypeAlias
import warnings

import boto3
from deltalake import DeltaTable, QueryBuilder
from deltalake.warnings import ExperimentalWarning
import polars as pl
import pyarrow as pa

from datarepo.core.dataframe import NlkDataFrame
from datarepo.core.tables.filters import InputFilters, normalize_filters
from datarepo.core.tables.metadata import (
    TableMetadata,
    TableProtocol,
    TableSchema,
)
from datarepo.core.tables.util import (
    DeltaRoapiOptions,
    Filter,
    RoapiOptions,
    filters_to_sql_predicate,
    get_storage_options,
)

READ_PARQUET_RETRY_COUNT = 10
DEFAULT_TIMEOUT = "150s"

DeltaInputFilters: TypeAlias = InputFilters | str


@dataclass
class DeltaCacheOptions:
    # Path to the directory where files are cached. This can be the same for all tables
    # since the S3 table prefix is included in the cached paths.
    file_cache_path: str
    # Duration for which the _last_checkpoint file is cached. A longer duration means
    # we can reuse cached checkpoints for longer, which could improve loading performance
    # from not downloading new checkpoint parquets. However, we also need to load more
    # individual transaction jsons, so this should not be set too high.
    # A reasonable value for a table with frequent updates (e.g. binned spikes) is 30m.
    file_cache_last_checkpoint_valid_duration: str | None = None

    def to_storage_options(self) -> dict[str, Any]:
        opts = {
            "file_cache_path": os.path.expanduser(self.file_cache_path),
        }
        if self.file_cache_last_checkpoint_valid_duration is not None:
            opts["file_cache_last_checkpoint_valid_duration"] = (
                self.file_cache_last_checkpoint_valid_duration
            )
        return opts


class DeltalakeTable(TableProtocol):
    def __init__(
        self,
        name: str,
        uri: str,
        schema: pa.Schema,
        description: str = "",
        docs_filters: list[Filter] = [],
        docs_columns: list[str] | None = None,
        roapi_opts: RoapiOptions | None = None,
        unique_columns: list[str] | None = None,
        table_metadata_args: dict[str, Any] | None = None,
        stats_cols: list[str] | None = None,
        extra_cols: list[tuple[pl.Expr, str]] | None = None,
    ):
        self.name = name
        self.uri = uri
        self.schema = schema
        self.unique_columns = unique_columns
        self.stats_cols = stats_cols or []
        self.extra_cols = extra_cols or []

        self.table_metadata = TableMetadata(
            table_type="DELTA_LAKE",
            description=description,
            docs_args={"filters": docs_filters, "columns": docs_columns},
            roapi_opts=roapi_opts or DeltaRoapiOptions(),
            **(table_metadata_args or {}),
        )

    def get_schema(self) -> TableSchema:
        dt = self.delta_table()
        schema = self.schema
        partition_cols = dt.metadata().partition_columns
        filters = {
            f.column: f.value
            for f in self.table_metadata.docs_args.get("filters", [])
            if isinstance(f, Filter)
        }
        partitions = [
            {
                "column_name": col,
                "type_annotation": str(schema.field(col).type),
                "value": filters.get(col),
            }
            for col in partition_cols
        ]
        columns = [
            {
                "name": name,
                "type": str(schema.field(name).type),
                "has_stats": name in partition_cols or name in self.stats_cols,
            }
            for name in schema.names
        ]
        columns += [
            {
                "name": expr.meta.output_name(),
                "type": expr_type,
                "readonly": True,
            }
            for expr, expr_type in self.extra_cols
        ]
        return TableSchema(
            partitions=partitions,
            columns=columns,
        )

    def __call__(
        self,
        filters: DeltaInputFilters | None = None,
        columns: list[str] | None = None,
        boto3_session: boto3.Session | None = None,
        endpoint_url: str | None = None,
        timeout: str | None = None,
        cache_options: DeltaCacheOptions | None = None,
        **kwargs: Any,
    ) -> NlkDataFrame:
        storage_options = {
            "timeout": timeout or DEFAULT_TIMEOUT,
            **get_storage_options(
                boto3_session=boto3_session, endpoint_url=endpoint_url
            ),
        }
        if cache_options is not None:
            storage_options = {
                **storage_options,
                **cache_options.to_storage_options(),
            }
        dt = self.delta_table(storage_options=storage_options)

        return self.construct_df(dt=dt, filters=filters, columns=columns)

    def construct_df(
        self,
        dt: DeltaTable,
        filters: DeltaInputFilters | None = None,
        columns: list[str] | None = None,
    ) -> NlkDataFrame:
        # Use schema defined on this table, the physical schema in deltalake metadata might be different
        schema = self.schema

        predicate_str = datafusion_predicate_from_filters(schema, filters)

        # These should not be read because they don't exist in the delta table
        extra_col_exprs = [expr for expr, _ in self.extra_cols]
        extra_column_names = set(expr.meta.output_name() for expr in extra_col_exprs)

        columns_to_read = None
        unique_column_names = set(self.unique_columns or [])
        if columns:
            columns_to_read = list(
                (set(columns) | unique_column_names) - extra_column_names
            )

        # TODO(peter): consider a sql builder for more complex queries?
        select_cols = (
            ", ".join([f'"{col}"' for col in columns_to_read])
            if columns_to_read
            else "*"
        )
        condition = f"WHERE {predicate_str}" if predicate_str else ""
        query_string = f"""
            SELECT {select_cols}
            FROM "{self.name}"
            {condition}
        """
        with warnings.catch_warnings():
            # Ignore ExperimentalWarning emitted from QueryBuilder
            warnings.filterwarnings("ignore", category=ExperimentalWarning)
            batches = (
                QueryBuilder().register(self.name, dt).execute(query_string).fetchall()
            )

        # Since we might cast unique string columns to categoricals, use a string cache to
        # improve performance when combining multiple dataframes
        with pl.StringCache():
            if batches:
                frame = pl.from_arrow(batches, rechunk=False)
                frame = _normalize_df(frame, self.schema, columns=columns_to_read)
            else:
                # If dataset is empty, the returned dataframe will have no columns
                frame = _empty_normalized_df(schema)

            if self.extra_cols:
                frame = frame.with_columns(extra_col_exprs)

            if self.unique_columns:
                # Cast unique string columns to categoricals first
                # In some cases, this reduces peak memory usage up to 50%
                curr_schema = frame.schema
                cat_schema = {
                    col: pl.Categorical
                    for col in curr_schema
                    if curr_schema[col] == pl.String
                }
                frame = (
                    frame.cast(cat_schema)
                    .unique(subset=self.unique_columns, maintain_order=True)
                    .cast(curr_schema)
                )

        if columns:
            frame = frame.select(columns)

        return frame.lazy()

    def delta_table(
        self, storage_options: dict[str, Any] | None = None, version: int | None = None
    ) -> DeltaTable:
        return DeltaTable(
            table_uri=self.uri, storage_options=storage_options, version=version
        )


def fetch_df_by_partition(
    dt: DeltaTable,
    partition: list[tuple[str, str, Any]],
    schema: pa.Schema,
    storage_options: dict[str, Any] | None = None,
) -> pl.DataFrame:
    """
    The native delta-rs read has slower performance. The difference comes from the dataset in
    dt.to_pyarrow_dataset() - this dataset is slower than the one manually constructed below.

    pyarrow.dataset.Dataset.to_table() reading was also tried, however this also resulted
    in slower performance for larger datasets. For example, reading P1 webgrid data on 2024-05-21
    (2.1M+ rows) takes ~20+ seconds.

    The hypothesized reason(s) for the slow read performance of pyarrow.dataset.Dataset.to_table()
    are
    1. Additional step of metadata loading
    2. Lazy loading which could lead to longer load times
    Source: https://github.com/apache/arrow/issues/35332

    When using pyarrow's parquet read_table(), which will eagerly read the entire dataset, the
    read for the P1 webgrid data on 2024-05-21 (2.1M+ rows) takes ~7-10 seconds.
    Thus, it makes sense to use read_table() since we have a predefined list of files to be loaded
    from dt.files

    """
    files = dt.files(partition_filters=partition)

    files = [os.path.join(dt.table_uri, file) for file in files]

    if not files:
        # NOTE: polars has a bug where with_columns(...) on an empty dataframe with no columns will add a row
        # for all new columns. Workaround by adding the columns before normalizing
        return _empty_normalized_df(schema)

    return fetch_dfs_by_paths(
        files=files, schema=schema, storage_options=storage_options
    )


def fetch_dfs_by_paths(
    files: list[str],
    schema: pa.Schema,
    storage_options: dict[str, Any] | None = None,
) -> pl.DataFrame:
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                pl.read_parquet,
                file,
                retries=READ_PARQUET_RETRY_COUNT,
                storage_options=storage_options,
                # Hive partitioning was disabled by default in https://github.com/pola-rs/polars/pull/17106
                hive_partitioning=True,
            )
            for file in files
        ]
        concurrent.futures.wait(futures)

    dfs = [future.result() for future in futures]

    return pl.concat([_normalize_df(df, schema=schema) for df in dfs])


def _empty_normalized_df(schema: pa.Schema) -> pl.DataFrame:
    return _normalize_df(pl.DataFrame({col: [] for col in schema.names}), schema=schema)


def _normalize_df(
    df: pl.DataFrame,
    schema: pa.Schema,
    columns: list[str] | None = None,
) -> pl.DataFrame:
    """
    Add missing columns, cast, and reorder dataframe columns to the specified schema's order.

    If columns is provided, only those columns will be added.
    """
    polars_schema = pl.from_arrow(schema.empty_table()).schema
    if columns:
        # Only add back specified columns
        polars_schema = {
            col: dtype for col, dtype in polars_schema.items() if col in columns
        }

    schema_columns = list(polars_schema.keys())
    missing_columns = set(schema_columns) - set(df.columns)
    return (
        df.with_columns(pl.lit(None).alias(col) for col in missing_columns)
        .cast(polars_schema)
        .select(schema_columns)
    )


def datafusion_predicate_from_filters(
    schema: pa.Schema, filters: DeltaInputFilters | None
) -> str | None:
    if not filters:
        return None
    elif isinstance(filters, str):
        return filters

    normalized_filters = normalize_filters(filters)
    return filters_to_sql_predicate(schema, normalized_filters)
