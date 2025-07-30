from typing import Any, Optional, Tuple
import pandas as pd  # only needed for type hints when engine is pandas

from .config import JobConfig, Engine
from .connectors.pandas import PandasConnector
from .connectors.polars import PolarsConnector
from .connectors.duckdb import DuckDBConnector


class Aquifer:
    """
    Core class for the pyaquifer pipeline.
    Dispatches load/transform/write to the chosen engine connector.
    """

    def __init__(self, config: JobConfig):
        self.config = config

        if config.engine is Engine.PANDAS:
            self.connector = PandasConnector(
                region_name       = config.region_name,
                aws_profile_name  = config.aws_profile_name,
                input_bucket_arn  = config.input_bucket_arn,
                glue_database     = config.glue_database,
                output_bucket_arn = config.resolved_output_bucket_arn,
            )
        elif config.engine is Engine.POLARS:
            self.connector = PolarsConnector(
                region_name       = config.region_name,
                aws_profile_name  = config.aws_profile_name,
                input_bucket_arn  = config.input_bucket_arn,
                glue_database     = config.glue_database,
                output_bucket_arn = config.resolved_output_bucket_arn,
            )
        elif config.engine is Engine.DUCKDB:
            self.connector = DuckDBConnector(
                region_name       = config.region_name,
                aws_profile_name  = config.aws_profile_name,
                input_bucket_arn  = config.input_bucket_arn,
                glue_database     = config.glue_database,
                output_bucket_arn = config.resolved_output_bucket_arn,
            )
        else:
            raise ValueError(f"Unsupported engine: {config.engine}")

    def load(self, table_name: str) -> Any:
        """
        Load one table from the input namespace into the selected engine's DataFrame.
        """
        return self.connector.load_table(self.config.iceberg_namespace, table_name)

    def transform(self, df: Any, **kwargs: Any) -> Any:
        """
        Apply user-defined transformations to the DataFrame.
        Default implementation is a no-op.
        """
        return df

    def write(
        self,
        table_name: str,
        df: Any,
        append: bool = False,
    ) -> None:
        """
        Persist a transformed DataFrame back to Iceberg in the output namespace.

        Parameters
        ----------
        table_name : str
            Name of the table to write (without namespace).
        df : Any
            Your Pandas/Polars/DuckDB result.
        append : bool, default=False
            If True and the table already exists, will append new rows
            rather than overwriting the entire table.
        """
        # delegate to the connector, passing along the append flag
        self.connector.write_table(
            namespace=self.config.output_namespace,
            table_name=table_name,
            df=df,
            append=append,
        )

    def delta_load(
        self,
        table_name: str,
        start_snapshot: Optional[int] = None,
    ) -> Tuple[Any, int]:
        """
        Incrementally load only the rows added since `start_snapshot`.

        Parameters
        ----------
        table_name : str
            The name of the table (no namespace).
        start_snapshot : int, optional
            The Iceberg snapshot_id to start from.  If None, you get *all* rows.

        Returns
        -------
        delta : Any
            Depending on your engine, this is
              - a pandas.DataFrame (Engine.PANDAS)
              - a polars.DataFrame  (Engine.POLARS)
              - a DuckDB view name  (Engine.DUCKDB)
        latest_snapshot : int
            The snapshot_id at which this load was taken.  Store it for next time.
        """
        # build the full identifier
        namespace = self.config.iceberg_namespace
        return self.connector.delta_load(
            namespace=namespace,
            table_name=table_name,
            start_snapshot=start_snapshot,
        )