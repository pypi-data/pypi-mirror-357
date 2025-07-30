import asyncio
import random
from typing import Any, Dict

from pipetee.models.stage import StageResult
from pipetee.pipeline import Pipeline, PipelineStage


class DataGeneratorStage(PipelineStage[None, Dict[str, Any]]):
    """Generates sample data for processing"""

    async def process(self, _: None) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.5)
        data = {
            "records": [{"id": i, "value": random.randint(1, 100)} for i in range(10)],
            "batch_id": random.randint(1000, 9999),
        }
        return StageResult(success=True, data=data)


class ValidationStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    """Validates the data format and values"""

    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.3)

        if not isinstance(data.get("records"), list):
            return StageResult(
                success=False,
                data=None,
                error="Invalid data format: records must be a list",
            )

        data["validation_passed"] = True
        return StageResult(success=True, data=data)


class ProcessingStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    """Processes the records with potential failures"""

    def __init__(self, fail_probability: float = 0.3):
        super().__init__()
        self.fail_probability = fail_probability

    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.5)

        # Simulate random processing failure
        if random.random() < self.fail_probability:
            # Return the original data when failing to preserve state
            return StageResult(
                success=False,
                data=data,  # Keep the original data instead of None
                error="Random processing failure occurred",
            )

        # Process records
        processed_records = []
        for record in data["records"]:
            processed_records.append({**record, "processed_value": record["value"] * 2})

        data["records"] = processed_records
        data["processing_complete"] = True

        return StageResult(success=True, data=data)


class AggregationStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    """Aggregates the processed results"""

    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.4)

        total_value = sum(r["processed_value"] for r in data["records"])
        avg_value = total_value / len(data["records"])

        data["aggregated_results"] = {
            "total_value": total_value,
            "average_value": avg_value,
            "record_count": len(data["records"]),
        }

        return StageResult(success=True, data=data)


async def run_with_checkpoint_demo() -> None:
    """Demonstrates pipeline execution with checkpoint recovery"""
    pipeline = Pipeline()

    # Add stages
    pipeline.add_stage("generate", DataGeneratorStage())
    pipeline.add_stage("validate", ValidationStage())
    pipeline.add_stage("process", ProcessingStage())
    pipeline.add_stage("aggregate", AggregationStage())

    print("\n=== Starting Pipeline Execution ===")

    # First run - might fail during processing
    result = await pipeline.process(None)

    if not result.success:
        print(f"\nPipeline failed: {result.error}")
        print("Attempting to restore from last checkpoint...")

        # Get the last checkpoint ID from the .pipeline_checkpoints directory
        import os

        checkpoint_dir = ".pipeline_checkpoints"
        checkpoints = [f for f in os.listdir(checkpoint_dir) if f.endswith(".json")]
        if checkpoints:
            # Get the most recent checkpoint
            latest_checkpoint = sorted(checkpoints)[-1]
            checkpoint_id = latest_checkpoint.replace(".json", "")

            print(f"Found checkpoint: {checkpoint_id}")

            # Create a new pipeline with a more reliable processing stage
            restore_pipeline = Pipeline()
            restore_pipeline._checkpoint_dir = pipeline._checkpoint_dir

            # Add stages with a more reliable processing stage
            restore_pipeline.add_stage("generate", DataGeneratorStage())
            restore_pipeline.add_stage("validate", ValidationStage())
            restore_pipeline.add_stage(
                "process", ProcessingStage(fail_probability=0.1)
            )  # Lower failure probability
            restore_pipeline.add_stage("aggregate", AggregationStage())

            # Restore and continue from checkpoint
            restored_data = await restore_pipeline.restore_from_checkpoint(
                checkpoint_id
            )

            if restored_data is not None:
                print("\n=== Pipeline Restored Successfully ===")
                print(f"Final Results: {restored_data}")

                # Print pipeline visualization after successful restoration
                print("\nRestored Pipeline Execution Diagram:")
                print("```mermaid")
                print(restore_pipeline.visualizer.generate_mermaid_diagram())
                print("```")

                print("\nRestored Execution Timeline:")
                print("```mermaid")
                print(restore_pipeline.visualizer.generate_execution_timeline())
                print("```")
            else:
                print("\nFailed to restore from checkpoint")

                # Print failure visualization
                print("\nFailed Pipeline Execution Diagram:")
                print("```mermaid")
                print(pipeline.visualizer.generate_mermaid_diagram())
                print("```")
    else:
        print("\n=== Pipeline Completed Successfully ===")
        print(f"Final Results: {result.data}")

        # Print success visualization
        print("\nSuccessful Pipeline Execution Diagram:")
        print("```mermaid")
        print(pipeline.visualizer.generate_mermaid_diagram())
        print("```")

        print("\nExecution Timeline:")
        print("```mermaid")
        print(pipeline.visualizer.generate_execution_timeline())
        print("```")


if __name__ == "__main__":
    asyncio.run(run_with_checkpoint_demo())
