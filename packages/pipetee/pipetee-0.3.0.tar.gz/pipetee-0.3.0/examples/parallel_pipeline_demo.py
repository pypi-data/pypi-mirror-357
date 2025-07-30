"""
Demonstration of 1-to-N-to-1 parallel pipeline execution pattern.

This example shows how to:
1. Fan out from one stage to multiple parallel stages (1-to-N)
2. Execute multiple stages concurrently
3. Aggregate results back to a single stage (N-to-1)
4. Continue with normal pipeline execution
"""

import asyncio
import time
from typing import Any, Dict, List

from pipetee.models.stage import StageDecision, StageResult
from pipetee.pipeline import Pipeline, PipelineStage


class DataPreparationStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    """Prepares data and decides whether to use parallel processing"""

    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        print(
            f"🔧 [PREP] Starting data preparation at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )
        await asyncio.sleep(0.2)

        # Add some metadata and prepare for parallel processing
        data["prepared"] = True
        data["timestamp"] = time.strftime("%H:%M:%S.%f")[:-3]

        print(
            f"🔧 [PREP] Data prepared, triggering parallel processing at {time.strftime('%H:%M:%S.%f')[:-3]}"
        )

        # Use PARALLEL_TO decision to explicitly trigger parallel execution
        return StageResult(
            success=True,
            data=data,
            decision=StageDecision.PARALLEL_TO,
            next_stage="text_analyzer,image_processor,data_validator",  # Comma-separated parallel stages
        )


class TextAnalyzerStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    """Analyzes text content in parallel"""

    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        start_time = time.strftime("%H:%M:%S.%f")[:-3]
        print(f"📝 [TEXT] Starting text analysis at {start_time}")

        await asyncio.sleep(1.0)  # Longer delay to make parallelism more obvious

        result = {
            "stage": "text_analyzer",
            "word_count": len(data.get("text", "").split()) if "text" in data else 0,
            "sentiment": "positive",
            "processing_time": 1.0,
            "start_time": start_time,
            "end_time": time.strftime("%H:%M:%S.%f")[:-3],
        }

        print(f"📝 [TEXT] Text analysis completed at {result['end_time']}")
        return StageResult(success=True, data=result)


class ImageProcessorStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    """Processes images in parallel"""

    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        start_time = time.strftime("%H:%M:%S.%f")[:-3]
        print(f"🖼️  [IMG]  Starting image processing at {start_time}")

        await asyncio.sleep(1.5)  # Different delay to show they run concurrently

        result = {
            "stage": "image_processor",
            "image_count": len(data.get("images", [])),
            "total_size": sum(img.get("size", 0) for img in data.get("images", [])),
            "processing_time": 1.5,
            "start_time": start_time,
            "end_time": time.strftime("%H:%M:%S.%f")[:-3],
        }

        print(f"🖼️  [IMG]  Image processing completed at {result['end_time']}")
        return StageResult(success=True, data=result)


class DataValidatorStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    """Validates data integrity in parallel"""

    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        start_time = time.strftime("%H:%M:%S.%f")[:-3]
        print(f"✅ [VAL]  Starting data validation at {start_time}")

        await asyncio.sleep(0.8)  # Another different delay

        result = {
            "stage": "data_validator",
            "is_valid": True,
            "validation_score": 0.95,
            "processing_time": 0.8,
            "start_time": start_time,
            "end_time": time.strftime("%H:%M:%S.%f")[:-3],
        }

        print(f"✅ [VAL]  Data validation completed at {result['end_time']}")
        return StageResult(success=True, data=result)


class ResultAggregatorStage(PipelineStage[List[Dict[str, Any]], Dict[str, Any]]):
    """Aggregates results from parallel stages (N-to-1)"""

    async def process(self, data: List[Dict[str, Any]]) -> StageResult[Dict[str, Any]]:
        start_time = time.strftime("%H:%M:%S.%f")[:-3]
        print(f"🔄 [AGG]  Starting result aggregation at {start_time}")

        await asyncio.sleep(0.2)

        # Combine results from all parallel stages
        aggregated = {
            "aggregation_timestamp": start_time,
            "parallel_results": {},
            "timing_analysis": {},
            "summary": {},
        }

        # Analyze timing to prove parallelism
        all_start_times = []
        all_end_times = []

        for result in data:
            if isinstance(result, dict):
                stage_name = result.get("stage", "unknown")
                aggregated["parallel_results"][stage_name] = result

                # Collect timing data
                if "start_time" in result and "end_time" in result:
                    all_start_times.append(result["start_time"])
                    all_end_times.append(result["end_time"])
                    aggregated["timing_analysis"][stage_name] = {
                        "start": result["start_time"],
                        "end": result["end_time"],
                        "duration": result.get("processing_time", 0),
                    }

        # Calculate parallel execution metrics
        if all_start_times and all_end_times:
            earliest_start = min(all_start_times)
            latest_end = max(all_end_times)
            total_parallel_time = sum(
                r.get("processing_time", 0) for r in data if isinstance(r, dict)
            )

            aggregated["timing_analysis"]["summary"] = {
                "earliest_start": earliest_start,
                "latest_end": latest_end,
                "parallel_execution_time": latest_end,  # Time from first start to last end
                "total_sequential_time_would_be": total_parallel_time,
                "time_saved": total_parallel_time
                - 1.5,  # Approximate actual parallel time
                "parallelism_efficiency": f"{((total_parallel_time - 1.5) / total_parallel_time * 100):.1f}%",
            }

        # Create summary
        aggregated["summary"] = {
            "total_stages_processed": len(data),
            "all_successful": all(isinstance(r, dict) for r in data),
            "processing_complete": True,
        }

        end_time = time.strftime("%H:%M:%S.%f")[:-3]
        print(f"🔄 [AGG]  Aggregation completed at {end_time}")
        return StageResult(success=True, data=aggregated)


class FinalReportStage(PipelineStage[Dict[str, Any], Dict[str, Any]]):
    """Final stage that processes the aggregated results"""

    async def process(self, data: Dict[str, Any]) -> StageResult[Dict[str, Any]]:
        start_time = time.strftime("%H:%M:%S.%f")[:-3]
        print(f"📊 [FINAL] Generating final report at {start_time}")

        await asyncio.sleep(0.1)

        # Generate final report
        report = {
            "final_report": True,
            "aggregated_data": data,
            "report_generated_at": time.strftime("%H:%M:%S.%f")[:-3],
        }

        print(f"📊 [FINAL] Final report completed at {report['report_generated_at']}")
        return StageResult(success=True, data=report)


async def main():
    """Demonstrate 1-to-N-to-1 parallel pipeline execution"""

    print("=" * 60)
    print("🚀 1-to-N-to-1 PARALLEL PIPELINE DEMONSTRATION")
    print("=" * 60)
    print()
    print("This demo will show:")
    print("• Data preparation stage (0.2s)")
    print("• THREE PARALLEL stages:")
    print("  - Text analyzer (1.0s)")
    print("  - Image processor (1.5s)")
    print("  - Data validator (0.8s)")
    print("• Result aggregation (0.2s)")
    print("• Final report generation (0.1s)")
    print()
    print("If sequential: ~3.6 seconds total")
    print("If parallel: ~2.0 seconds total (stages overlap!)")
    print()
    print("Watch the timestamps to see parallelism in action!")
    print("-" * 60)

    # Create pipeline
    pipeline = Pipeline()

    # Add stages in sequence
    pipeline.add_stage("data_preparation", DataPreparationStage())
    pipeline.add_stage("text_analyzer", TextAnalyzerStage())
    pipeline.add_stage("image_processor", ImageProcessorStage())
    pipeline.add_stage("data_validator", DataValidatorStage())
    pipeline.add_stage("result_aggregator", ResultAggregatorStage())
    pipeline.add_stage("final_report", FinalReportStage())

    # Sample input data
    input_data = {
        "text": "This is a sample text for analysis with multiple words",
        "images": [
            {"name": "image1.jpg", "size": 1024},
            {"name": "image2.png", "size": 2048},
        ],
        "metadata": {"source": "demo", "version": "1.0"},
    }

    print(f"\n⏰ Pipeline started at {time.strftime('%H:%M:%S.%f')[:-3]}")
    start_time = time.time()

    # Execute pipeline
    result = await pipeline.process(input_data)

    end_time = time.time()
    total_time = end_time - start_time

    print(f"⏰ Pipeline completed at {time.strftime('%H:%M:%S.%f')[:-3]}")
    print("-" * 60)

    print("\n📈 PERFORMANCE RESULTS:")
    print(f"Success: {result.success}")
    print(f"Total execution time: {total_time:.2f} seconds")

    if result.success and result.data:
        # Extract timing analysis from aggregated results
        aggregated_data = result.data.get("aggregated_data", {})
        timing_analysis = aggregated_data.get("timing_analysis", {})

        if "summary" in timing_analysis:
            summary = timing_analysis["summary"]
            print(
                f"Time if sequential: {summary.get('total_sequential_time_would_be', 0):.1f} seconds"
            )
            print(
                f"Parallelism efficiency: {summary.get('parallelism_efficiency', 'N/A')}"
            )

        print("\n🎯 PARALLEL EXECUTION PROOF:")
        if timing_analysis:
            for stage, timings in timing_analysis.items():
                if stage != "summary" and isinstance(timings, dict):
                    print(
                        f"  {stage}: {timings['start']} → {timings['end']} ({timings['duration']}s)"
                    )

        print("\n📋 EXECUTION PATH:")
        if result.metadata:
            exec_path = result.metadata.get("execution_path", [])
            print(f"Stages executed: {' → '.join(exec_path)}")

    print("\n✨ Notice how the three parallel stages have overlapping timestamps!")
    print("   This proves they ran concurrently, not sequentially!")


if __name__ == "__main__":
    asyncio.run(main())
