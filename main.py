#!/usr/bin/env python3
"""
Interactive Python terminal for controlling Anova WiFi devices
Supports both Anova Precision Cookers (APC) and Anova Precision Ovens (APO)
"""

import asyncio
import sys

import commands
from client import AnovaController
import models


async def main():
    # controller = AnovaController()
    client = AnovaController(token="anova-eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiI0MDBRaXNsVjRCYkNzYXN2U3hXNENvZHJ6RUEyIiwiY3JlYXRlZEF0IjoxNzU4ODg0MDE2NDUyfQ.gIxNMZ8njgpIAicIAr7UzA9ujV2OLtnSNuBaeT8KWVY")

    try:
        if not await client.connect():
            return
        
        # Select device
        if not client.select_device():
            return
        
        print(f"\n🚀 Ready to control your {client.selected_device['name']}!")
        print("Keep this connection open to send commands...")

        cook = models.Cook(stages=[
            models.Stage(
                title="first",
                description="1st stage",
                type=models.Stage.Type.PREHEAT,
                userActionRequired=False,
                temperatureBulbs=models.TempBulb.wet_bulb(90),
                heatingElements=models.HeatingElements.top_and_bottom(),
                fan=models.Fan(speed=100),
                probe=models.Probe(temp=60),
                stageTransitionType=models.Stage.Transition.AUTO,
                steamGenerators=models.SteamGenerators.sous_vide(30)
            ),
            models.Stage(
                title="second",
                description="2nd stage",
                type=models.Stage.Type.COOK,
                userActionRequired=True,
                temperatureBulbs=models.TempBulb.dry_bulb(120),
                heatingElements=models.HeatingElements.top_only(),
                fan=models.Fan(speed=50),
                probe=models.Probe(temp=60),
                stageTransitionType=models.Stage.Transition.MANUAL,
                steamGenerators=models.SteamGenerators.no_steam()
            )
        ])

        command = commands.Command.start(device_id=client.selected_device['id'], cook=cook)

        await client.send_command_and_wait_for_response(command_data=command)

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Check if websockets is available
    try:
        import websockets
    except ImportError:
        print("❌ Missing required dependency: websockets")
        print("Install with: pip install websockets")
        sys.exit(1)
    
    asyncio.run(main())
