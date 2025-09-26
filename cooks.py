
async def start_sous_vide_cook(self):
    """Start cooking on APC device"""
    try:
        temp_unit = self.temperature_unit
        max_temp = 95 if temp_unit == "C" else 203
        temp = float(input(f"Enter target temperature (°{temp_unit}, max {max_temp}): "))

        if temp_unit == "C" and temp > 95:
            print("❌ Temperature too high. Maximum is 95°C for sous vide.")
            return
        elif temp_unit == "F" and temp > 203:
            print("❌ Temperature too high. Maximum is 203°F for sous vide.")
            return

        timer_minutes = float(input("Enter cook time (minutes): "))
        timer_seconds = int(timer_minutes * 60)

        temp_celsius = temp if temp_unit == "C" else (temp - 32) * 5/9

        command = {
            "command": "CMD_APC_START",
            "requestId": self.generate_uuid(),
            "payload": {
                "cookerId": self.selected_device["id"],
                "type": self.selected_device["device_type"],
                "targetTemperature": temp_celsius,
                "unit": "C",
                "timer": timer_seconds
            }
        }

        await self.send_command_and_wait_for_response(command)
    except ValueError:
        print("❌ Invalid input. Please enter numeric values.")

async def start_oven_sous_vide(self):
    """Start sous vide cooking on APO device"""
    try:
        temp_unit = self.temperature_unit
        max_temp = 100 if temp_unit == "C" else 212
        temp = float(input(f"Enter target temperature (°{temp_unit}, max {max_temp}): "))

        if temp_unit == "C" and temp > 100:
            print("❌ Temperature too high. Maximum is 100°C for wet bulb sous vide.")
            return
        elif temp_unit == "F" and temp > 212:
            print("❌ Temperature too high. Maximum is 212°F for wet bulb sous vide.")
            return

        timer_minutes = float(input("Enter cook time (minutes): "))
        timer_seconds = int(timer_minutes * 60)

        temp_celsius = temp if temp_unit == "C" else (temp - 32) * 5/9

        command = {
            "command": "CMD_APO_START",
            "payload": {
                "id": self.selected_device["id"],
                "payload": {
                    "stages": [
                        {
                            "id": self.generate_uuid(),
                            "do": {
                                "type": "cook",
                                "fan": {
                                    "speed": 100
                                },
                                "heatingElements": {
                                    "top": {"on": False},
                                    "bottom": {"on": False},
                                    "rear": {"on": True}
                                },
                                "exhaustVent": {
                                    "state": "closed"
                                },
                                "steamGenerators": {
                                    "mode": "relative-humidity",
                                    "relativeHumidity": {
                                        "setpoint": 100
                                    }
                                },
                                "temperatureBulbs": {
                                    "mode": "wet",
                                    "wet": {
                                        "setpoint": {
                                            "celsius": temp_celsius
                                        }
                                    }
                                },
                                "timer": {
                                    "initial": timer_seconds
                                }
                            },
                            "exit": {
                                "conditions": {
                                    "and": {
                                        "nodes.timer.mode": {
                                            "=": "completed"
                                        }
                                    }
                                }
                            },
                            "title": "",
                            "description": "",
                            "rackPosition": 3
                        }
                    ],
                    "cookId": self.generate_uuid(),
                    "cookerId": self.selected_device["id"],
                    "cookableId": "",
                    "title": "",
                    "type": self.selected_device["device_type"],
                    "originSource": "api",
                    "cookableType": "manual"
                },
                "type": "CMD_APO_START"
            },
            "requestId": self.generate_uuid()
        }

        await self.send_command_and_wait_for_response(command)
    except ValueError:
        print("❌ Invalid input. Please enter numeric values.")

async def start_oven_sous_vide_v1(self):
    """Start sous vide cooking on APO v1 device"""
    try:
        temp_f = float(input("Enter target temperature (°F, max 212): "))
        if temp_f > 212:
            print("❌ Temperature too high. Maximum is 212°F for wet bulb sous vide.")
            return
        temp_c = (temp_f - 32) * 5/9

        command = {
            "command": "CMD_APO_START",
            "payload": {
                "id": self.selected_device["id"],
                "payload": {
                    "cookId": self.generate_uuid(),
                    "stages": [
                        {
                            "stepType": "stage",
                            "id": self.generate_uuid(),
                            "title": "",
                            "description": "",
                            "type": "preheat",
                            "userActionRequired": False,
                            "temperatureBulbs": {
                                "mode": "wet",
                                "wet": {
                                    "setpoint": {
                                        "celsius": temp_c,
                                        "fahrenheit": temp_f
                                    }
                                }
                            },
                            "heatingElements": {
                                "top": {"on": False},
                                "bottom": {"on": False},
                                "rear": {"on": True}
                            },
                            "fan": {"speed": 100},
                            "vent": {"open": False},
                            "rackPosition": 3,
                            "stageTransitionType": "automatic",
                            "steamGenerators": {
                                "mode": "relative-humidity",
                                "relativeHumidity": {"setpoint": 100}
                            }
                        },
                        {
                            "stepType": "stage",
                            "id": self.generate_uuid(),
                            "title": "",
                            "description": "",
                            "type": "cook",
                            "userActionRequired": False,
                            "temperatureBulbs": {
                                "mode": "wet",
                                "wet": {
                                    "setpoint": {
                                        "celsius": temp_c,
                                        "fahrenheit": temp_f
                                    }
                                }
                            },
                            "heatingElements": {
                                "top": {"on": False},
                                "bottom": {"on": False},
                                "rear": {"on": True}
                            },
                            "fan": {"speed": 100},
                            "vent": {"open": False},
                            "rackPosition": 3,
                            "stageTransitionType": "automatic",
                            "steamGenerators": {
                                "mode": "relative-humidity",
                                "relativeHumidity": {"setpoint": 100}
                            }
                        }
                    ]
                },
                "type": "CMD_APO_START"
            },
            "requestId": self.generate_uuid()
        }

        await self.send_command_and_wait_for_response(command)
    except ValueError:
        print("❌ Invalid input. Please enter numeric values.")

async def start_oven_roast(self):
    """Start roasting on APO device"""
    try:
        temp_unit = self.temperature_unit
        max_temp = 250 if temp_unit == "C" else 482
        temp = float(input(f"Enter roasting temperature (°{temp_unit}, max {max_temp}): "))

        if temp_unit == "C" and temp > 250:
            print("❌ Temperature too high. Maximum is 250°C for roasting.")
            return
        elif temp_unit == "F" and temp > 482:
            print("❌ Temperature too high. Maximum is 482°F for roasting.")
            return

        timer_minutes = float(input("Enter cook time (minutes): "))
        timer_seconds = int(timer_minutes * 60)

        temp_celsius = temp if temp_unit == "C" else (temp - 32) * 5/9

        command = {
            "command": "CMD_APO_START",
            "payload": {
                "id": self.selected_device["id"],
                "payload": {
                    "stages": [
                        {
                            "id": self.generate_uuid(),
                            "do": {
                                "type": "cook",
                                "fan": {
                                    "speed": 75
                                },
                                "heatingElements": {
                                    "top": {"on": False},
                                    "bottom": {"on": True},
                                    "rear": {"on": True}
                                },
                                "exhaustVent": {
                                    "state": "closed"
                                },
                                "temperatureBulbs": {
                                    "mode": "dry",
                                    "dry": {
                                        "setpoint": {
                                            "celsius": temp_celsius
                                        }
                                    }
                                },
                                "timer": {
                                    "initial": timer_seconds
                                }
                            },
                            "exit": {
                                "conditions": {
                                    "and": {
                                        "nodes.timer.mode": {
                                            "=": "completed"
                                        }
                                    }
                                }
                            },
                            "title": "",
                            "description": "",
                            "rackPosition": 3
                        }
                    ],
                    "cookId": self.generate_uuid(),
                    "cookerId": self.selected_device["id"],
                    "cookableId": "",
                    "title": "",
                    "type": self.selected_device["device_type"],
                    "originSource": "api",
                    "cookableType": "manual"
                },
                "type": "CMD_APO_START"
            },
            "requestId": self.generate_uuid()
        }

        await self.send_command_and_wait_for_response(command)
    except ValueError:
        print("❌ Invalid input. Please enter numeric values.")

async def start_oven_roast_v1(self):
    """Start roasting on APO v1 device"""
    try:
        temp_f = float(input("Enter roasting temperature (°F, max 482): "))
        if temp_f > 482:
            print("❌ Temperature too high. Maximum is 482°F for roasting.")
            return
        temp_c = (temp_f - 32) * 5/9

        command = {
            "command": "CMD_APO_START",
            "payload": {
                "id": self.selected_device["id"],
                "payload": {
                    "cookId": self.generate_uuid(),
                    "stages": [
                        {
                            "stepType": "stage",
                            "id": self.generate_uuid(),
                            "title": "",
                            "description": "",
                            "type": "preheat",
                            "userActionRequired": False,
                            "temperatureBulbs": {
                                "mode": "dry",
                                "dry": {
                                    "setpoint": {
                                        "celsius": temp_c,
                                        "fahrenheit": temp_f
                                    }
                                }
                            },
                            "heatingElements": {
                                "top": {"on": False},
                                "bottom": {"on": True},
                                "rear": {"on": True}
                            },
                            "fan": {"speed": 75},
                            "vent": {"open": False},
                            "rackPosition": 3,
                            "stageTransitionType": "automatic"
                        },
                        {
                            "stepType": "stage",
                            "id": self.generate_uuid(),
                            "title": "",
                            "description": "",
                            "type": "cook",
                            "userActionRequired": False,
                            "temperatureBulbs": {
                                "mode": "dry",
                                "dry": {
                                    "setpoint": {
                                        "celsius": temp_c,
                                        "fahrenheit": temp_f
                                    }
                                }
                            },
                            "heatingElements": {
                                "top": {"on": False},
                                "bottom": {"on": True},
                                "rear": {"on": True}
                            },
                            "fan": {"speed": 75},
                            "vent": {"open": False},
                            "rackPosition": 3,
                            "stageTransitionType": "automatic"
                        }
                    ]
                },
                "type": "CMD_APO_START"
            },
            "requestId": self.generate_uuid()
        }

        await self.send_command_and_wait_for_response(command)
    except ValueError:
        print("❌ Invalid input. Please enter numeric values.")

async def start_oven_steam(self):
    """Start steam cooking on APO device"""
    try:
        temp_unit = self.temperature_unit
        max_temp = 250 if temp_unit == "C" else 482
        temp = float(input(f"Enter temperature (°{temp_unit}, max {max_temp}): "))

        if temp_unit == "C" and temp > 250:
            print("❌ Temperature too high. Maximum is 250°C for steam cooking.")
            return
        elif temp_unit == "F" and temp > 482:
            print("❌ Temperature too high. Maximum is 482°F for steam cooking.")
            return

        humidity = int(input("Enter humidity percentage (0-100): "))
        if humidity < 0 or humidity > 100:
            print("❌ Humidity must be between 0-100%.")
            return
        timer_minutes = float(input("Enter cook time (minutes): "))
        timer_seconds = int(timer_minutes * 60)

        temp_celsius = temp if temp_unit == "C" else (temp - 32) * 5/9

        command = {
            "command": "CMD_APO_START",
            "payload": {
                "id": self.selected_device["id"],
                "payload": {
                    "stages": [
                        {
                            "id": self.generate_uuid(),
                            "do": {
                                "type": "cook",
                                "fan": {
                                    "speed": 100
                                },
                                "heatingElements": {
                                    "top": {"on": False},
                                    "bottom": {"on": True},
                                    "rear": {"on": True}
                                },
                                "exhaustVent": {
                                    "state": "closed"
                                },
                                "temperatureBulbs": {
                                    "mode": "dry",
                                    "dry": {
                                        "setpoint": {
                                            "celsius": temp_celsius
                                        }
                                    }
                                },
                                "steamGenerators": {
                                    "mode": "relative-humidity",
                                    "relativeHumidity": {
                                        "setpoint": humidity
                                    }
                                },
                                "timer": {
                                    "initial": timer_seconds
                                }
                            },
                            "exit": {
                                "conditions": {
                                    "and": {
                                        "nodes.timer.mode": {
                                            "=": "completed"
                                        }
                                    }
                                }
                            },
                            "title": "",
                            "description": "",
                            "rackPosition": 3
                        }
                    ],
                    "cookId": self.generate_uuid(),
                    "cookerId": self.selected_device["id"],
                    "cookableId": "",
                    "title": "",
                    "type": self.selected_device["device_type"],
                    "originSource": "api",
                    "cookableType": "manual"
                },
                "type": "CMD_APO_START"
            },
            "requestId": self.generate_uuid()
        }

        await self.send_command_and_wait_for_response(command)
    except ValueError:
        print("❌ Invalid input. Please enter numeric values.")

async def start_oven_steam_v1(self):
    """Start steam cooking on APO v1 device"""
    try:
        temp_f = float(input("Enter temperature (°F, max 482): "))
        if temp_f > 482:
            print("❌ Temperature too high. Maximum is 482°F for steam cooking.")
            return
        temp_c = (temp_f - 32) * 5/9
        humidity = int(input("Enter humidity percentage (0-100): "))
        if humidity < 0 or humidity > 100:
            print("❌ Humidity must be between 0-100%.")
            return

        command = {
            "command": "CMD_APO_START",
            "payload": {
                "id": self.selected_device["id"],
                "payload": {
                    "cookId": self.generate_uuid(),
                    "stages": [
                        {
                            "stepType": "stage",
                            "id": self.generate_uuid(),
                            "title": "",
                            "description": "",
                            "type": "preheat",
                            "userActionRequired": False,
                            "temperatureBulbs": {
                                "mode": "dry",
                                "dry": {
                                    "setpoint": {
                                        "celsius": temp_c,
                                        "fahrenheit": temp_f
                                    }
                                }
                            },
                            "heatingElements": {
                                "top": {"on": True},
                                "bottom": {"on": True},
                                "rear": {"on": True}
                            },
                            "fan": {"speed": 50},
                            "vent": {"open": False},
                            "rackPosition": 3,
                            "stageTransitionType": "automatic",
                            "steamGenerators": {
                                "mode": "relative-humidity",
                                "relativeHumidity": {"setpoint": humidity}
                            }
                        },
                        {
                            "stepType": "stage",
                            "id": self.generate_uuid(),
                            "title": "",
                            "description": "",
                            "type": "cook",
                            "userActionRequired": False,
                            "temperatureBulbs": {
                                "mode": "dry",
                                "dry": {
                                    "setpoint": {
                                        "celsius": temp_c,
                                        "fahrenheit": temp_f
                                    }
                                }
                            },
                            "heatingElements": {
                                "top": {"on": True},
                                "bottom": {"on": True},
                                "rear": {"on": True}
                            },
                            "fan": {"speed": 50},
                            "vent": {"open": False},
                            "rackPosition": 3,
                            "stageTransitionType": "automatic",
                            "steamGenerators": {
                                "mode": "relative-humidity",
                                "relativeHumidity": {"setpoint": humidity}
                            }
                        }
                    ]
                },
                "type": "CMD_APO_START"
            },
            "requestId": self.generate_uuid()
        }

        await self.send_command_and_wait_for_response(command)
    except ValueError:
        print("❌ Invalid input. Please enter numeric values.")

async def export_telemetry(self):
    """Export telemetry data from device"""
    print("📊 Export telemetry data")
    print("Note: Date range cannot exceed 14 days, and start date cannot be more than 90 days in the past")

    try:
        start_date = input("Enter start date (YYYY-MM-DD): ").strip()
        end_date = input("Enter end date (YYYY-MM-DD): ").strip()

        # Validate date format
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")

        command = {
            "command": "CMD_EXPORT_TELEMETRY",
            "requestId": self.generate_uuid(),
            "payload": {
                "id": self.generate_uuid(),
                "type": "CMD_EXPORT_TELEMETRY",
                "payload": {
                    "deviceId": self.selected_device["id"],
                    "startTime": start_date,
                    "endTime": end_date
                }
            }
        }

        await self.send_command_and_wait_for_response(command, timeout=30, show_timeout_warning=True)
    except ValueError:
        print("❌ Invalid date format. Use YYYY-MM-DD")

async def show_message_stream(self):
    print("Message History")
    print("=" * 60)

    # Show recent message history first
    if self.message_history:
        recent_messages = self.message_history[-10:]  # Show last 10 messages
        for msg in recent_messages:
            self.display_formatted_message(msg)

    print("=" * 60)
    print("🔴 LIVE - New messages will appear below - Press Enter to return to menu")

    # Track the last message count to detect new messages
    last_count = len(self.message_history)

    # Create concurrent tasks for message monitoring and user input
    async def monitor_messages():
        nonlocal last_count
        while True:
            current_count = len(self.message_history)
            if current_count > last_count:
                # Display new messages
                new_messages = self.message_history[last_count:]
                for msg in new_messages:
                    self.display_formatted_message(msg)
                last_count = current_count
            await asyncio.sleep(0.1)

    async def wait_for_user_input():
        loop = asyncio.get_event_loop()
        # Use run_in_executor to make input() non-blocking
        await loop.run_in_executor(None, input)

    # Run both tasks concurrently, return when user input is received
    monitor_task = asyncio.create_task(monitor_messages())
    input_task = asyncio.create_task(wait_for_user_input())

    try:
        # Wait for user to press Enter
        await input_task
    except KeyboardInterrupt:
        pass
    finally:
        # Cancel the monitoring task
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

    print("Exiting message stream...")


async def show_menu(self):
    """Show command menu based on device type"""
    if self.device_type == "APC":
        print(f"\n🍳 Commands for {self.selected_device['name']} (Sous Vide):")
        print("1. Show message stream")
        print("2. Start sous vide cook")
        print("3. Stop cooking")
        print("4. Set temperature unit")
        print("5. Export telemetry data")
        print("0. Exit")
    else:  # APO
        print(f"\n🔥 Commands for {self.selected_device['name']} (Oven):")
        print("1. Show message stream")
        print("2. Start sous vide cook (wet bulb)")
        print("3. Start roasting (dry bulb)")
        print("4. Start steam cooking")
        print("5. Stop cooking")
        print("6. Set temperature unit")
        print("7. Export telemetry data")
        print("0. Exit")

async def handle_menu_choice(self, choice):
    """Handle user menu selection"""
    if self.device_type == "APC":
        if choice == "1":
            await self.show_message_stream()
            return "no_pause"  # Special return value to skip "Press Enter"
        elif choice == "2":
            await self.start_sous_vide_cook()
        elif choice == "3":
            await self.stop_device()
        elif choice == "4":
            await self.set_temperature_unit()
        elif choice == "5":
            await self.export_telemetry()
        elif choice == "0":
            return False
        else:
            print("❌ Invalid choice")
    else:  # APO
        if choice == "1":
            await self.show_message_stream()
            return "no_pause"  # Special return value to skip "Press Enter"
        elif choice == "2":
            # Use v1 or v2 commands based on device_type
            if self.selected_device["device_type"] == "oven_v2":
                await self.start_oven_sous_vide()
            else:
                await self.start_oven_sous_vide_v1()
        elif choice == "3":
            # Use v1 or v2 commands based on device_type
            if self.selected_device["device_type"] == "oven_v2":
                await self.start_oven_roast()
            else:
                await self.start_oven_roast_v1()
        elif choice == "4":
            # Use v1 or v2 commands based on device_type
            if self.selected_device["device_type"] == "oven_v2":
                await self.start_oven_steam()
            else:
                await self.start_oven_steam_v1()
        elif choice == "5":
            await self.stop_device()
        elif choice == "6":
            await self.set_temperature_unit()
        elif choice == "7":
            await self.export_telemetry()
        elif choice == "0":
            return False
        else:
            print("❌ Invalid choice")

    return True

async def run_interactive_menu(self):
    """Run the interactive menu loop"""
    try:
        while True:
            await self.show_menu()
            choice = input("\nSelect option: ").strip()

            result = await self.handle_menu_choice(choice)
            if result == False:
                print("👋 Exiting...")
                break
            elif result == "no_pause":
                # Skip the "Press Enter to continue" for message stream
                continue
            else:
                # Normal pause for other commands
                input("\nPress Enter to continue...")
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"❌ Menu error: {e}")
    finally:
        # Ensure cleanup happens
        await self.close()

