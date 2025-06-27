import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
from TraceCollector import TraceCollector, FailureAnalyzer, FailurePropagationMonitor, PatchEvaluator

class MetaGPTTraceHandler(logging.Handler):
    """
    Custom logging handler for MetaGPT agents that stores logs in memory.
    """
    
    def __init__(self, agent_id: str):
        super().__init__()
        self.agent_id = agent_id
        self.logs = []
        self.lock = threading.Lock()
    
    def emit(self, record):
        with self.lock:
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'message': self.format(record),
                'level': record.levelname,
                'agent_id': self.agent_id
            }
            self.logs.append(log_entry)
    
    def get_logs(self) -> List[Dict]:
        """Get all logs for this agent."""
        with self.lock:
            return self.logs.copy()
    
    def clear_logs(self):
        """Clear all logs for this agent."""
        with self.lock:
            self.logs.clear()

class MetaGPTTraceManager:
    """
    Manages trace handlers for MetaGPT agents and provides access to logs.
    """
    
    def __init__(self):
        self.agents: Dict[str, MetaGPTTraceHandler] = {}
        self.lock = threading.Lock()
    
    def register_agent(self, agent_id: str) -> MetaGPTTraceHandler:
        """Register a new agent and return its trace handler."""
        with self.lock:
            handler = MetaGPTTraceHandler(agent_id)
            self.agents[agent_id] = handler
            return handler
    
    def get_agent_logs(self, agent_id: str) -> List[Dict]:
        """Get logs for a specific agent."""
        with self.lock:
            if agent_id in self.agents:
                return self.agents[agent_id].get_logs()
            return []
    
    def get_all_logs(self) -> List[Dict]:
        """Get all logs from all agents."""
        all_logs = []
        with self.lock:
            for agent_id, handler in self.agents.items():
                logs = handler.get_logs()
                for log in logs:
                    all_logs.append({
                        'agent_id': agent_id,
                        'timestamp': log['timestamp'],
                        'message': log['message']
                    })
        return all_logs
    
    def clear_agent_logs(self, agent_id: str):
        """Clear logs for a specific agent."""
        with self.lock:
            if agent_id in self.agents:
                self.agents[agent_id].clear_logs()
    
    def get_registered_agents(self) -> List[str]:
        """Get list of registered agent IDs."""
        with self.lock:
            return list(self.agents.keys())

def setup_metagpt_tracing(agent_id: str, trace_manager: MetaGPTTraceManager) -> logging.Handler:
    """
    Set up tracing for a MetaGPT agent.
    
    Usage in MetaGPT:
    from metagpt_trace_integration import setup_metagpt_tracing, trace_manager
    
    # In your agent initialization
    trace_handler = setup_metagpt_tracing("your_agent_name", trace_manager)
    logger = logging.getLogger()
    logger.addHandler(trace_handler)
    """
    return trace_manager.register_agent(agent_id)

def run_trace_analysis(trace_manager: MetaGPTTraceManager):
    """
    Run the complete trace analysis on MetaGPT agents.
    
    Args:
        trace_manager: The trace manager containing agent logs
    """
    print("Starting MetaGPT Trace Analysis...")
    
    # Get all logs
    logs = trace_manager.get_all_logs()
    
    if not logs:
        print("No logs collected. Make sure agents are running and logging.")
        return
    
    # Save logs to CSV
    with open('metagpt_logs.csv', 'w', newline='', encoding='utf-8') as csvfile:
        import csv
        fieldnames = ['agent_id', 'timestamp', 'message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for log in logs:
            writer.writerow(log)
    
    print(f"Saved {len(logs)} log entries to metagpt_logs.csv")
    
    # Analyze failures
    print("\n=== FAILURE ANALYSIS ===")
    analyzer = FailureAnalyzer(logs)
    failures_by_agent = analyzer.classify_failures()
    
    for agent_id, failures in failures_by_agent.items():
        print(f"\nFailures for {agent_id}:")
        for failure in failures:
            print(f"  [{failure['timestamp']}] {failure['message']} (Category: {failure['category']})")
    
    # Monitor failure propagation
    print("\n=== FAILURE PROPAGATION ===")
    propagation_monitor = FailurePropagationMonitor(logs)
    propagation_monitor.show_propagation()
    propagation_monitor.show_failure_introducers()
    
    print("\nTrace analysis complete!")

# Global trace manager instance
trace_manager = MetaGPTTraceManager()

# Example usage
if __name__ == "__main__":
    # Example: Simulate some agent logs
    print("Setting up MetaGPT Trace Manager...")
    
    # Register some example agents
    pm_handler = setup_metagpt_tracing("product_manager", trace_manager)
    arch_handler = setup_metagpt_tracing("architect", trace_manager)
    eng_handler = setup_metagpt_tracing("engineer", trace_manager)
    
    # Simulate some log messages
    pm_handler.emit(logging.LogRecord(
        name="product_manager", level=logging.INFO, pathname="", lineno=0,
        msg="Starting product requirements analysis", args=(), exc_info=None
    ))
    
    arch_handler.emit(logging.LogRecord(
        name="architect", level=logging.ERROR, pathname="", lineno=0,
        msg="Failed to design system architecture: timeout error", args=(), exc_info=None
    ))
    
    eng_handler.emit(logging.LogRecord(
        name="engineer", level=logging.ERROR, pathname="", lineno=0,
        msg="Cannot implement due to architecture failure", args=(), exc_info=None
    ))
    
    # Run analysis
    run_trace_analysis(trace_manager) 