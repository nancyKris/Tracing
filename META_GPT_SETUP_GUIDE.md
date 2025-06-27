# MetaGPT Trace Integration Setup Guide

This guide shows how to integrate your `TraceCollector.py` with the actual [MetaGPT repository](https://github.com/FoundationAgents/MetaGPT).

## Prerequisites

1. **Python 3.9-3.11** (MetaGPT requirement)
2. **Node.js and pnpm** (for MetaGPT's frontend components)
3. **Git** (to clone MetaGPT)

## Step 1: Install MetaGPT

```bash
# Clone MetaGPT if you haven't already
git clone https://github.com/FoundationAgents/MetaGPT.git
cd MetaGPT

# Install MetaGPT
pip install --upgrade -e .

# Install Node.js dependencies
pnpm install
```

## Step 2: Configure MetaGPT

```bash
# Initialize MetaGPT configuration
metagpt --init-config
```

Edit `~/.metagpt/config2.yaml`:
```yaml
llm:
  api_type: "openai"  # or your preferred LLM
  model: "gpt-4-turbo"
  base_url: "https://api.openai.com/v1"
  api_key: "YOUR_API_KEY"
```

## Step 3: Copy Trace Integration Files

Copy the trace integration files to your MetaGPT directory:

```bash
# Copy files to MetaGPT root
cp /path/to/TraceCollector.py ./
cp /path/to/metagpt_trace_integration.py ./
cp /path/to/metagpt_traced_company.py ./
cp /path/to/test_metagpt_integration.py ./
```

## Step 4: Test the Integration

### Option A: Test with Simulated Agents
```bash
python test_metagpt_integration.py
```

### Option B: Test with Real MetaGPT
```bash
python metagpt_traced_company.py "Create a simple todo app"
```

## Step 5: Advanced Integration

### Integrate with Existing MetaGPT Workflows

Create a custom script that uses your traced agents:

```python
#!/usr/bin/env python3
"""
Custom MetaGPT workflow with tracing
"""

import asyncio
from metagpt_traced_company import generate_traced_repo

async def main():
    # Your custom workflow
    ideas = [
        "Create a weather app",
        "Build a chat application", 
        "Design a task management system"
    ]
    
    for idea in ideas:
        print(f"\n{'='*60}")
        print(f"Processing: {idea}")
        print(f"{'='*60}")
        
        try:
            result = await generate_traced_repo(idea)
            print(f"✅ Success: {len(result)} files generated")
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Monitor Real-time Failures

Create a monitoring script:

```python
#!/usr/bin/env python3
"""
Real-time MetaGPT failure monitoring
"""

import time
import threading
from metagpt_trace_integration import trace_manager, run_trace_analysis

def monitor_failures():
    """Monitor failures in real-time."""
    while True:
        logs = trace_manager.get_all_logs()
        failures = [log for log in logs if any(word in log['message'].lower() 
                                             for word in ['fail', 'error', 'exception'])]
        
        if failures:
            print(f"\n🚨 {len(failures)} failures detected!")
            for failure in failures[-3:]:  # Show last 3 failures
                print(f"  {failure['agent_id']}: {failure['message']}")
        
        time.sleep(10)  # Check every 10 seconds

# Start monitoring in background
monitor_thread = threading.Thread(target=monitor_failures, daemon=True)
monitor_thread.start()
```

## Step 6: Production Usage

### Integrate with MetaGPT CLI

Modify your MetaGPT installation to use traced agents by default:

```python
# In your MetaGPT environment, create a wrapper
from metagpt.software_company import generate_repo
from metagpt_traced_company import generate_traced_repo

# Replace the default function
def traced_generate_repo(idea: str):
    """Generate repo with tracing enabled."""
    return asyncio.run(generate_traced_repo(idea))

# Use this instead of the original generate_repo
```

### Batch Processing with Tracing

```python
#!/usr/bin/env python3
"""
Batch process multiple ideas with tracing
"""

import asyncio
import json
from datetime import datetime
from metagpt_traced_company import generate_traced_repo
from metagpt_trace_integration import trace_manager

async def batch_process(ideas_file: str):
    """Process multiple ideas from a JSON file."""
    
    with open(ideas_file, 'r') as f:
        ideas = json.load(f)
    
    results = []
    
    for i, idea in enumerate(ideas, 1):
        print(f"\n{'='*60}")
        print(f"Processing {i}/{len(ideas)}: {idea}")
        print(f"{'='*60}")
        
        # Clear previous logs
        for agent in trace_manager.get_registered_agents():
            trace_manager.clear_agent_logs(agent)
        
        try:
            result = await generate_traced_repo(idea)
            results.append({
                'idea': idea,
                'status': 'success',
                'files_generated': len(result),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            results.append({
                'idea': idea,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        
        # Run analysis after each idea
        run_trace_analysis(trace_manager)
    
    # Save results
    with open('batch_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

# Usage: python batch_process.py ideas.json
```

## Step 7: Customize Failure Detection

### Add MetaGPT-Specific Failure Categories

Edit `TraceCollector.py` to add MetaGPT-specific failure detection:

```python
def _categorize_failure(self, msg: str) -> str:
    msg_lower = msg.lower()
    
    # MetaGPT-specific categories
    if any(kw in msg_lower for kw in ['llm', 'gpt', 'openai', 'api']):
        return 'LLM API Error'
    elif any(kw in msg_lower for kw in ['code generation', 'syntax', 'compile']):
        return 'Code Generation Error'
    elif any(kw in msg_lower for kw in ['requirements', 'user story', 'product']):
        return 'Requirements Analysis Error'
    elif any(kw in msg_lower for kw in ['architecture', 'design', 'system']):
        return 'Architecture Design Error'
    elif any(kw in msg_lower for kw in ['project', 'planning', 'timeline']):
        return 'Project Management Error'
    elif any(kw in msg_lower for kw in ['implementation', 'coding', 'development']):
        return 'Implementation Error'
    
    # Original categories
    if any(kw in msg_lower for kw in ['syntax error', 'compile error']):
        return 'Syntax / compile error'
    elif any(kw in msg_lower for kw in ['assertion failed', 'test failed']):
        return 'Logic / test failure'
    elif 'timeout' in msg_lower:
        return 'Timeout'
    elif any(kw in msg_lower for kw in ['hallucination', 'nonsensical']):
        return 'LLM hallucination'
    else:
        return 'Other'
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure MetaGPT is properly installed
   ```bash
   pip install --upgrade -e .
   ```

2. **Configuration Issues**: Check your `~/.metagpt/config2.yaml`
   ```bash
   metagpt --init-config
   ```

3. **No Logs Generated**: Ensure agents are actually running
   ```python
   # Add debug logging
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

4. **Permission Issues**: Make sure you have write permissions
   ```bash
   chmod +x metagpt_traced_company.py
   ```

### Debug Mode

Enable debug mode to see what's happening:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Next Steps

1. **Customize failure detection** for your specific use cases
2. **Add alerting** when critical failures occur
3. **Integrate with monitoring systems** like Grafana or Prometheus
4. **Create dashboards** to visualize failure patterns
5. **Set up automated testing** with failure analysis

## Support

- Check the [MetaGPT documentation](https://docs.deepwisdom.ai/)
- Join the [MetaGPT Discord](https://discord.gg/metagpt)
- Create issues in the [MetaGPT repository](https://github.com/FoundationAgents/MetaGPT) 