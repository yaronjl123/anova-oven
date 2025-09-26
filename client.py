import asyncio
import json
import uuid
from datetime import datetime
from pydantic import BaseModel
import commands
import websockets


class AnovaController:
    def __init__(self, token):
        self.websocket = None
        self.token = token
        self.devices = []
        self.selected_device = None
        self.device_type = None
        self.message_history = []
        self.listener_task = None
        self.temperature_unit = "C"

    async def connect(self):
        """Connect to Anova websocket with authentication"""
        uri = f"wss://devices.anovaculinary.io?token={self.token}&supportedAccessories=APC,APO"

        try:
            self.websocket = await websockets.connect(uri)

            # Start background message listener immediately - it will handle device discovery
            self.listener_task = asyncio.create_task(self.continuous_message_listener())

            # Wait for device discovery messages to be captured by background listener
            await self.wait_for_device_discovery()
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    async def wait_for_device_discovery(self):
        """Wait for device discovery by checking message history"""
        print("🔍 Discovering devices...")

        try:
            # Wait for device discovery messages to appear in history
            timeout = 5
            start_time = asyncio.get_event_loop().time()

            while (asyncio.get_event_loop().time() - start_time) < timeout:
                # Check message history for device lists
                for msg in self.message_history:
                    data = msg["data"]

                    if data.get("command") == "EVENT_APC_WIFI_LIST" and "payload" in data:
                        for device in data["payload"]:
                            # Check if device already exists
                            if not any(d["id"] == device["cookerId"] for d in self.devices):
                                self.devices.append({
                                    "id": device["cookerId"],
                                    "name": device.get("name", "Anova Precision Cooker"),
                                    "type": "APC",
                                    "device_type": device.get("type", "unknown")
                                })

                    elif data.get("command") == "EVENT_APO_WIFI_LIST" and "payload" in data:
                        for device in data["payload"]:
                            # Check if device already exists
                            if not any(d["id"] == device["cookerId"] for d in self.devices):
                                self.devices.append({
                                    "id": device["cookerId"],
                                    "name": device.get("name", "Anova Precision Oven"),
                                    "type": "APO",
                                    "device_type": device.get("type", "unknown")
                                })

                # If we found devices, break early
                if self.devices:
                    break

                # Wait a bit before checking again
                await asyncio.sleep(0.1)

        except Exception as e:
            print(f"Error waiting for device discovery: {e}")

    async def continuous_message_listener(self):
        """Background task to continuously collect websocket messages"""
        print("🎧 Starting background message listener...")
        last_message_time = datetime.now()
        try:
            while True:
                # Add timeout to detect if no messages are coming
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=30.0)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    last_message_time = datetime.now()
                    data = json.loads(message)

                    # Store message with timestamp
                    self.message_history.append({
                        "timestamp": timestamp,
                        "data": data,
                        "raw": message
                    })

                    # Process device discovery messages
                    await self.process_device_discovery(data)

                except asyncio.TimeoutError:
                    # No message received in 30 seconds
                    now = datetime.now()
                    time_since_last = (now - last_message_time).total_seconds()
                    print(f"⏰ No websocket messages for {time_since_last:.0f} seconds (listener still active)")
                    continue

        except websockets.exceptions.ConnectionClosed:
            print("📡 WebSocket connection closed")
        except Exception as e:
            print(f"❌ Error in message listener: {e}")
            import traceback
            traceback.print_exc()

    async def process_device_discovery(self, data):
        """Process device discovery messages from websocket"""
        if data.get("command") == "EVENT_APC_WIFI_LIST" and "payload" in data:
            for device in data["payload"]:
                # Check if device already exists
                if not any(d["id"] == device["cookerId"] for d in self.devices):
                    self.devices.append({
                        "id": device["cookerId"],
                        "name": device.get("name", "Anova Precision Cooker"),
                        "type": "APC",
                        "device_type": device.get("type", "unknown")
                    })

        elif data.get("command") == "EVENT_APO_WIFI_LIST" and "payload" in data:
            for device in data["payload"]:
                # Check if device already exists
                if not any(d["id"] == device["cookerId"] for d in self.devices):
                    self.devices.append({
                        "id": device["cookerId"],
                        "name": device.get("name", "Anova Precision Oven"),
                        "type": "APO",
                        "device_type": device.get("type", "unknown")
                    })

    def display_devices(self):
        """Display discovered devices"""
        if not self.devices:
            print("❌ No devices found. Make sure your devices are connected to WiFi and paired with your account.")
            return False

        print("\n📱 Discovered devices:")
        for i, device in enumerate(self.devices, 1):
            print(f"{i}. {device['name']} ({device['type']}) - ID: {device['id']}")

        return True

    def select_device(self):
        """Let user select a device"""
        if not self.display_devices():
            return False

        try:
            # choice = input("\nSelect device number: ").strip()
            # device_index = int(choice) - 1
            device_index = 0

            if 0 <= device_index < len(self.devices):
                self.selected_device = self.devices[device_index]
                self.device_type = self.selected_device["type"]
                print(f"✅ Selected: {self.selected_device['name']}")
                return True
            else:
                print("❌ Invalid selection")
                return False
        except ValueError:
            print("❌ Please enter a valid number")
            return False

    # async def send_command(self, cook: BaseModel):
    #     """Send command to device"""
    #     try:
    #         await self.websocket.send(cook.model_dump(mode="json"))
    #         print("💡 Response will appear in message stream (option 1)")
    #     except Exception as e:
    #         print(f"❌ Error sending command: {e}")

    async def send_command_and_wait_for_response(self, command_data: BaseModel, timeout=10, show_timeout_warning=False):
        """Send command and wait for RESPONSE message"""
        try:
            # Record message count before sending
            initial_count = len(self.message_history)

            # Send the command
            await self.websocket.send(command_data.model_dump_json(exclude_none=True))
            print(f"📤 Sent command: {command_data.model_dump_json(exclude_none=True)}")
            print("⏳ Waiting for response...")

            # Show timeout warning if requested
            if show_timeout_warning:
                print("⚠️ This command can take up to 30 seconds to receive a response")

            # Wait for RESPONSE messages with timeout
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                # Check for new messages since we sent the command
                if len(self.message_history) > initial_count:
                    new_messages = self.message_history[initial_count:]

                    # Look for RESPONSE commands in new messages
                    for msg in new_messages:
                        data = msg["data"]
                        command = data.get("command", "")

                        # Check if this is a response message (not a state update)
                        if command.startswith("RESPONSE") or \
                           (command.startswith("CMD_") and not command.startswith("CMD_STATE")) or \
                           command == "EVENT_EXPORT_READY":

                            print("\n📨 Response received:")
                            print("-" * 40)
                            self.display_formatted_message(msg)
                            print("-" * 40)
                            return True

                await asyncio.sleep(0.1)

            # Timeout reached
            print(f"⏰ No response received within {timeout} seconds")
            return False

        except Exception as e:
            print(command_data.model_dump_json(exclude_none=True))
            print(f"❌ Error sending command: {e}")
            return False

    def generate_uuid(self):
        """Generate a UUID for requests"""
        return str(uuid.uuid4())

    async def stop_device(self):
        """Stop cooking on selected device"""
        # if self.device_type == "APC":
        #     command = {
        #         "command": "CMD_APC_STOP",
        #         "requestId": self.generate_uuid(),
        #         "payload": {
        #             "cookerId": self.selected_device["id"],
        #             "type": self.selected_device["device_type"]
        #         }
        #     }
        # else:  # APO
        #     command = {
        #         "command": "CMD_APO_STOP",
        #         "payload": {
        #             "id": self.selected_device["id"],
        #             "type": "CMD_APO_STOP"
        #         },
        #         "requestId": self.generate_uuid()
        #     }

        await self.send_command_and_wait_for_response(commands.Command.stop(self.selected_device["id"]))

    # async def set_temperature_unit(self):
    #     """Set temperature unit (C or F)"""
    #     unit = input("Enter temperature unit (C/F): ").upper().strip()
    #     if unit not in ["C", "F"]:
    #         print("❌ Invalid unit. Use C or F")
    #         return
    #
    #     if self.device_type == "APC":
    #         command = {
    #             "command": "CMD_APC_SET_TEMPERATURE_UNIT",
    #             "requestId": self.generate_uuid(),
    #             "payload": {
    #                 "cookerId": self.selected_device["id"],
    #                 "type": self.selected_device["device_type"],
    #                 "unit": unit
    #             }
    #         }
    #     else:  # APO
    #         command = {
    #             "command": "CMD_APO_SET_TEMPERATURE_UNIT",
    #             "payload": {
    #                 "id": self.selected_device["id"],
    #                 "payload": {
    #                     "temperatureUnit": unit
    #                 },
    #                 "type": "CMD_APO_SET_TEMPERATURE_UNIT"
    #             },
    #             "requestId": self.generate_uuid()
    #         }
    #
    #     result = await self.send_command_and_wait_for_response(command)
    #     if result:
    #         self.temperature_unit = unit
    #         print(f"✅ Temperature unit preference saved: {unit}")

    async def close(self):
        """Close websocket connection"""
        print("🔄 Cleaning up connections...")

        # Cancel background listener task
        if self.listener_task and not self.listener_task.done():
            print("🛑 Stopping background listener...")
            self.listener_task.cancel()
            try:
                await asyncio.wait_for(self.listener_task, timeout=2.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass

        # Close websocket connection
        if self.websocket:
            print("🔌 Closing websocket...")
            try:
                await self.websocket.close()
            except Exception as e:
                print(f"⚠️ Error closing websocket: {e}")

        print("✅ Cleanup complete")
    def display_formatted_message(self, msg):
        """Format and display a single message"""
        timestamp = msg["timestamp"]
        data = msg["data"]
        command = data.get("command", "UNKNOWN")

        # Format different message types
        if command.startswith("EVENT_"):
            if "STATE" in command:
                # State messages - show full state
                payload = data.get("payload", {})
                if isinstance(payload, dict):
                    temp = payload.get("temperature", "N/A")
                    status = payload.get("status", payload.get("state", "N/A"))
                    if temp != "N/A" and isinstance(temp, (int, float)):
                        if self.temperature_unit == "F":
                            temp_display = f"{temp * 9/5 + 32:.1f}°F"
                        else:
                            temp_display = f"{temp}°C"
                    else:
                        temp_display = "N/A"
                    print(f"[{timestamp}] STATE: Temp: {temp_display}, Status: {status}")
                else:
                    print(f"[{timestamp}] {command}: {payload}")
            else:
                # Other events
                print(f"[{timestamp}] EVENT: {command}")
        elif command.startswith("RESPONSE"):
            # Command responses - show full response
            payload = data.get("payload", {})
            print(f"[{timestamp}] RESPONSE: {command} - {payload}")
        elif command.startswith("CMD_"):
            # Command responses - show full response
            payload = data.get("payload", {})
            print(f"[{timestamp}] RESPONSE: {command} - {payload}")
        else:
            # Unknown format - show raw
            print(f"[{timestamp}] RAW: {command}")

        # Add newline between messages
        print()
