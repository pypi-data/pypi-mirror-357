import asyncio
from typing import Any, Dict

from pipetee.models.stage import StageDecision, StageResult
from pipetee.pipeline import Condition, Pipeline, PipelineStage


# Example stages that simulate different data processing steps
class DataLoadStage(PipelineStage[None, Dict[str, Any]]):
    async def process(self, data: None) -> StageResult[Dict[str, Any]]:
        # Simulate loading data
        await asyncio.sleep(0.5)
        return StageResult(
            success=True,
            data={"raw_data": [1, 2, 3, 4, 5], "metadata": {"source": "demo"}},
        )


class ValidationStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.3)
        if not data.get("raw_data"):
            return StageResult(success=False, data=None, error="No raw data found")
        data["is_valid"] = True
        return StageResult(success=True, data=data)


class EnrichmentStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.4)
        data["enriched"] = [x * 2 for x in data["raw_data"]]
        return StageResult(success=True, data=data)


class TransformationStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.3)
        data["transformed"] = sum(data["enriched"])
        return StageResult(
            success=True,
            data=data,
            decision=StageDecision.BRANCH_TO,
            next_stage=(
                "high_value_processing"
                if data["transformed"] > 20
                else "low_value_processing"
            ),
        )


class HighValueProcessing(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.5)
        data["priority"] = "high"
        return StageResult(success=True, data=data)


class LowValueProcessing(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.2)
        data["priority"] = "low"
        return StageResult(success=True, data=data)


class ExportStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.3)
        return StageResult(success=True, data=data)


async def main() -> None:
    # Create pipeline
    pipeline = Pipeline()

    # Define conditions
    has_errors = Condition(
        "has_errors", lambda data: isinstance(data, dict) and "error" in data
    )

    # Add stages with conditions
    pipeline.add_stage("load_data", DataLoadStage())

    validation = ValidationStage()
    validation.add_skip_condition(has_errors)
    pipeline.add_stage("validate", validation)

    enrichment = EnrichmentStage()
    enrichment.add_skip_condition(has_errors)
    pipeline.add_stage("enrich", enrichment)

    transform = TransformationStage()
    pipeline.add_stage("transform", transform)

    pipeline.add_stage("high_value_processing", HighValueProcessing())
    pipeline.add_stage("low_value_processing", LowValueProcessing())
    pipeline.add_stage("export", ExportStage())

    # Run pipeline
    await pipeline.process(None)

    # Generate and print Mermaid diagram
    print("\nMermaid Diagram:")
    print("```mermaid")
    print(pipeline.visualizer.generate_mermaid_diagram())
    print("```")

    print("\nExecution Timeline:")
    print("```mermaid")
    print(pipeline.visualizer.generate_execution_timeline())
    print("```")


if __name__ == "__main__":
    asyncio.run(main())
