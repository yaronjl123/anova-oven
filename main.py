#!/usr/bin/env python3
"""
Interactive Python terminal for controlling Anova WiFi devices
Supports both Anova Precision Cookers (APC) and Anova Precision Ovens (APO)
"""

import asyncio
import sys

from controller import AnovaController


async def main():
    print("🔥 Anova WiFi Device Controller")
    print("=" * 40)
    
    # Get Personal Access Token
    print("\n🔑 Personal Access Token Required")
    print("Find your token in the Anova Oven app: More → Developer → Personal Access Tokens")
    print("(Note: Sous Vide users should also download the Oven app to generate tokens)")
    
    token = input("\nEnter your Personal Access Token (starts with 'anova-'): ").strip()
    
    if not token.startswith("anova-"):
        print("❌ Invalid token format. Token should start with 'anova-'")
        return
    
    controller = AnovaController()
    
    try:
        # Connect to websocket
        if not await controller.connect(token):
            return
        
        # Select device
        if not controller.select_device():
            return
        
        print(f"\n🚀 Ready to control your {controller.selected_device['name']}!")
        print("Keep this connection open to send commands...")
        
        # Run interactive menu (background listener already started)
        await controller.run_interactive_menu()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Cleanup will be handled by run_interactive_menu
        pass


if __name__ == "__main__":
    # Check if websockets is available
    try:
        import websockets
    except ImportError:
        print("❌ Missing required dependency: websockets")
        print("Install with: pip install websockets")
        sys.exit(1)
    
    asyncio.run(main())