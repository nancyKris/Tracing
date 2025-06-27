# MetaGPT Trace Integration Guide

This guide explains how to integrate your `TraceCollector.py` with MetaGPT to trace and analyze failures in your Multi-Agent System.

## Prerequisites

1. **MetaGPT Installation**: Make sure you have MetaGPT installed and working
2. **Python Dependencies**: Install required packages:
   ```bash
   pip install flask requests
   ```

## Integration Methods

### Method 1: Direct Integration (Recommended)

This method integrates tracing directly into your MetaGPT agents without requiring HTTP endpoints.

#### Step 1: Import the Trace Integration

In your MetaGPT project, add this to your main script or agent initialization:

```python
from metagpt_trace_integration import setup_metagpt_tracing, trace_manager, run_trace_analysis
```

#### Step 2: Modify Your MetaGPT Agents

For each MetaGPT agent you want to trace, add this to their initialization:

```python
# Example: In your ProductManager agent
class ProductManager:
    def __init__(self):
        # ... existing MetaGPT initialization ...
        
        # Add tracing
        self.trace_handler = setup_metagpt_tracing("product_manager", trace_manager)
        self.logger = logging.getLogger()
        self.logger.addHandler(self.trace_handler)
        
        # Set logging level
        self.logger.setLevel(logging.INFO)
```

#### Step 3: Add Logging to Agent Methods

Add logging statements to your agent methods to capture important events:

```python
class ProductManager:
    def analyze_requirements(self, requirements):
        self.logger.info("Starting requirements analysis")
        try:
            # ... existing logic ...
            self.logger.info("Requirements analysis completed successfully")
        except Exception as e:
            self.logger.error(f"Requirements analysis failed: {str(e)}")
            raise
```

#### Step 4: Run Trace Analysis

After your MetaGPT agents have run, analyze the traces:

```python
# Run the complete analysis
run_trace_analysis(trace_manager)
```

### Method 2: HTTP Endpoint Integration

This method uses HTTP endpoints for more distributed tracing.

#### Step 1: Install Flask

```bash
pip install flask
```

#### Step 2: Create HTTP Trace Server

Create a file called `metagpt_http_trace.py`:

```python
from flask import Flask, jsonify
from metagpt_trace_integration import MetaGPTTraceManager
import threading

app = Flask(__name__)
trace_manager = MetaGPTTraceManager()

@app.route('/logs/<agent_id>', methods=['GET'])
def get_agent_logs(agent_id):
    logs = trace_manager.get_agent_logs(agent_id)
    return jsonify(logs)

@app.route('/logs', methods=['GET'])
def get_all_logs():
    logs = trace_manager.get_all_logs()
    return jsonify(logs)

@app.route('/agents', methods=['GET'])
def get_agents():
    agents = trace_manager.get_registered_agents()
    return jsonify(agents)

def start_server(port=5000):
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    start_server()
```

#### Step 3: Use TraceCollector with HTTP Endpoints

```python
from TraceCollector import TraceCollector

# Configure agent endpoints
agent_endpoints = {
    'product_manager': 'http://localhost:5000/logs/product_manager',
    'architect': 'http://localhost:5000/logs/architect',
    'engineer': 'http://localhost:5000/logs/engineer',
}

# Collect and analyze
collector = TraceCollector(agent_endpoints)
logs = collector.collect_logs()
collector.save_to_csv(logs, 'metagpt_logs.csv')
```

## Complete Integration Example

Here's a complete example showing how to integrate with a typical MetaGPT workflow:

```python
import logging
from metagpt_trace_integration import setup_metagpt_tracing, trace_manager, run_trace_analysis

# Set up tracing for all agents
def setup_agent_tracing(agent_name):
    handler = setup_metagpt_tracing(agent_name, trace_manager)
    logger = logging.getLogger(agent_name)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

# Initialize your MetaGPT agents with tracing
class TracedProductManager:
    def __init__(self):
        self.logger = setup_agent_tracing("product_manager")
    
    def analyze_requirements(self, requirements):
        self.logger.info("Starting requirements analysis")
        try:
            # Your MetaGPT logic here
            result = "Requirements analyzed"
            self.logger.info("Requirements analysis completed")
            return result
        except Exception as e:
            self.logger.error(f"Requirements analysis failed: {e}")
            raise

class TracedArchitect:
    def __init__(self):
        self.logger = setup_agent_tracing("architect")
    
    def design_system(self, requirements):
        self.logger.info("Starting system design")
        try:
            # Your MetaGPT logic here
            if "complex" in requirements:
                raise Exception("System too complex - timeout")
            result = "System designed"
            self.logger.info("System design completed")
            return result
        except Exception as e:
            self.logger.error(f"System design failed: {e}")
            raise

# Main workflow
def run_metagpt_workflow():
    pm = TracedProductManager()
    arch = TracedArchitect()
    
    try:
        requirements = pm.analyze_requirements("Build a complex system")
        design = arch.design_system(requirements)
    except Exception as e:
        print(f"Workflow failed: {e}")
    
    # Run trace analysis
    run_trace_analysis(trace_manager)

if __name__ == "__main__":
    run_metagpt_workflow()
```

## Advanced Usage

### Custom Failure Categories

You can extend the failure categorization by modifying the `_categorize_failure` method in `TraceCollector.py`:

```python
def _categorize_failure(self, msg: str) -> str:
    msg_lower = msg.lower()
    # Add your custom categories
    if any(kw in msg_lower for kw in ['metagpt', 'agent', 'workflow']):
        return 'MetaGPT Agent Error'
    # ... existing categories ...
```

### Real-time Monitoring

For real-time monitoring, you can periodically run the analysis:

```python
import time
import threading

def monitor_metagpt():
    while True:
        run_trace_analysis(trace_manager)
        time.sleep(30)  # Check every 30 seconds

# Start monitoring in background
monitor_thread = threading.Thread(target=monitor_metagpt, daemon=True)
monitor_thread.start()
```

### Integration with MetaGPT's Built-in Logging

If MetaGPT already has logging, you can intercept it:

```python
import logging

class MetaGPTTraceInterceptor(logging.Handler):
    def __init__(self, agent_id: str, trace_manager):
        super().__init__()
        self.agent_id = agent_id
        self.trace_manager = trace_manager
    
    def emit(self, record):
        # Convert MetaGPT logs to trace format
        trace_record = logging.LogRecord(
            name=self.agent_id,
            level=record.levelno,
            pathname=record.pathname,
            lineno=record.lineno,
            msg=record.getMessage(),
            args=record.args,
            exc_info=record.exc_info
        )
        
        # Send to trace manager
        handler = self.trace_manager.register_agent(self.agent_id)
        handler.emit(trace_record)
```

## Troubleshooting

### Common Issues

1. **No logs collected**: Make sure agents are actually logging and the trace handlers are properly attached.

2. **Import errors**: Ensure all required packages are installed and the trace integration files are in your Python path.

3. **Thread safety**: The trace manager is thread-safe, but if you're using multiple processes, consider using a database or file-based storage.

### Debug Mode

Enable debug logging to see what's happening:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show all trace operations
```

## Next Steps

1. **Customize failure detection**: Modify the failure keywords and categories based on your specific MetaGPT use cases.

2. **Add visualization**: Integrate with plotting libraries to create failure propagation graphs.

3. **Database storage**: For production use, consider storing traces in a database for better performance and querying.

4. **Alerting**: Add automatic alerts when critical failures are detected.

## Support

If you encounter issues:
1. Check that all dependencies are installed
2. Verify that agents are properly logging
3. Ensure the trace manager is accessible from all agent processes
4. Check the console output for error messages 