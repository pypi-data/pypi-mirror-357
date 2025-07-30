"""
Real-World Example: Building a Data Processing Pipeline with Dynamic Configuration

This example demonstrates how to use frostbound.pydanticonf to build a complete
data processing application where the entire architecture is defined in configuration
files and instantiated dynamically.

Architecture:
- Data Sources (Database, API, File)
- Data Processors (Cleaner, Transformer, Validator)
- Data Sinks (Database, File, API)
- Monitoring (Logger, Metrics)
- Orchestrator (Pipeline)

Everything is configurable and swappable via YAML configuration!
"""

import os
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel

from frostbound.pydanticonf import (
    ConfigLoader,
    DynamicConfig,
    instantiate,
    register_dependency,
)

console = Console()

# ============================================================================
# Abstract Base Classes (Protocols)
# ============================================================================


class DataSource(ABC):
    """Abstract base class for data sources."""

    @abstractmethod
    def read(self) -> List[Dict[str, Any]]:
        """Read data from the source."""
        pass


class DataProcessor(ABC):
    """Abstract base class for data processors."""

    @abstractmethod
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process the data."""
        pass


class DataSink(ABC):
    """Abstract base class for data sinks."""

    @abstractmethod
    def write(self, data: List[Dict[str, Any]]) -> None:
        """Write data to the sink."""
        pass


class Monitor(ABC):
    """Abstract base class for monitoring."""

    @abstractmethod
    def log(self, message: str) -> None:
        """Log a message."""
        pass

    @abstractmethod
    def metric(self, name: str, value: float) -> None:
        """Record a metric."""
        pass


# ============================================================================
# Concrete Implementations
# ============================================================================


class DatabaseSource(DataSource):
    """Reads data from a database."""

    def __init__(self, connection_string: str, query: str, monitor: Monitor):
        self.connection_string = connection_string
        self.query = query
        self.monitor = monitor
        self.monitor.log(f"DatabaseSource initialized: {connection_string}")

    def read(self) -> List[Dict[str, Any]]:
        self.monitor.log(f"Executing query: {self.query}")
        # Simulate database read
        data = [
            {"id": 1, "name": "Alice", "age": 30, "salary": 50000},
            {"id": 2, "name": "Bob", "age": 25, "salary": 45000},
            {"id": 3, "name": "Charlie", "age": 35, "salary": 60000},
        ]
        self.monitor.metric("records_read", len(data))
        return data


class FileSource(DataSource):
    """Reads data from a file."""

    def __init__(self, file_path: str, format: str, monitor: Monitor):
        self.file_path = file_path
        self.format = format
        self.monitor = monitor
        self.monitor.log(f"FileSource initialized: {file_path} ({format})")

    def read(self) -> List[Dict[str, Any]]:
        self.monitor.log(f"Reading file: {self.file_path}")
        # Simulate file read
        data = [
            {"product": "Widget A", "price": 10.99, "stock": 100},
            {"product": "Widget B", "price": 15.99, "stock": 50},
            {"product": "Widget C", "price": 8.99, "stock": 200},
        ]
        self.monitor.metric("records_read", len(data))
        return data


class DataCleaner(DataProcessor):
    """Cleans and validates data."""

    def __init__(self, remove_nulls: bool = True, monitor: Monitor = None):
        self.remove_nulls = remove_nulls
        self.monitor = monitor
        if self.monitor:
            self.monitor.log(f"DataCleaner initialized (remove_nulls={remove_nulls})")

    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if self.monitor:
            self.monitor.log(f"Cleaning {len(data)} records")

        cleaned_data = []
        for record in data:
            if self.remove_nulls:
                # Remove None values
                cleaned_record = {k: v for k, v in record.items() if v is not None}
            else:
                cleaned_record = record
            cleaned_data.append(cleaned_record)

        if self.monitor:
            self.monitor.metric("records_cleaned", len(cleaned_data))
        return cleaned_data


class DataTransformer(DataProcessor):
    """Transforms data according to rules."""

    def __init__(self, transformations: Dict[str, str], monitor: Monitor = None):
        self.transformations = transformations
        self.monitor = monitor
        if self.monitor:
            self.monitor.log(f"DataTransformer initialized with {len(transformations)} transformations")

    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if self.monitor:
            self.monitor.log(f"Transforming {len(data)} records")

        transformed_data = []
        for record in data:
            transformed_record = record.copy()

            # Apply transformations
            for field, transformation in self.transformations.items():
                if field in transformed_record:
                    if transformation == "uppercase":
                        transformed_record[field] = str(transformed_record[field]).upper()
                    elif transformation == "multiply_by_2":
                        if isinstance(transformed_record[field], int | float):
                            transformed_record[field] *= 2

            transformed_data.append(transformed_record)

        if self.monitor:
            self.monitor.metric("records_transformed", len(transformed_data))
        return transformed_data


class DatabaseSink(DataSink):
    """Writes data to a database."""

    def __init__(self, connection_string: str, table: str, monitor: Monitor):
        self.connection_string = connection_string
        self.table = table
        self.monitor = monitor
        self.monitor.log(f"DatabaseSink initialized: {connection_string} -> {table}")

    def write(self, data: List[Dict[str, Any]]) -> None:
        self.monitor.log(f"Writing {len(data)} records to {self.table}")
        # Simulate database write
        for record in data:
            console.print(f"  INSERT INTO {self.table}: {record}")
        self.monitor.metric("records_written", len(data))


class FileSink(DataSink):
    """Writes data to a file."""

    def __init__(self, file_path: str, format: str, monitor: Monitor):
        self.file_path = file_path
        self.format = format
        self.monitor = monitor
        self.monitor.log(f"FileSink initialized: {file_path} ({format})")

    def write(self, data: List[Dict[str, Any]]) -> None:
        self.monitor.log(f"Writing {len(data)} records to {self.file_path}")
        # Simulate file write
        console.print(f"  Writing to {self.file_path}:")
        for record in data:
            console.print(f"    {record}")
        self.monitor.metric("records_written", len(data))


class ConsoleMonitor(Monitor):
    """Simple console-based monitoring."""

    def __init__(self, name: str, log_level: str = "INFO"):
        self.name = name
        self.log_level = log_level
        self.metrics = {}
        console.print(f"📊 Monitor '{name}' initialized (level={log_level})")

    def log(self, message: str) -> None:
        console.print(f"[{self.log_level}] {self.name}: {message}")

    def metric(self, name: str, value: float) -> None:
        self.metrics[name] = self.metrics.get(name, 0) + value
        console.print(f"📈 {self.name} metric {name}: {value} (total: {self.metrics[name]})")


class DataPipeline:
    """Main pipeline orchestrator."""

    def __init__(
        self, name: str, source: DataSource, processors: List[DataProcessor], sink: DataSink, monitor: Monitor
    ):
        self.name = name
        self.source = source
        self.processors = processors
        self.sink = sink
        self.monitor = monitor
        self.monitor.log(f"Pipeline '{name}' initialized with {len(processors)} processors")

    def run(self) -> None:
        """Execute the complete pipeline."""
        self.monitor.log(f"Starting pipeline '{self.name}'")

        # Read data
        data = self.source.read()
        self.monitor.log(f"Read {len(data)} records from source")

        # Process data through each processor
        for i, processor in enumerate(self.processors):
            self.monitor.log(f"Running processor {i + 1}/{len(self.processors)}: {type(processor).__name__}")
            data = processor.process(data)
            self.monitor.log(f"Processor output: {len(data)} records")

        # Write data
        self.sink.write(data)

        self.monitor.log(f"Pipeline '{self.name}' completed successfully")


# ============================================================================
# Configuration Models
# ============================================================================


class DataSourceConfig(DynamicConfig[DataSource]):
    """Configuration for data sources."""

    pass


class DataProcessorConfig(DynamicConfig[DataProcessor]):
    """Configuration for data processors."""

    pass


class DataSinkConfig(DynamicConfig[DataSink]):
    """Configuration for data sinks."""

    pass


class MonitorConfig(DynamicConfig[Monitor]):
    """Configuration for monitors."""

    pass


class PipelineConfig(DynamicConfig[DataPipeline]):
    """Configuration for the pipeline."""

    name: str
    source: DataSourceConfig
    processors: List[DataProcessorConfig]
    sink: DataSinkConfig
    monitor: MonitorConfig


class AppConfig(BaseSettings):
    """Main application configuration."""

    model_config = SettingsConfigDict(env_prefix="PIPELINE_", env_nested_delimiter="__")

    app_name: str = "DataPipeline"
    debug: bool = False
    pipeline: PipelineConfig


# ============================================================================
# Example Configurations
# ============================================================================


def create_example_configs():
    """Create example YAML configurations for different scenarios."""

    # Configuration 1: Database to Database pipeline
    db_to_db_config = {
        "app_name": "DB-to-DB Pipeline",
        "debug": False,
        "pipeline": {
            "_target_": "__main__.DataPipeline",
            "name": "user_data_pipeline",
            "source": {
                "_target_": "__main__.DatabaseSource",
                "connection_string": "postgresql://user:pass@source-db:5432/source",
                "query": "SELECT * FROM users WHERE active = true",
                "monitor": {"_target_": "__main__.ConsoleMonitor", "name": "source_monitor", "log_level": "INFO"},
            },
            "processors": [
                {
                    "_target_": "__main__.DataCleaner",
                    "remove_nulls": True,
                    "monitor": {"_target_": "__main__.ConsoleMonitor", "name": "cleaner_monitor", "log_level": "DEBUG"},
                },
                {
                    "_target_": "__main__.DataTransformer",
                    "transformations": {"name": "uppercase", "salary": "multiply_by_2"},
                    "monitor": {
                        "_target_": "__main__.ConsoleMonitor",
                        "name": "transformer_monitor",
                        "log_level": "INFO",
                    },
                },
            ],
            "sink": {
                "_target_": "__main__.DatabaseSink",
                "connection_string": "postgresql://user:pass@dest-db:5432/dest",
                "table": "processed_users",
                "monitor": {"_target_": "__main__.ConsoleMonitor", "name": "sink_monitor", "log_level": "INFO"},
            },
            "monitor": {"_target_": "__main__.ConsoleMonitor", "name": "pipeline_monitor", "log_level": "INFO"},
        },
    }

    # Configuration 2: File to File pipeline (simpler)
    file_to_file_config = {
        "app_name": "File-to-File Pipeline",
        "debug": True,
        "pipeline": {
            "_target_": "__main__.DataPipeline",
            "name": "product_data_pipeline",
            "source": {
                "_target_": "__main__.FileSource",
                "file_path": "/data/products.csv",
                "format": "csv",
                "monitor": {"_target_": "__main__.ConsoleMonitor", "name": "file_source_monitor"},
            },
            "processors": [
                {
                    "_target_": "__main__.DataTransformer",
                    "transformations": {"product": "uppercase", "price": "multiply_by_2"},
                    "monitor": {"_target_": "__main__.ConsoleMonitor", "name": "price_doubler"},
                }
            ],
            "sink": {
                "_target_": "__main__.FileSink",
                "file_path": "/output/processed_products.json",
                "format": "json",
                "monitor": {"_target_": "__main__.ConsoleMonitor", "name": "file_sink_monitor"},
            },
            "monitor": {"_target_": "__main__.ConsoleMonitor", "name": "main_pipeline_monitor"},
        },
    }

    return db_to_db_config, file_to_file_config


def demo_scenario_1():
    """Demo: Database to Database pipeline with dependency injection."""
    console.print(Panel("Scenario 1: Database to Database Pipeline", style="bold blue"))

    # Create shared monitor for dependency injection
    shared_monitor = ConsoleMonitor("shared_global_monitor", "INFO")
    register_dependency("monitor", shared_monitor)

    db_config, _ = create_example_configs()

    # Write config to temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(db_config, f)
        config_path = Path(f.name)

    try:
        console.print("📝 Loading configuration from YAML...")
        config = ConfigLoader.from_yaml(AppConfig, config_path)

        console.print(f"✅ Configuration loaded: {config.app_name}")
        console.print(f"   Debug mode: {config.debug}")
        console.print(f"   Pipeline name: {config.pipeline.name}")

        console.print("\n🔧 Instantiating pipeline...")
        pipeline = instantiate(config.pipeline)

        console.print("\n🚀 Running pipeline...")
        pipeline.run()

    finally:
        config_path.unlink()

    console.print()


def demo_scenario_2():
    """Demo: File to File pipeline with environment overrides."""
    console.print(Panel("Scenario 2: File to File Pipeline with Environment Overrides", style="bold blue"))

    _, file_config = create_example_configs()

    # Write config to temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(file_config, f)
        config_path = Path(f.name)

    # Set environment overrides
    original_env = dict(os.environ)
    os.environ.update(
        {
            "PIPELINE_APP_NAME": "Environment Override Pipeline",
            "PIPELINE_DEBUG": "false",
            "PIPELINE_PIPELINE__SOURCE__FILE_PATH": "/override/input.csv",
            "PIPELINE_PIPELINE__SINK__FILE_PATH": "/override/output.json",
        }
    )

    try:
        console.print("📝 Loading configuration with environment overrides...")
        config = ConfigLoader.from_yaml_with_env(AppConfig, config_path, env_prefix="PIPELINE")

        console.print(f"✅ Configuration loaded: {config.app_name}")
        console.print(f"   Debug mode: {config.debug}")
        console.print(f"   Source file: {config.pipeline.source.file_path}")
        console.print(f"   Sink file: {config.pipeline.sink.file_path}")

        console.print("\n🔧 Instantiating pipeline...")
        pipeline = instantiate(config.pipeline)

        console.print("\n🚀 Running pipeline...")
        pipeline.run()

    finally:
        config_path.unlink()
        os.environ.clear()
        os.environ.update(original_env)

    console.print()


def demo_scenario_3():
    """Demo: Dynamic pipeline configuration based on runtime parameters."""
    console.print(Panel("Scenario 3: Dynamic Pipeline Configuration", style="bold blue"))

    def create_dynamic_pipeline(source_type: str, enable_cleaning: bool, output_format: str):
        """Create pipeline configuration dynamically based on parameters."""

        # Choose source based on type
        if source_type == "database":
            source_config = {
                "_target_": "__main__.DatabaseSource",
                "connection_string": "postgresql://localhost:5432/data",
                "query": "SELECT * FROM raw_data",
            }
        else:
            source_config = {
                "_target_": "__main__.FileSource",
                "file_path": f"/data/input.{source_type}",
                "format": source_type,
            }

        # Choose processors based on options
        processors = []
        if enable_cleaning:
            processors.append({"_target_": "__main__.DataCleaner", "remove_nulls": True})

        processors.append({"_target_": "__main__.DataTransformer", "transformations": {"name": "uppercase"}})

        # Choose sink based on output format
        if output_format == "database":
            sink_config = {
                "_target_": "__main__.DatabaseSink",
                "connection_string": "postgresql://localhost:5432/output",
                "table": "processed_data",
            }
        else:
            sink_config = {
                "_target_": "__main__.FileSink",
                "file_path": f"/output/result.{output_format}",
                "format": output_format,
            }

        return {
            "_target_": "__main__.DataPipeline",
            "name": f"dynamic_{source_type}_to_{output_format}_pipeline",
            "source": source_config,
            "processors": processors,
            "sink": sink_config,
            "monitor": {"_target_": "__main__.ConsoleMonitor", "name": "dynamic_monitor"},
        }

    # Create different pipeline configurations
    scenarios = [("csv", True, "json"), ("database", False, "database"), ("json", True, "csv")]

    for source_type, enable_cleaning, output_format in scenarios:
        console.print(f"\n🔧 Creating {source_type} → {output_format} pipeline (cleaning={enable_cleaning}):")

        pipeline_config = create_dynamic_pipeline(source_type, enable_cleaning, output_format)
        pipeline = instantiate(pipeline_config)

        console.print(f"   Pipeline: {pipeline.name}")
        console.print(f"   Source: {type(pipeline.source).__name__}")
        console.print(f"   Processors: {len(pipeline.processors)}")
        console.print(f"   Sink: {type(pipeline.sink).__name__}")

    console.print()


def main():
    """Run all demonstration scenarios."""
    console.print(
        Panel.fit(
            "🏭 Real-World Data Pipeline Example\n\n"
            "This demonstrates how to build a complete, configurable\n"
            "data processing application using frostbound.pydanticonf.\n\n"
            "Features:\n"
            "• Pluggable data sources, processors, and sinks\n"
            "• Complete configuration via YAML files\n"
            "• Environment variable overrides\n"
            "• Dependency injection\n"
            "• Dynamic pipeline creation",
            title="Data Pipeline Demo",
            style="bold green",
        )
    )

    demo_scenario_1()
    demo_scenario_2()
    demo_scenario_3()

    console.print(
        Panel.fit(
            "🎉 Real-World Demo Complete!\n\n"
            "Key takeaways:\n\n"
            "• Configuration-driven architecture enables flexibility\n"
            "• Components are easily swappable via config changes\n"
            "• Environment overrides enable deployment flexibility\n"
            "• Dependency injection reduces configuration duplication\n"
            "• Dynamic instantiation enables runtime adaptability\n\n"
            "This pattern scales to complex enterprise applications!",
            title="✅ Demo Complete",
            style="bold green",
        )
    )


if __name__ == "__main__":
    main()
