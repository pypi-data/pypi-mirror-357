import asyncio
import random
from datetime import datetime
from typing import Any, Dict

from pipetee.models.stage import StageResult
from pipetee.pipeline import Condition, Pipeline, PipelineStage


class DataSourceStage(PipelineStage[None, Dict[str, Any]]):
    async def process(self, _: None) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.3)
        # Generate more robust test data
        data_types: Dict[str, Dict[str, Any]] = {
            "text": {
                "type": "text",
                "content": "Sample text data for processing",
                "length": 28,
                "metadata": {"source": "test_generator"},
            },
            "image": {
                "type": "image",
                "dimensions": [800, 600],
                "format": "jpeg",
                "metadata": {"source": "test_generator"},
            },
            "numeric": {
                "type": "numeric",
                "values": [1.5, 2.7, 3.2, 4.1, 5.8],
                "stats": {"mean": 3.46, "count": 5},
                "metadata": {"source": "test_generator"},
            },
        }

        selected_type = random.choice(list(data_types.keys()))
        result_data = data_types[
            selected_type
        ].copy()  # Make a copy to avoid shared references

        print(
            f"DataSource generated: {selected_type} data with content: {result_data}"
        )  # Debug log
        return StageResult[Dict[str, Any]](success=True, data=result_data)


class DataClassifier(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.2)

        print(f"Classifier received data type: {type(data)}")  # Debug log
        print(f"Classifier received data content: {data}")  # Debug log

        # Validate input data
        if not isinstance(data, dict):
            return StageResult[Dict[str, Any]](
                success=False,
                data=None,
                error=f"Invalid input type: expected dict, got {type(data)}",
            )

        data_type = data.get("type")
        if not data_type:
            return StageResult[Dict[str, Any]](
                success=False, data=None, error=f"Missing 'type' field in data: {data}"
            )

        # Add classification metadata
        data["classified"] = True
        data["classification_timestamp"] = str(datetime.now())
        print(f"Classifier processed data type: {data_type}")  # Debug log

        return StageResult[Dict[str, Any]](success=True, data=data)


class TextProcessor(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.4)
        print(f"TextProcessor processing: {data}")  # Debug log
        data["text_processed"] = True
        return StageResult[Dict[str, Any]](success=True, data=data)


class ImageProcessor(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.3)
        print(f"ImageProcessor processing: {data}")  # Debug log
        data["image_processed"] = True
        return StageResult[Dict[str, Any]](success=True, data=data)


class NumericProcessor(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.2)
        print(f"NumericProcessor processing: {data}")  # Debug log
        data["numeric_processed"] = True
        return StageResult[Dict[str, Any]](success=True, data=data)


# Terminal stages for different paths
class LongTextHandler(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.2)
        print(f"LongTextHandler processing: {data}")  # Debug log
        data["processed"] = "long_text_processed"
        return StageResult[Dict[str, Any]](success=True, data=data)


class ShortTextHandler(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.1)
        print(f"ShortTextHandler processing: {data}")  # Debug log
        data["processed"] = "short_text_processed"
        return StageResult[Dict[str, Any]](success=True, data=data)


class ImageCompression(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.4)
        print(f"ImageCompression processing: {data}")  # Debug log
        data["processed"] = "image_compressed"
        return StageResult[Dict[str, Any]](success=True, data=data)


class DirectStorage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.2)
        print(f"DirectStorage processing: {data}")  # Debug log
        data["processed"] = "direct_stored"
        return StageResult[Dict[str, Any]](success=True, data=data)


class HighValueAnalytics(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.3)
        print(f"HighValueAnalytics processing: {data}")  # Debug log
        data["processed"] = "high_value_analyzed"
        return StageResult[Dict[str, Any]](success=True, data=data)


class LowValueAnalytics(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        await asyncio.sleep(0.2)
        print(f"LowValueAnalytics processing: {data}")  # Debug log
        data["processed"] = "low_value_analyzed"
        return StageResult[Dict[str, Any]](success=True, data=data)


async def main() -> None:
    # Create pipeline with debug logging
    pipeline = Pipeline()

    print("Initializing pipeline stages...")

    # Add stages with proper branching configuration
    pipeline.add_stage("classifier", DataClassifier())

    # Text processing branch
    pipeline.add_stage("text_processor", TextProcessor())
    pipeline.add_stage("long_text_handler", LongTextHandler())
    pipeline.add_stage("short_text_handler", ShortTextHandler())

    # Image processing branch
    pipeline.add_stage("image_processor", ImageProcessor())
    pipeline.add_stage("image_compression", ImageCompression())
    pipeline.add_stage("direct_storage", DirectStorage())

    # Numeric processing branch
    pipeline.add_stage("numeric_processor", NumericProcessor())
    pipeline.add_stage("high_value_analytics", HighValueAnalytics())
    pipeline.add_stage("low_value_analytics", LowValueAnalytics())

    # Configure branching paths from classifier
    classifier = pipeline.stages["classifier"]
    classifier.add_branch_condition(
        Condition("is_text", lambda data: data["type"] == "text"), "text_processor"
    )
    classifier.add_branch_condition(
        Condition("is_image", lambda data: data["type"] == "image"), "image_processor"
    )
    classifier.add_branch_condition(
        Condition("is_numeric", lambda data: data["type"] == "numeric"),
        "numeric_processor",
    )

    # Configure type-specific branching paths
    text_processor = pipeline.stages["text_processor"]
    text_processor.add_branch_condition(
        Condition("is_long_text", lambda data: len(data["content"]) > 10),
        "long_text_handler",
    )
    text_processor.add_branch_condition(
        Condition("is_short_text", lambda data: len(data["content"]) <= 10),
        "short_text_handler",
    )

    image_processor = pipeline.stages["image_processor"]
    image_processor.add_branch_condition(
        Condition(
            "is_large_image",
            lambda data: data["dimensions"][0] * data["dimensions"][1] > 600_000,
        ),
        "image_compression",
    )
    image_processor.add_branch_condition(
        Condition(
            "is_small_image",
            lambda data: data["dimensions"][0] * data["dimensions"][1] <= 600_000,
        ),
        "direct_storage",
    )

    numeric_processor = pipeline.stages["numeric_processor"]
    numeric_processor.add_branch_condition(
        Condition("is_high_value", lambda data: data["stats"]["mean"] > 2.5),
        "high_value_analytics",
    )
    numeric_processor.add_branch_condition(
        Condition("is_low_value", lambda data: data["stats"]["mean"] <= 2.5),
        "low_value_analytics",
    )

    print("Pipeline initialized. Starting processing...")

    # Sample input data for different scenarios
    test_inputs = [
        {
            "type": "text",
            "content": "Sample text data for processing",
            "metadata": {"source": "manual_input"},
        },
        {
            "type": "image",
            "dimensions": [1024, 768],
            "format": "png",
            "metadata": {"source": "manual_input"},
        },
        {
            "type": "numeric",
            "values": [2.1, 3.4, 4.2],
            "stats": {"mean": 3.2, "count": 3},
            "metadata": {"source": "manual_input"},
        },
    ]

    # Run pipeline with different input data
    for i, input_data in enumerate(test_inputs):
        print(f"\nPipeline Run #{i + 1}")
        print("-" * 50)
        print(f"Input data: {input_data}")
        result = await pipeline.process(input_data)

        if not result.success:
            print(f"Pipeline run failed: {result.error}")
        else:
            print(f"Pipeline run succeeded. Final data: {result.data}")

        print("\nMermaid Diagram:")
        print("```mermaid")
        print(pipeline.visualizer.generate_mermaid_diagram())
        print("```")

        print("\nExecution Timeline:")
        print("```mermaid")
        print(pipeline.visualizer.generate_execution_timeline())
        print("```")

        # Clear visualizer for next run
        pipeline.visualizer.reset()
        await asyncio.sleep(1)  # Pause between runs


if __name__ == "__main__":
    asyncio.run(main())
