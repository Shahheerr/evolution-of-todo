# Tracing

Built-in tracing for debugging and monitoring agent execution.

## Basic Tracing

```python
from agents import Agent, Runner, enable_tracing

# Enable tracing globally
enable_tracing()

agent = Agent(name="Test", instructions="Be helpful.")
result = Runner.run_sync(agent, "Hello")

# Traces are automatically recorded
```

## Trace Configuration

```python
from agents import enable_tracing, disable_tracing

# Enable with options
enable_tracing(
    project_name="my-project",
    log_level="debug"  # debug, info, warning, error
)

# Run agents...

# Disable tracing
disable_tracing()
```

## Accessing Traces

```python
from agents import Agent, Runner

agent = Agent(name="Test", instructions="...")
result = Runner.run_sync(agent, "Hello")

# Access trace from result
trace = result.trace

# Trace metadata
print(f"Trace ID: {trace.id}")
print(f"Duration: {trace.duration_ms}ms")
print(f"Tokens: {trace.total_tokens}")

# Trace steps
for step in trace.steps:
    print(f"Step: {step.type}")
    print(f"  Duration: {step.duration_ms}ms")
```

## Custom Trace Processors

```python
from agents import TraceProcessor, enable_tracing

class LoggingProcessor(TraceProcessor):
    def process_trace(self, trace):
        print(f"[TRACE] Run {trace.id}")
        print(f"  Agent: {trace.agent_name}")
        print(f"  Turns: {trace.turn_count}")
        print(f"  Duration: {trace.duration_ms}ms")
        print(f"  Tokens: {trace.total_tokens}")
        
        for step in trace.steps:
            self._log_step(step)
    
    def _log_step(self, step, indent=2):
        prefix = " " * indent
        print(f"{prefix}[{step.type}] {step.summary}")

# Register processor
enable_tracing(processors=[LoggingProcessor()])
```

## Export Traces

### JSON Export

```python
from agents import Agent, Runner
import json

agent = Agent(name="Test", instructions="...")
result = Runner.run_sync(agent, "Hello")

# Export trace to JSON
trace_data = result.trace.to_dict()

with open("trace.json", "w") as f:
    json.dump(trace_data, f, indent=2)
```

### Trace Structure

```python
trace_data = {
    "id": "trace_abc123",
    "agent_name": "Test",
    "start_time": "2024-01-25T10:00:00Z",
    "end_time": "2024-01-25T10:00:01Z",
    "duration_ms": 1234,
    "turn_count": 2,
    "total_tokens": 150,
    "steps": [
        {
            "type": "llm_call",
            "model": "gpt-4o",
            "input_tokens": 50,
            "output_tokens": 100,
            "duration_ms": 800
        },
        {
            "type": "tool_call",
            "tool_name": "search",
            "arguments": {"query": "test"},
            "output": "Results...",
            "duration_ms": 200
        }
    ],
    "final_output": "Here are the results..."
}
```

## Tracing with OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from agents import TraceProcessor, enable_tracing

# Set up OpenTelemetry
provider = TracerProvider()
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter())
)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

class OTelProcessor(TraceProcessor):
    def process_trace(self, agent_trace):
        with tracer.start_as_current_span("agent_run") as span:
            span.set_attribute("agent.name", agent_trace.agent_name)
            span.set_attribute("agent.turns", agent_trace.turn_count)
            span.set_attribute("tokens.total", agent_trace.total_tokens)
            
            for step in agent_trace.steps:
                with tracer.start_span(step.type) as step_span:
                    step_span.set_attribute("duration_ms", step.duration_ms)
                    if step.type == "tool_call":
                        step_span.set_attribute("tool.name", step.tool_name)

enable_tracing(processors=[OTelProcessor()])
```

## Trace Filtering

```python
from agents import TraceProcessor, enable_tracing

class FilteredProcessor(TraceProcessor):
    def __init__(self, min_duration_ms=100):
        self.min_duration_ms = min_duration_ms
    
    def should_process(self, trace) -> bool:
        """Only process slow traces."""
        return trace.duration_ms >= self.min_duration_ms
    
    def process_trace(self, trace):
        print(f"[SLOW] {trace.agent_name}: {trace.duration_ms}ms")

enable_tracing(processors=[FilteredProcessor(min_duration_ms=500)])
```

## Debugging with Traces

```python
from agents import Agent, Runner

agent = Agent(
    name="DebugAgent",
    instructions="Be helpful.",
    tools=[some_tool]
)

result = Runner.run_sync(agent, "Do something")

# Inspect what happened
trace = result.trace

print("=== Trace Analysis ===")
print(f"Total time: {trace.duration_ms}ms")
print(f"Total tokens: {trace.total_tokens}")
print()

for i, step in enumerate(trace.steps, 1):
    print(f"Step {i}: {step.type}")
    
    if step.type == "llm_call":
        print(f"  Model: {step.model}")
        print(f"  Input tokens: {step.input_tokens}")
        print(f"  Output tokens: {step.output_tokens}")
    
    elif step.type == "tool_call":
        print(f"  Tool: {step.tool_name}")
        print(f"  Args: {step.arguments}")
        print(f"  Output: {step.output[:100]}...")
    
    elif step.type == "handoff":
        print(f"  Target: {step.target_agent}")
    
    print(f"  Duration: {step.duration_ms}ms")
    print()
```

## Complete Example

```python
"""
Agent with comprehensive tracing
"""

import json
import time
from datetime import datetime
from agents import Agent, Runner, function_tool, enable_tracing, TraceProcessor

# =============================================================================
# Custom Trace Processor
# =============================================================================

class DetailedLogger(TraceProcessor):
    def __init__(self, log_file="traces.jsonl"):
        self.log_file = log_file
    
    def process_trace(self, trace):
        # Print summary
        print(f"\n{'='*60}")
        print(f"RUN TRACE: {trace.id}")
        print(f"{'='*60}")
        print(f"Agent: {trace.agent_name}")
        print(f"Duration: {trace.duration_ms}ms")
        print(f"Tokens: {trace.total_tokens}")
        print(f"Turns: {trace.turn_count}")
        print()
        
        # Log steps
        for i, step in enumerate(trace.steps, 1):
            self._log_step(i, step)
        
        print(f"\nFinal Output:\n{trace.final_output[:200]}...")
        print(f"{'='*60}\n")
        
        # Append to file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(trace.to_dict()) + "\n")
    
    def _log_step(self, num, step):
        print(f"Step {num}: [{step.type.upper()}]")
        
        if step.type == "llm_call":
            print(f"    Model: {step.model}")
            print(f"    Tokens: {step.input_tokens} in, {step.output_tokens} out")
        
        elif step.type == "tool_call":
            print(f"    Tool: {step.tool_name}")
            print(f"    Args: {json.dumps(step.arguments)}")
            print(f"    Output: {str(step.output)[:80]}...")
        
        elif step.type == "handoff":
            print(f"    Target: {step.target_agent}")
        
        print(f"    Time: {step.duration_ms}ms")

# =============================================================================
# Enable Tracing
# =============================================================================

enable_tracing(
    project_name="agent-demo",
    processors=[DetailedLogger()]
)

# =============================================================================
# Define Agent
# =============================================================================

@function_tool
def calculate(expression: str) -> str:
    """Calculate a math expression."""
    try:
        result = eval(expression)
        return str(result)
    except:
        return "Error: Invalid expression"

@function_tool
def get_time() -> str:
    """Get current time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

agent = Agent(
    name="Calculator",
    instructions="""You are a helpful calculator assistant.
You can perform calculations and tell the time.
Always show your work.""",
    tools=[calculate, get_time]
)

# =============================================================================
# Run with Tracing
# =============================================================================

queries = [
    "What is 2 + 2?",
    "Calculate 15 * 7 + 23 / 5",
    "What time is it and what's 100 / 4?"
]

for query in queries:
    print(f"\nQuery: {query}")
    result = Runner.run_sync(agent, query)
    print(f"Response: {result.final_output}")
```
