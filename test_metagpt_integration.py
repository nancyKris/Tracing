#!/usr/bin/env python3
"""
Test script demonstrating MetaGPT trace integration.
This simulates a typical MetaGPT workflow with tracing enabled.
"""

import logging
import time
from datetime import datetime
from metagpt_trace_integration import setup_metagpt_tracing, trace_manager, run_trace_analysis

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class SimulatedProductManager:
    """Simulates a MetaGPT Product Manager agent with tracing."""
    
    def __init__(self):
        self.trace_handler = setup_metagpt_tracing("product_manager", trace_manager)
        self.logger = logging.getLogger("product_manager")
        self.logger.addHandler(self.trace_handler)
        self.logger.setLevel(logging.INFO)
    
    def analyze_requirements(self, requirements: str):
        """Simulate requirements analysis."""
        self.logger.info(f"Starting requirements analysis for: {requirements}")
        
        try:
            # Simulate some processing time
            time.sleep(0.1)
            
            if "invalid" in requirements.lower():
                raise ValueError("Invalid requirements format")
            
            if "complex" in requirements.lower():
                self.logger.warning("Complex requirements detected - may cause issues downstream")
            
            self.logger.info("Requirements analysis completed successfully")
            return f"Analyzed requirements: {requirements}"
            
        except Exception as e:
            self.logger.error(f"Requirements analysis failed: {str(e)}")
            raise

class SimulatedArchitect:
    """Simulates a MetaGPT Architect agent with tracing."""
    
    def __init__(self):
        self.trace_handler = setup_metagpt_tracing("architect", trace_manager)
        self.logger = logging.getLogger("architect")
        self.logger.addHandler(self.trace_handler)
        self.logger.setLevel(logging.INFO)
    
    def design_system(self, requirements: str):
        """Simulate system design."""
        self.logger.info("Starting system architecture design")
        
        try:
            # Simulate some processing time
            time.sleep(0.1)
            
            if "complex" in requirements.lower():
                self.logger.error("System too complex - timeout error")
                raise TimeoutError("System design timeout - complexity too high")
            
            if "invalid" in requirements.lower():
                self.logger.error("Cannot design system with invalid requirements")
                raise ValueError("Invalid requirements provided")
            
            self.logger.info("System architecture design completed")
            return "System architecture designed successfully"
            
        except Exception as e:
            self.logger.error(f"System design failed: {str(e)}")
            raise

class SimulatedEngineer:
    """Simulates a MetaGPT Engineer agent with tracing."""
    
    def __init__(self):
        self.trace_handler = setup_metagpt_tracing("engineer", trace_manager)
        self.logger = logging.getLogger("engineer")
        self.logger.addHandler(self.trace_handler)
        self.logger.setLevel(logging.INFO)
    
    def implement_system(self, architecture: str):
        """Simulate system implementation."""
        self.logger.info("Starting system implementation")
        
        try:
            # Simulate some processing time
            time.sleep(0.1)
            
            if "timeout" in architecture.lower():
                self.logger.error("Cannot implement due to architecture timeout")
                raise RuntimeError("Implementation blocked by architecture failure")
            
            self.logger.info("System implementation completed successfully")
            return "System implemented successfully"
            
        except Exception as e:
            self.logger.error(f"System implementation failed: {str(e)}")
            raise

class SimulatedQAEngineer:
    """Simulates a MetaGPT QA Engineer agent with tracing."""
    
    def __init__(self):
        self.trace_handler = setup_metagpt_tracing("qa_engineer", trace_manager)
        self.logger = logging.getLogger("qa_engineer")
        self.logger.addHandler(self.trace_handler)
        self.logger.setLevel(logging.INFO)
    
    def test_system(self, implementation: str):
        """Simulate system testing."""
        self.logger.info("Starting system testing")
        
        try:
            # Simulate some processing time
            time.sleep(0.1)
            
            if "blocked" in implementation.lower():
                self.logger.error("Testing blocked due to implementation failure")
                raise RuntimeError("Testing cannot proceed - implementation failed")
            
            # Simulate some test failures
            if "complex" in implementation.lower():
                self.logger.warning("Complex system detected - some tests may fail")
                self.logger.error("Test failure: integration test timeout")
                raise AssertionError("Integration test failed - timeout")
            
            self.logger.info("System testing completed successfully")
            return "All tests passed"
            
        except Exception as e:
            self.logger.error(f"System testing failed: {str(e)}")
            raise

def run_metagpt_workflow(requirements: str):
    """Run a complete MetaGPT workflow with tracing."""
    print(f"\n=== Starting MetaGPT Workflow ===")
    print(f"Requirements: {requirements}")
    print(f"Timestamp: {datetime.now()}")
    
    # Initialize agents
    pm = SimulatedProductManager()
    arch = SimulatedArchitect()
    eng = SimulatedEngineer()
    qa = SimulatedQAEngineer()
    
    try:
        # Step 1: Requirements Analysis
        print("\n1. Product Manager analyzing requirements...")
        analyzed_req = pm.analyze_requirements(requirements)
        
        # Step 2: System Design
        print("\n2. Architect designing system...")
        architecture = arch.design_system(analyzed_req)
        
        # Step 3: Implementation
        print("\n3. Engineer implementing system...")
        implementation = eng.implement_system(architecture)
        
        # Step 4: Testing
        print("\n4. QA Engineer testing system...")
        test_results = qa.test_system(implementation)
        
        print(f"\n✅ Workflow completed successfully!")
        print(f"Final result: {test_results}")
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {str(e)}")
    
    print(f"\n=== Workflow completed at {datetime.now()} ===")

def main():
    """Main function to demonstrate the integration."""
    print("MetaGPT Trace Integration Demo")
    print("=" * 50)
    
    # Test scenarios
    test_scenarios = [
        "Build a simple web application",
        "Build a complex distributed system",  # This will cause failures
        "Build an invalid system",  # This will cause different failures
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*20} Test Scenario {i} {'='*20}")
        
        # Clear previous logs
        trace_manager.clear_agent_logs("product_manager")
        trace_manager.clear_agent_logs("architect")
        trace_manager.clear_agent_logs("engineer")
        trace_manager.clear_agent_logs("qa_engineer")
        
        # Run workflow
        run_metagpt_workflow(scenario)
        
        # Run trace analysis
        print(f"\n{'='*20} Trace Analysis for Scenario {i} {'='*20}")
        run_trace_analysis(trace_manager)
        
        # Wait between scenarios
        if i < len(test_scenarios):
            print("\nWaiting 2 seconds before next scenario...")
            time.sleep(2)
    
    print(f"\n{'='*20} Demo Complete {'='*20}")
    print("Check the generated 'metagpt_logs.csv' file for detailed logs.")

if __name__ == "__main__":
    main() 