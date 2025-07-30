"""
Utilities for pipeline visualization using pure Python dependencies.
"""

from pathlib import Path
from typing import Optional, Tuple, Union

import graphviz
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from pipetee.pipeline import Pipeline


def create_pipeline_graph(
    pipeline: Pipeline,
    output_path: Union[str, Path],
    format: str = "png",
) -> Optional[Path]:
    """
    Create a visualization of the pipeline structure using graphviz.

    Args:
        pipeline: The Pipeline instance to visualize
        output_path: Path where the output image should be saved
        format: Output format (png, svg, pdf)

    Returns:
        Optional[Path]: Path to the generated image file, or None if generation failed
    """
    try:
        # Create a new directed graph
        dot = graphviz.Digraph(comment="Pipeline Structure")
        dot.attr(rankdir="LR")  # Left to right layout

        # Status colors
        colors = {
            "pending": "#808080",  # Gray
            "running": "#FFA500",  # Orange
            "completed": "#32CD32",  # Green
            "skipped": "#87CEEB",  # Light blue
            "failed": "#FF0000",  # Red
        }

        # Status icons (emoji work in most modern viewers)
        icons = {
            "pending": "🔄",
            "running": "⚡",
            "completed": "✅",
            "skipped": "⏭️",
            "failed": "❌",
        }

        # Add nodes for each stage
        for stage_name, stage_info in pipeline.visualizer.viz_data.items():
            status = stage_info.status
            color = colors.get(status, "#808080")
            icon = icons.get(status, "")

            # Create node label with status icon
            label = f"{icon} {stage_name}\n({status})"

            dot.node(
                stage_name,
                label,
                style="filled",
                fillcolor=color,
                fontcolor="white" if status in ["failed", "running"] else "black",
            )

        # Add edges for default sequence
        for i in range(len(pipeline.default_sequence) - 1):
            current = pipeline.default_sequence[i]
            next_stage = pipeline.default_sequence[i + 1]
            dot.edge(current, next_stage)

        # Add edges for branch conditions
        for stage_name, stage in pipeline.stages.items():
            for condition, target in stage.branch_conditions.items():
                dot.edge(stage_name, target, label=condition.name, style="dashed")

        # Save the graph
        output_path = Path(output_path)
        dot.render(str(output_path.with_suffix("")), format=format, cleanup=True)

        return output_path.with_suffix(f".{format}")

    except Exception as e:
        print(f"Error generating pipeline graph: {str(e)}")
        return None


def create_timeline_plot(
    pipeline: Pipeline,
    output_path: Union[str, Path],
    format: str = "png",
    figsize: Tuple[float, float] = (10, 6),
    dpi: int = 100,
) -> Optional[Path]:
    """
    Create a timeline visualization using matplotlib.

    Args:
        pipeline: The Pipeline instance to visualize
        output_path: Path where the output image should be saved
        format: Output format (png, svg, pdf)
        figsize: Figure size in inches (width, height)
        dpi: Dots per inch for raster formats

    Returns:
        Optional[Path]: Path to the generated image file, or None if generation failed
    """
    try:
        # Create figure and axis
        fig, ax = plt.subplots(figsize=figsize)

        # Status colors
        colors = {
            "pending": "#808080",
            "running": "#FFA500",
            "completed": "#32CD32",
            "skipped": "#87CEEB",
            "failed": "#FF0000",
        }

        # Status icons
        icons = {
            "pending": "🔄",
            "running": "⚡",
            "completed": "✅",
            "skipped": "⏭️",
            "failed": "❌",
        }

        # Collect timeline data
        stages = []
        starts = []
        durations = []
        colors_list = []

        for stage_name, stage_info in pipeline.visualizer.viz_data.items():
            if stage_info.start_time and stage_info.end_time:
                stages.append(f"{icons.get(stage_info.status, '')} {stage_name}")
                starts.append(stage_info.start_time)
                duration = (stage_info.end_time - stage_info.start_time).total_seconds()
                durations.append(duration)
                colors_list.append(colors.get(stage_info.status, "#808080"))

        # Create timeline bars
        if stages:  # Only create plot if we have data
            # Plot bars
            ax.barh(range(len(stages)), durations, left=starts, color=colors_list)

            # Customize axis
            ax.set_yticks(range(len(stages)))
            ax.set_yticklabels(stages)

            # Format x-axis to show time
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
            plt.gcf().autofmt_xdate()

            # Add labels and title
            ax.set_xlabel("Time")
            ax.set_title("Pipeline Execution Timeline")

            # Add grid
            ax.grid(True, axis="x", linestyle="--", alpha=0.7)

            # Adjust layout
            plt.tight_layout()

            # Save plot
            output_path = Path(output_path)
            plt.savefig(output_path, format=format, dpi=dpi)
            plt.close()

            return output_path

        return None

    except Exception as e:
        print(f"Error generating timeline plot: {str(e)}")
        return None


def save_pipeline_visualization(
    pipeline: Pipeline,
    output_dir: Union[str, Path],
    base_name: str = "pipeline",
    format: str = "png",
) -> Tuple[Optional[Path], Optional[Path]]:
    """
    Save both the pipeline structure and timeline visualizations as image files.

    Args:
        pipeline: The Pipeline instance to visualize
        output_dir: Directory where the images should be saved
        base_name: Base name for the output files
        format: Output format (png, svg, pdf)

    Returns:
        Tuple[Optional[Path], Optional[Path]]: Paths to the structure and timeline images,
                                             or None if generation failed
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate structure diagram
    structure_path = output_dir / f"{base_name}_structure.{format}"
    structure_result = create_pipeline_graph(pipeline, structure_path, format)

    # Generate timeline diagram
    timeline_path = output_dir / f"{base_name}_timeline.{format}"
    timeline_result = create_timeline_plot(pipeline, timeline_path, format)

    return structure_result, timeline_result
