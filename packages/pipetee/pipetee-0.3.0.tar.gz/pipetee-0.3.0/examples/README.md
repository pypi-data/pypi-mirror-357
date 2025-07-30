# Pipeline-Tee Examples

This directory contains example pipelines demonstrating various features of Pipeline-Tee.

## Examples Overview

### 1. Parallel Pipeline Demo (`parallel_pipeline_demo.py`) ✨ NEW

Demonstrates the **1-to-N-to-1 parallel execution pattern** with true concurrent processing:

- **1-to-N (Fan Out)**: Single stage triggers multiple parallel stages
- **N (Parallel Processing)**: Stages execute concurrently using `asyncio.gather()`
- **N-to-1 (Aggregation)**: Results collected and combined into next stage
- **Performance Benefits**: ~40% faster execution through parallelism

Pipeline flow:
```
Data Preparation → [Text Analyzer + Image Processor + Data Validator] → Result Aggregator → Final Report
                   ↑ These 3 stages run in parallel ↑
```

Key features:
- Real-time timing analysis with millisecond precision
- Parallelism efficiency metrics
- Visual proof of concurrent execution through overlapping timestamps
- Performance comparison (sequential vs parallel execution times)

### 2. Mixed Parallel & Sequential Demo (`mixed_parallel_demo.py`) ✨ NEW

Shows how to combine **selective parallelism** with sequential processing in a single pipeline:

- **Sequential stages** for setup, aggregation, and dependencies
- **Multiple parallel groups** separated by sequential stages
- **Conditional parallel execution** based on data or logic
- **Real-world workflow patterns**

Pipeline flow:
```
Init → Analysis → [Group1: Text+Image+Cleaner] → Aggregation → Middle → [Group2: Validator+Optimizer] → Final
       ↑ Sequential ↑        ↑ Parallel ↑         ↑ Sequential ↑        ↑ Parallel ↑        ↑ Sequential ↑
```

Benefits:
- **Optimal resource usage**: Parallelism only where beneficial
- **Dependency management**: Sequential stages ensure proper data flow
- **Flexibility**: Mix and match parallel/sequential as needed
- **Performance**: ~30% faster than fully sequential execution

### 3. Visualization Demo (`visualization_demo.py`)

Demonstrates the pipeline visualization features with a data processing pipeline that includes:

- Branching based on data values
- Conditional execution
- Different processing paths
- Timeline visualization
- Multiple output formats (PNG, SVG, PDF)

### 4. Complex Pipeline Demo (`complex_pipeline_demo.py`)

Shows how to build complex data processing pipelines with:

- Multiple processing stages
- Conditional branching
- Error handling
- State tracking

### 5. Complex Branching Pipeline (`complex_branching_pipeline.py`)

Demonstrates advanced flow control features:

- Multiple branch conditions
- Skip conditions
- Dynamic path selection

## Parallel Execution Features

Pipeline-Tee now supports **true concurrent execution** with two main patterns:

### 1-to-N-to-1 Pattern (Fan Out/Fan In)
```python
# Stage that triggers parallel execution
return StageResult(
    success=True,
    data=data,
    decision=StageDecision.PARALLEL_TO,
    next_stage="stage_a,stage_b,stage_c"  # Comma-separated parallel stages
)
```

### Selective Parallelism
- **Default**: All stages run sequentially
- **Opt-in**: Only specified stages run in parallel
- **Controlled**: Use conditions to decide when to parallelize
- **Mixed**: Combine parallel groups with sequential stages

### Performance Benefits
- **Concurrent I/O**: Database calls, API requests, file operations
- **CPU-intensive tasks**: Data processing, analysis, transformations
- **Independent operations**: Text analysis + image processing + validation
- **Real performance gains**: 30-50% faster execution in typical scenarios

## Requirements

1. **Python Dependencies**:

```bash
# Core package with development tools
pip install -e ".[dev]"

# Visualization dependencies (matplotlib, graphviz)
pip install -e ".[viz]"
```

2. **System Dependencies**:

- **Graphviz** (required for pipeline structure diagrams):
  ```bash
  # macOS
  brew install graphviz

  # Linux (Ubuntu/Debian)
  sudo apt-get install graphviz

  # Windows
  choco install graphviz
  ```
- **Python 3.8+**
- **pip** (for package installation)

## Running the Examples

After installing all dependencies, you can run any example:

```bash
# Parallel execution demos (NEW!)
python examples/parallel_pipeline_demo.py
python examples/mixed_parallel_demo.py

# Original demos
python examples/visualization_demo.py
python examples/complex_pipeline_demo.py
python examples/complex_branching_pipeline.py
```

## Example Pipeline Structures

### Sequential Pipeline (Traditional)
```
generate_data → validate → [high_value_processing or low_value_processing] → enrich → export
```

### Parallel Pipeline (NEW!)
```
data_prep → [text_analyzer + image_processor + data_validator] → aggregator → final_report
            ↑ Parallel execution (concurrent) ↑
```

### Mixed Pipeline (NEW!)
```
init → analysis → [text + image + cleaner] → agg1 → middle → [validator + optimizer] → agg2 → final
       ↑ Sequential ↑  ↑ Parallel Group 1 ↑  ↑ Sequential ↑  ↑ Parallel Group 2 ↑  ↑ Sequential ↑
```

## Parallel Execution Use Cases

### When to Use Parallel Stages:
- ✅ **Independent processing tasks** (text + image + data analysis)
- ✅ **I/O-bound operations** (API calls, database queries, file operations)
- ✅ **CPU-intensive computations** that can run concurrently
- ✅ **Different transformations** on the same input data
- ✅ **Time-sensitive workflows** where speed matters

### When to Keep Sequential:
- ⚠️  **Dependencies** (Stage B needs Stage A's output)
- ⚠️  **Resource constraints** (limited CPU/memory)
- ⚠️  **Shared state modifications** (database updates, file writes)
- ⚠️  **Setup/teardown operations** (initialization, cleanup)
- ⚠️  **Lightweight tasks** (no performance benefit from parallelism)

## Visualization Features

The demo showcases two types of visualizations:

1. **Pipeline Structure** (using Graphviz):
   - Shows all stages and their connections
   - Color-coded nodes based on stage status:
     - 🔄 Gray: Pending
     - ⚡ Orange: Running
     - ✅ Green: Completed
     - ⏭️ Light Blue: Skipped
     - ❌ Red: Failed
   - Solid lines for default sequence
   - Dashed lines for conditional branches
   - **NEW**: Parallel execution groups clearly marked
   - Requires system Graphviz installation

2. **Execution Timeline** (using Matplotlib):
   - Shows when each stage started and ended
   - Color-coded bars for stage status
   - Duration of each stage
   - Status icons and stage names
   - Time-based axis
   - **NEW**: Overlapping bars show parallel execution

## Performance Analysis

The parallel demos include built-in performance analysis:

- **Execution time comparison** (sequential vs parallel)
- **Parallelism efficiency metrics**
- **Time savings calculations**
- **Overlapping timestamp analysis**
- **Resource utilization insights**

Example output:
```
📈 PERFORMANCE RESULTS:
Success: True
Total execution time: 2.01 seconds
Time if sequential: 3.3 seconds
Parallelism efficiency: 54.5%
Time saved: 1.29 seconds (39% faster!)
```

## Troubleshooting

1. **Structure diagram not generating** (`failed to execute PosixPath('dot')`):
   - This means the system Graphviz executables are not installed or not in PATH
   - Install Graphviz using the commands above for your OS
   - Verify installation with `dot -V`

2. **Missing status icons** in timeline:
   - This is a font issue and doesn't affect functionality
   - The timeline will still show stage status through color coding

3. **Parallel stages not running concurrently**:
   - Check that you're using `StageDecision.PARALLEL_TO` correctly
   - Ensure stages are specified with comma-separated names
   - Verify asyncio event loop is running (use `asyncio.run()`)

4. **Poor parallel performance**:
   - Parallel overhead may exceed benefits for very fast stages (<100ms)
   - Consider grouping small operations or using sequential execution
   - Profile your specific use case to find optimal parallelization points
