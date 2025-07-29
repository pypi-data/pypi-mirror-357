#!/usr/bin/env python3
"""
Minimal script to create and run a DroidAgent
"""

import asyncio
import os
import sys

# Add the current directory to Python path so we can import droidrun
sys.path.insert(0, '/home/sleyn/projects/droidrun')

async def main():
    try:
        # Import required modules
        from droidrun.agent.droid import DroidAgent
        from droidrun.agent.utils.llm_picker import load_llm
        from droidrun.tools.adb import DeviceManager, AdbTools
        from droidrun.agent.context.personas import DEFAULT, APP_STARTER_EXPERT
        
        # Configuration
        goal = """Open the notes app and create a new note"""
        provider = "Gemini"  # Change this to your preferred provider
        model = "models/gemini-2.5-flash-preview-05-20"
        
        # Check for API key
        api_key = os.getenv("GEMINI_API_KEY") #os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ Please set GEMINI_API_KEY environment variable")
            print("   Example: export GEMINI_API_KEY='your-api-key-here'")
            return
        
        print(f"🎯 Goal: {goal}")
        print(f"🤖 Using {provider} with model {model}")
        
        # Find a connected device
        device_manager = DeviceManager()
        devices = await device_manager.list_devices()
        
        #if not devices:
        #    print("❌ No Android devices found. Please connect a device via ADB.")
        #    print("   Try: adb devices")
        #    return
        
        device_serial = devices[0].serial
        #"http://localhost:6643"using the CLI and 
        #device_serial = "http://192.168.100.91:6643"
        print(f"📱 Using device: {device_serial}")
        
        # Initialize LLM
        print("🧠 Initializing LLM...")
        llm = load_llm(
            provider_name=provider,
            model=model,
            api_key=api_key,
            temperature=0.2
        )

        tools = AdbTools(serial=device_serial)


        
        # Create DroidAgent
        print("🤖 Creating DroidAgent...")
        agent = DroidAgent(
            goal=goal,
            llm=llm,
            tools=tools,
            max_steps=100,
            timeout=3000,
            reasoning=False,
            debug=True,
            save_trajectories=True,
            enable_tracing=False
        )
        
        # Run the agent
        print("🚀 Running agent...")
        handler = agent.run()
        async for nested_ev in handler.stream_events():
            print(f"EXTERNAL EVENT: {nested_ev.__class__.__name__}")

        result = await handler

        # Print results
        if result.get("success"):
            print(f"✅ Success: {result.get('reason', 'Goal completed')}")
        else:
            print(f"❌ Failed: {result.get('reason', 'Unknown error')}")
        
        print(f"📊 Steps taken: {result.get('steps', 0)}")
        
        if result.get("trajectory"):
            print(f"📝 Trajectory has {len(result['trajectory'])} steps")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're in the droidrun project directory")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
