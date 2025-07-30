"""
Demonstration of MIXED parallel and sequential pipeline execution.

This example shows how to:
1. Have some stages run sequentially
2. Have some stages run in parallel
3. Return to sequential execution
4. Have multiple parallel groups in one pipeline
"""

import asyncio
import time
from typing import Any, Dict, List

from pipetee.models.stage import StageDecision, StageResult
from pipetee.pipeline import Pipeline, PipelineStage


class InitialProcessingStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    """Sequential stage - processes data normally"""

    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        print(f"🔧 [INIT] Sequential processing at {time.strftime('%H:%M:%S.%f')[:-3]}")
        await asyncio.sleep(0.3)

        data["initial_processed"] = True
        data["stage_count"] = 1

        print(
            f"🔧 [INIT] Sequential processing completed at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        return StageResult(success=True, data=data)


class DataAnalysisStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    """Sequential stage that decides whether to use parallel processing"""

    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        print(f"📊 [ANALYSIS] Analyzing data at {time.strftime('%H:%M:%S.%f')[:-3]}")
        await asyncio.sleep(0.2)

        data["analysis_complete"] = True
        data["stage_count"] += 1

        # Decide to use parallel processing for data processing tasks
        print(
            f"📊 [ANALYSIS] Triggering PARALLEL processing group 1 at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )

        return StageResult(
            success=True,
            data=data,
            decision=StageDecision.PARALLEL_TO,
            next_stage="text_processor,image_enhancer,data_cleaner",  # PARALLEL GROUP 1
        )


# PARALLEL GROUP 1 - Data Processing Tasks
class TextProcessorStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        print(
            f"📝 [TEXT-P1] Starting parallel text processing at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        await asyncio.sleep(0.8)

        result = {
            "stage": "text_processor",
            "processing_time": 0.8,
            "parallel_group": 1,
            "processed_words": 100,
            "start_time": time.strftime("%H:%M:%S.%f")[:-3],
        }

        print(
            f"📝 [TEXT-P1] Parallel text processing completed at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        return StageResult(success=True, data=result)


class ImageEnhancerStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        print(
            f"🖼️  [IMG-P1] Starting parallel image enhancement at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        await asyncio.sleep(1.2)

        result = {
            "stage": "image_enhancer",
            "processing_time": 1.2,
            "parallel_group": 1,
            "enhanced_images": 5,
            "start_time": time.strftime("%H:%M:%S.%f")[:-3],
        }

        print(
            f"🖼️  [IMG-P1] Parallel image enhancement completed at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        return StageResult(success=True, data=result)


class DataCleanerStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        print(
            f"🧹 [CLEAN-P1] Starting parallel data cleaning at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        await asyncio.sleep(0.6)

        result = {
            "stage": "data_cleaner",
            "processing_time": 0.6,
            "parallel_group": 1,
            "cleaned_records": 1000,
            "start_time": time.strftime("%H:%M:%S.%f")[:-3],
        }

        print(
            f"🧹 [CLEAN-P1] Parallel data cleaning completed at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        return StageResult(success=True, data=result)


class FirstAggregatorStage(PipelineStage[List[Dict[str, Any]], Dict[str, Any]]):
    """Sequential stage - aggregates results from parallel group 1"""

    async def process(self, data: List[Dict[str, Any]]) -> StageResult[Dict[str, Any]]:
        print(
            f"🔄 [AGG1] Sequential aggregation of group 1 at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        await asyncio.sleep(0.2)

        aggregated = {
            "group_1_results": {item["stage"]: item for item in data},
            "group_1_summary": f"Processed {len(data)} parallel tasks",
            "ready_for_next_phase": True,
        }

        print(
            f"🔄 [AGG1] Sequential aggregation completed at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        return StageResult(success=True, data=aggregated)


class MiddleProcessingStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    """Sequential stage - processes aggregated data and decides on second parallel group"""

    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        print(
            f"⚙️  [MIDDLE] Sequential middle processing at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        await asyncio.sleep(0.4)

        data["middle_processed"] = True
        data["ready_for_group_2"] = True

        print(
            f"⚙️  [MIDDLE] Triggering PARALLEL processing group 2 at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )

        return StageResult(
            success=True,
            data=data,
            decision=StageDecision.PARALLEL_TO,
            next_stage="validator,optimizer",  # PARALLEL GROUP 2 (smaller group)
        )


# PARALLEL GROUP 2 - Validation and Optimization
class ValidatorStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        print(
            f"✅ [VAL-P2] Starting parallel validation at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        await asyncio.sleep(0.7)

        result = {
            "stage": "validator",
            "processing_time": 0.7,
            "parallel_group": 2,
            "validation_score": 0.95,
            "start_time": time.strftime("%H:%M:%S.%f")[:-3],
        }

        print(
            f"✅ [VAL-P2] Parallel validation completed at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        return StageResult(success=True, data=result)


class OptimizerStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        print(
            f"⚡ [OPT-P2] Starting parallel optimization at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        await asyncio.sleep(1.0)

        result = {
            "stage": "optimizer",
            "processing_time": 1.0,
            "parallel_group": 2,
            "optimization_gain": "25%",
            "start_time": time.strftime("%H:%M:%S.%f")[:-3],
        }

        print(
            f"⚡ [OPT-P2] Parallel optimization completed at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        return StageResult(success=True, data=result)


class FinalAggregatorStage(PipelineStage[List[Dict[str, Any]], Dict[str, Any]]):
    """Sequential stage - aggregates results from parallel group 2"""

    async def process(self, data: List[Dict[str, Any]]) -> StageResult[Dict[str, Any]]:
        print(
            f"🔄 [AGG2] Sequential aggregation of group 2 at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        await asyncio.sleep(0.2)

        aggregated = {
            "group_2_results": {item["stage"]: item for item in data},
            "group_2_summary": f"Validated and optimized {len(data)} components",
            "final_processing_ready": True,
        }

        print(
            f"🔄 [AGG2] Sequential aggregation completed at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        return StageResult(success=True, data=aggregated)


class FinalStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    """Sequential stage - final processing"""

    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        print(
            f"🏁 [FINAL] Sequential final processing at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        await asyncio.sleep(0.3)

        final_result = {
            "pipeline_complete": True,
            "total_parallel_groups": 2,
            "all_data": data,
            "completion_time": time.strftime("%H:%M:%S.%f")[:-3],
        }

        print(
            f"🏁 [FINAL] Sequential final processing completed at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        return StageResult(success=True, data=final_result)


async def main():
    """Demonstrate mixed parallel and sequential execution"""

    print("=" * 70)
    print("🔀 MIXED PARALLEL & SEQUENTIAL PIPELINE DEMONSTRATION")
    print("=" * 70)
    print()
    print("Pipeline Flow:")
    print("📋 Sequential: Initial Processing (0.3s)")
    print("📋 Sequential: Data Analysis (0.2s)")
    print("🔄 PARALLEL GROUP 1: Text(0.8s) + Image(1.2s) + Cleaner(0.6s)")
    print("📋 Sequential: First Aggregation (0.2s)")
    print("📋 Sequential: Middle Processing (0.4s)")
    print("🔄 PARALLEL GROUP 2: Validator(0.7s) + Optimizer(1.0s)")
    print("📋 Sequential: Final Aggregation (0.2s)")
    print("📋 Sequential: Final Processing (0.3s)")
    print()
    print("Expected behavior:")
    print("• Sequential stages run one after another")
    print("• Parallel groups run concurrently within the group")
    print("• Different parallel groups are separated by sequential stages")
    print()
    print("If ALL sequential: ~4.9 seconds")
    print("With selective parallelism: ~3.5 seconds")
    print("-" * 70)

    # Create pipeline
    pipeline = Pipeline()

    # Add stages in sequence (order matters for default sequence)
    pipeline.add_stage("initial_processing", InitialProcessingStage())
    pipeline.add_stage("data_analysis", DataAnalysisStage())

    # Parallel Group 1
    pipeline.add_stage("text_processor", TextProcessorStage())
    pipeline.add_stage("image_enhancer", ImageEnhancerStage())
    pipeline.add_stage("data_cleaner", DataCleanerStage())

    # Sequential stages
    pipeline.add_stage("first_aggregator", FirstAggregatorStage())
    pipeline.add_stage("middle_processing", MiddleProcessingStage())

    # Parallel Group 2
    pipeline.add_stage("validator", ValidatorStage())
    pipeline.add_stage("optimizer", OptimizerStage())

    # Final sequential stages
    pipeline.add_stage("final_aggregator", FinalAggregatorStage())
    pipeline.add_stage("final_stage", FinalStage())

    # Sample input data
    input_data = {
        "task_id": "mixed_demo_001",
        "data_size": "large",
        "processing_mode": "mixed",
    }

    print(f"\n⏰ Mixed pipeline started at {time.strftime('%H:%M:%S.%f')[:-3]}")
    start_time = time.time()

    # Execute pipeline
    result = await pipeline.process(input_data)

    end_time = time.time()
    total_time = end_time - start_time

    print(f"⏰ Mixed pipeline completed at {time.strftime('%H:%M:%S.%f')[:-3]}")
    print("-" * 70)

    print("\n📈 MIXED EXECUTION RESULTS:")
    print(f"Success: {result.success}")
    print(f"Total execution time: {total_time:.2f} seconds")

    if result.metadata:
        print("\n📋 EXECUTION PATH:")
        exec_path = result.metadata.get("execution_path", [])
        print(f"Stages executed: {' → '.join(exec_path)}")

    print("\n🔍 PARALLELISM ANALYSIS:")
    print(
        "✅ Sequential stages: initial_processing, data_analysis, first_aggregator, middle_processing, final_aggregator, final_stage"
    )
    print("🔄 Parallel Group 1: text_processor, image_enhancer, data_cleaner")
    print("🔄 Parallel Group 2: validator, optimizer")
    print()
    print("💡 Key Point: Only specified stages run in parallel!")
    print("   The rest maintain sequential execution order.")


if __name__ == "__main__":
    asyncio.run(main())
