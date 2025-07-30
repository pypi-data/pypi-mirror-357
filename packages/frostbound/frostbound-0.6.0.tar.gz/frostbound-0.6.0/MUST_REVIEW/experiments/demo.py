from __future__ import annotations

import pickle
import tempfile
from pathlib import Path

from quantumblaze.experiments import ExperimentBuilder
from quantumblaze.experiments.core.storage import LocalFileStorage


def demo_alignment_experiment() -> None:
    """Demo with automatic timestamp appending.

    Two ways to add timestamps:
    1. .with_id("alignment").with_timestamp()
    2. .with_id("alignment", auto_timestamp=True)

    Both create folders like: alignment_20250806_143052
    """
    experiment = (
        ExperimentBuilder()
        .with_id("alignment")
        .with_timestamp()
        .with_description("Demo alignment experiment")
        .with_tags(["demo", "alignment", "test"])
        .with_storage(LocalFileStorage(Path("./output/experiments")))
        .add_parameter("source_lang", "en")
        .add_parameter("target_lang", "es")
        .add_parameter("alignment_threshold", 0.85)
        .build()
    )

    from quantumblaze.types import SegmentType, TranslationSegment

    source_segments = [
        TranslationSegment(
            id="src_1",
            text="Hello world",
            segment_type=SegmentType.PARAGRAPH,
        ),
        TranslationSegment(
            id="src_2",
            text="How are you?",
            segment_type=SegmentType.PARAGRAPH,
        ),
    ]

    target_segments = [
        TranslationSegment(
            id="tgt_1",
            text="Hola mundo",
            segment_type=SegmentType.PARAGRAPH,
        ),
        TranslationSegment(
            id="tgt_2",
            text="¿Cómo estás?",
            segment_type=SegmentType.PARAGRAPH,
        ),
    ]

    # Use save_dict for data serialization (MLflow pattern)
    source_data = [s.model_dump() for s in source_segments]
    target_data = [t.model_dump() for t in target_segments]

    # Lists need to be wrapped in a dict for save_dict
    experiment.save_dict({"segments": source_data}, "artifacts/source_segments.json")
    experiment.save_dict({"segments": target_data}, "artifacts/target_segments.json")

    # Direct file copy - no memory loading!
    config_path = Path("/Users/gaohn/gaohn/yinglong/quantumblaze/config/config_debug.yaml")
    if config_path.exists():
        experiment.save_artifact(config_path)  # Copy the actual file
        experiment.save_artifact(config_path, "configs")  # Copy to configs subdirectory

    # Save dict directly - auto-detects format from extension
    results = {"accuracy": 0.95, "precision": 0.92, "recall": 0.88}
    experiment.save_dict(results, "artifacts/results.json")  # JSON format
    experiment.save_dict(results, "artifacts/metrics/results.json")  # In subdirectory

    # Save dict as YAML (auto-detected from extension)
    config_dict = {"model": "bert", "learning_rate": 0.001}
    experiment.save_dict(config_dict, "artifacts/config.yaml")  # YAML format

    # Save text content
    experiment.save_text("Training completed successfully", "artifacts/logs/training.log")

    # Save complex nested data
    complex_data = {
        "experiment_id": "test_123",
        "description": "Test experiment",
        "tags": ["test", "demo"],
        "parameters": {"learning_rate": 0.001, "batch_size": 32},
    }
    experiment.save_dict(complex_data, "artifacts/experiment_config.json")

    experiment.record_metric("total_source_segments", len(source_segments))
    experiment.record_metric("total_target_segments", len(target_segments))
    experiment.record_metric("alignment_confidence", 0.95)

    experiment.complete()

    print(f"Experiment {experiment.id} completed!")
    print(f"Saved {len(experiment.artifacts)} artifacts")
    print(f"Recorded {len(experiment.metrics)} metrics")

    # Show what was saved
    print("Artifacts saved:")
    print("- source_segments.json")
    print("- target_segments.json")
    print("- config_debug.yaml")
    print("- configs/config_debug.yaml")
    print("- results.json")
    print("- metrics/results.json")
    print("- config.yaml")
    print("- logs/training.log")
    print("- experiment_config.json")


def demo_generic_experiment() -> None:
    experiment = (
        ExperimentBuilder()
        .with_id("generic_experiment", auto_timestamp=True)
        .with_description("Demo of generic experiment tracking")
        .with_storage(LocalFileStorage(Path("./output/experiments")))
        .build()
    )

    # Save dict as JSON
    training_data = {"X": [1, 2, 3], "y": [4, 5, 6]}
    experiment.save_dict(training_data, "artifacts/training_data.json")

    # Save dict as YAML (auto-detected from extension)
    experiment_config = {"model": "neural_net", "hyperparameters": {"learning_rate": 0.001, "batch_size": 32}}
    experiment.save_dict(experiment_config, "artifacts/experiment_config.yaml")

    # For pickle, we need to create a temp file first (no built-in save_pickle)
    model_config = {"layers": [10, 20, 10], "activation": "relu"}
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pkl") as f:
        pickle.dump(model_config, f)
        temp_path = f.name
    experiment.save_artifact(temp_path, "models")
    Path(temp_path).unlink()  # Clean up temp file

    experiment.record_metric("train_loss", 0.125)
    experiment.record_metric("val_loss", 0.142)
    experiment.record_metric("test_accuracy", 0.923)

    experiment.complete()

    print(f"\nGeneric experiment {experiment.id} completed!")
    print("Storage: In-memory")

    # Show what was saved
    print(f"Artifacts saved under experiment {experiment.id}")
    print("- training_data.json")
    print("- experiment_config.yaml")
    print("- models/model_config.pkl")


def demo_file_artifact() -> None:
    """Demo saving actual files as artifacts."""
    experiment = (
        ExperimentBuilder()
        .with_id("file_experiment")
        .with_timestamp()
        .with_storage(LocalFileStorage(Path("./output/experiments")))
        .build()
    )

    # Save any file directly - MLflow pattern!
    readme_path = Path("README.md")
    if readme_path.exists():
        experiment.save_artifact(readme_path)  # Copy the file
        experiment.save_artifact(readme_path, "docs")  # Copy to docs subdirectory

    # Save generated plot
    import matplotlib.pyplot as plt

    plt.figure(figsize=(8, 6))
    plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
    plt.title("Experiment Results")
    plt.savefig("temp_plot.png")
    plt.close()

    # Save the plot file
    plot_path = Path("temp_plot.png")
    experiment.save_artifact(plot_path, "plots")
    plot_path.unlink()  # Clean up temp file

    # Save directory example
    data_dir = Path("./quantumblaze/types")
    if data_dir.exists():
        experiment.save_artifacts(data_dir, "source_code/types")

    experiment.complete()
    print(f"\nFile experiment {experiment.id} completed!")


def demo_path_based_flexibility() -> None:
    """Demo the new path-based flexibility of save_dict and save_text.

    Shows how the new API allows saving to any path, not just artifacts/.
    """
    experiment = (
        ExperimentBuilder()
        .with_id("flexible_paths")
        .with_timestamp()
        .with_description("Demo of path-based save methods")
        .with_storage(LocalFileStorage(Path("./output/experiments")))
        .build()
    )

    # 1. Save config directly to configs/ (not under artifacts/)
    config = {"model": "gpt-4", "temperature": 0.7, "max_tokens": 2000}
    experiment.save_dict(config, "configs/model_config.yaml")

    # 2. Save logs directly to logs/ directory
    log_content = """[2024-06-09 10:30:00] Experiment started
[2024-06-09 10:35:00] Model initialized
[2024-06-09 10:40:00] Training completed"""
    experiment.save_text(log_content, "logs/experiment.log")

    # 3. Save results to a custom evaluation/ directory
    evaluation_results = {"accuracy": 0.95, "f1_score": 0.93, "confusion_matrix": [[95, 5], [3, 97]]}
    experiment.save_dict(evaluation_results, "evaluation/results.json")

    # 4. Save documentation at root level
    readme_content = f"""# Experiment {experiment.id}

This experiment demonstrates flexible path-based saving.

## Results
- Accuracy: 95%
- F1 Score: 93%
"""
    experiment.save_text(readme_content, "README.md")

    # 5. Contrast with save_artifact - still goes to artifacts/
    # Create a temp file to demonstrate
    import numpy as np

    data = np.random.randn(100, 10)  # noqa: NPY002
    with tempfile.NamedTemporaryFile(delete=False, suffix=".npy") as f:
        np.save(f, data)
        temp_path = f.name

    # This ALWAYS saves to artifacts/ directory and tracks the file
    artifact_key = experiment.save_artifact(temp_path, "data")
    Path(temp_path).unlink()

    # 6. Show the difference in tracking
    print(f"\nExperiment {experiment.id} completed!")
    print("\nFiles saved via save_dict/save_text (not tracked):")
    print("- configs/model_config.yaml")
    print("- logs/experiment.log")
    print("- evaluation/results.json")
    print("- README.md")

    print("\nArtifacts saved via save_artifact (tracked in experiment.artifacts):")
    print(f"- {artifact_key}")
    print(f"\nTotal tracked artifacts: {len(experiment.artifacts)}")

    # Complete the experiment
    experiment.complete()

    # Show the final structure
    print("\nFinal experiment structure:")
    print(f"{experiment.id}/")
    print("├── README.md                    # Root level doc")
    print("├── configs/")
    print("│   └── model_config.yaml        # Direct config save")
    print("├── logs/")
    print("│   └── experiment.log           # Direct log save")
    print("├── evaluation/")
    print("│   └── results.json             # Custom directory")
    print("├── artifacts/")
    print("│   └── data/")
    print("│       └── *.npy                # save_artifact always here")
    print("└── metadata/")
    print("    └── experiment.json          # Auto-generated")


if __name__ == "__main__":
    demo_alignment_experiment()
    demo_generic_experiment()
    demo_file_artifact()
    demo_path_based_flexibility()
