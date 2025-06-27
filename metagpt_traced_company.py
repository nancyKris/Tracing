#!/usr/bin/env python3
"""
MetaGPT Traced Software Company
Integrates TraceCollector with MetaGPT's actual agent roles.
"""

import asyncio
import logging
from typing import List
from metagpt.software_company import SoftwareCompany
from metagpt.roles import ProductManager, Architect, ProjectManager, Engineer
from metagpt_trace_integration import setup_metagpt_tracing, trace_manager, run_trace_analysis

class TracedProductManager(ProductManager):
    """Product Manager with tracing enabled."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up tracing
        self.trace_handler = setup_metagpt_tracing("product_manager", trace_manager)
        self.logger = logging.getLogger("product_manager")
        self.logger.addHandler(self.trace_handler)
        self.logger.setLevel(logging.INFO)
        self.logger.info("Product Manager initialized with tracing")

class TracedArchitect(Architect):
    """Architect with tracing enabled."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up tracing
        self.trace_handler = setup_metagpt_tracing("architect", trace_manager)
        self.logger = logging.getLogger("architect")
        self.logger.addHandler(self.trace_handler)
        self.logger.setLevel(logging.INFO)
        self.logger.info("Architect initialized with tracing")

class TracedProjectManager(ProjectManager):
    """Project Manager with tracing enabled."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up tracing
        self.trace_handler = setup_metagpt_tracing("project_manager", trace_manager)
        self.logger = logging.getLogger("project_manager")
        self.logger.addHandler(self.trace_handler)
        self.logger.setLevel(logging.INFO)
        self.logger.info("Project Manager initialized with tracing")

class TracedEngineer(Engineer):
    """Engineer with tracing enabled."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up tracing
        self.trace_handler = setup_metagpt_tracing("engineer", trace_manager)
        self.logger = logging.getLogger("engineer")
        self.logger.addHandler(self.trace_handler)
        self.logger.setLevel(logging.INFO)
        self.logger.info("Engineer initialized with tracing")

class TracedSoftwareCompany(SoftwareCompany):
    """Software Company with tracing enabled."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Replace default roles with traced versions
        self.product_manager = TracedProductManager()
        self.architect = TracedArchitect()
        self.project_manager = TracedProjectManager()
        self.engineer = TracedEngineer()
        
        # Set up company-level logging
        self.logger = logging.getLogger("software_company")
        self.logger.setLevel(logging.INFO)
        self.logger.info("Traced Software Company initialized")

    async def run(self, idea: str) -> List[str]:
        """Run the software company workflow with tracing."""
        self.logger.info(f"Starting software company workflow for: {idea}")
        
        try:
            # Run the original workflow
            result = await super().run(idea)
            self.logger.info("Software company workflow completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Software company workflow failed: {str(e)}")
            raise

async def generate_traced_repo(idea: str):
    """Generate a repository with tracing enabled."""
    print(f"Starting traced repository generation for: {idea}")
    
    # Create traced software company
    company = TracedSoftwareCompany()
    
    try:
        # Run the workflow
        result = await company.run(idea)
        
        # Run trace analysis
        print("\n" + "="*50)
        print("TRACE ANALYSIS RESULTS")
        print("="*50)
        run_trace_analysis(trace_manager)
        
        return result
    except Exception as e:
        print(f"Repository generation failed: {e}")
        # Still run trace analysis to see what happened
        print("\n" + "="*50)
        print("TRACE ANALYSIS (AFTER FAILURE)")
        print("="*50)
        run_trace_analysis(trace_manager)
        raise

def main():
    """Main function to demonstrate traced MetaGPT usage."""
    import sys
    
    if len(sys.argv) > 1:
        idea = " ".join(sys.argv[1:])
    else:
        idea = "Create a simple calculator app"
    
    print("MetaGPT Traced Software Company Demo")
    print("="*50)
    print(f"Idea: {idea}")
    print("="*50)
    
    # Run the traced workflow
    asyncio.run(generate_traced_repo(idea))

if __name__ == "__main__":
    main() 