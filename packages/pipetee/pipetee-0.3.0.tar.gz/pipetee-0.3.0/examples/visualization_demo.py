"""
Example demonstrating pipeline visualization features.
"""

import asyncio
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from pipetee.models.stage import StageDecision, StageResult
from pipetee.pipeline import Condition, Pipeline, PipelineStage
from pipetee.utils.visualization import save_pipeline_visualization


class DataGeneratorStage(PipelineStage[None, List[Dict[str, Any]]]):
    """Generates sample data for processing."""

    async def process(self, _: None) -> StageResult[List[Dict[str, Any]]]:
        await asyncio.sleep(0.5)  # Simulate work
        data = [
            {
                "id": i,
                "value": random.randint(1, 100),
                "timestamp": datetime.now().isoformat(),
            }
            for i in range(10)
        ]
        return StageResult(success=True, data=data)


class ValidationStage(PipelineStage[List[Dict[str, Any]], List[Dict[str, Any]]]):
    """Validates data and may trigger different processing paths."""

    async def process(
        self, data: List[Dict[str, Any]]
    ) -> StageResult[List[Dict[str, Any]]]:
        await asyncio.sleep(0.3)

        # Calculate average value
        avg_value = sum(item["value"] for item in data) / len(data)

        # Decide processing path based on average value
        if avg_value > 50:
            return StageResult(
                success=True,
                data=data,
                decision=StageDecision.BRANCH_TO,
                next_stage="high_value_processing",
            )
        return StageResult(
            success=True,
            data=data,
            decision=StageDecision.BRANCH_TO,
            next_stage="low_value_processing",
        )


class HighValueProcessing(PipelineStage[List[Dict[str, Any]], List[Dict[str, Any]]]):
    """Processes high-value data with extra steps."""

    async def process(
        self, data: List[Dict[str, Any]]
    ) -> StageResult[List[Dict[str, Any]]]:
        await asyncio.sleep(0.8)  # More intensive processing

        # Add premium processing flag
        processed_data = [
            {**item, "processing_type": "premium", "priority": "high"} for item in data
        ]

        return StageResult(success=True, data=processed_data)


class LowValueProcessing(PipelineStage[List[Dict[str, Any]], List[Dict[str, Any]]]):
    """Processes low-value data with standard steps."""

    async def process(
        self, data: List[Dict[str, Any]]
    ) -> StageResult[List[Dict[str, Any]]]:
        await asyncio.sleep(0.4)  # Standard processing

        # Add standard processing flag
        processed_data = [
            {**item, "processing_type": "standard", "priority": "normal"}
            for item in data
        ]

        return StageResult(success=True, data=processed_data)


class EnrichmentStage(PipelineStage[List[Dict[str, Any]], List[Dict[str, Any]]]):
    """Enriches data with additional information."""

    async def process(
        self, data: List[Dict[str, Any]]
    ) -> StageResult[List[Dict[str, Any]]]:
        await asyncio.sleep(0.6)

        # Add enrichment data
        enriched_data = [
            {
                **item,
                "enriched": True,
                "score": item["value"] * 1.5,
                "processed_at": datetime.now().isoformat(),
            }
            for item in data
        ]

        return StageResult(success=True, data=enriched_data)


class ExportStage(PipelineStage[List[Dict[str, Any]], List[Dict[str, Any]]]):
    """Exports processed data."""

    async def process(
        self, data: List[Dict[str, Any]]
    ) -> StageResult[List[Dict[str, Any]]]:
        await asyncio.sleep(0.3)

        # Simulate export
        print(f"Exporting {len(data)} records...")
        for item in data:
            print(
                f"- ID: {item['id']}, Value: {item['value']}, "
                f"Type: {item['processing_type']}"
            )

        return StageResult(success=True, data=data)


async def run_visualization_demo() -> None:
    """Run the pipeline and generate visualizations."""
    # Create pipeline
    pipeline = Pipeline()

    # Add stages
    pipeline.add_stage("generate_data", DataGeneratorStage())
    pipeline.add_stage("validate", ValidationStage())
    pipeline.add_stage("high_value_processing", HighValueProcessing())
    pipeline.add_stage("low_value_processing", LowValueProcessing())
    pipeline.add_stage("enrich", EnrichmentStage())
    pipeline.add_stage("export", ExportStage())

    # Add conditions
    has_errors = Condition(
        "has_errors", lambda data: any(item["value"] < 0 for item in data)
    )

    # Add skip conditions
    pipeline.stages["enrich"].add_skip_condition(has_errors)

    print("Running pipeline with visualization...")
    result = await pipeline.process(None)

    if result.success:
        print("\nPipeline completed successfully!")

        # Create visualization directory
        viz_dir = Path("pipeline_visualizations")

        # Save PNG versions
        png_structure, png_timeline = save_pipeline_visualization(
            pipeline, viz_dir, "demo_pipeline_png", format="png"
        )
        print("\nPNG Visualizations:")
        print(f"- Structure: {png_structure}")
        print(f"- Timeline: {png_timeline}")

        # Save SVG versions (better for documentation)
        svg_structure, svg_timeline = save_pipeline_visualization(
            pipeline, viz_dir, "demo_pipeline_svg", format="svg"
        )
        print("\nSVG Visualizations:")
        print(f"- Structure: {svg_structure}")
        print(f"- Timeline: {svg_timeline}")

        # Save PDF versions (good for printing)
        pdf_structure, pdf_timeline = save_pipeline_visualization(
            pipeline, viz_dir, "demo_pipeline_pdf", format="pdf"
        )
        print("\nPDF Visualizations:")
        print(f"- Structure: {pdf_structure}")
        print(f"- Timeline: {pdf_timeline}")
    else:
        print(f"Pipeline failed: {result.error}")


if __name__ == "__main__":
    asyncio.run(run_visualization_demo())
