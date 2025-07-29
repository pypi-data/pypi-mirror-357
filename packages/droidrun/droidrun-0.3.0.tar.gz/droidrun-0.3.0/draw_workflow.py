"""
Script to visualize the DroidAgent workflow using llama-index-utils-workflow
"""

import asyncio
from droidrun.agent.droid.droid_agent import PlannerAgent, DroidAgent, CodeActAgent
from llama_index.llms.openai import OpenAI
from llama_index.utils.workflow import (
    draw_all_possible_flows,
    draw_most_recent_execution,
)

async def main():
    # First, draw all possible flows statically
    print("📊 Drawing all possible workflow paths...")
    draw_all_possible_flows(DroidAgent, filename="droidagent.html")
    draw_all_possible_flows(CodeActAgent, filename="codeact.html")
    draw_all_possible_flows(PlannerAgent, filename="planner.html")
    return
    print("✨ All possible flows saved as 'droid_workflow_all.html'")
    
    # Then create an instance and run it to visualize a specific execution
    print("\n🔄 Running a sample workflow execution...")
    llm = OpenAI()  # You'll need to have OPENAI_API_KEY in env
    agent = DroidAgent(
        goal="List all installed apps",  # Simple example goal
        llm=llm,
        debug=True
    )
    
    # Run the workflow
    await agent.run()
    
    # Draw the most recent execution
    print("📊 Drawing the most recent execution path...")
    draw_most_recent_execution(agent, filename="droid_workflow_recent.html")
    print("✨ Recent execution flow saved as 'droid_workflow_recent.html'")

if __name__ == "__main__":
    asyncio.run(main()) 