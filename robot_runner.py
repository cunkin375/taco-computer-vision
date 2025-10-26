# import sys
# import time
# import subprocess
# from pathlib import Path

# # Absolute path to the commands file on the PC
# COMMANDS_FILE_PATH = Path(r"C:\Users\hackathon\dev\taco\taco-computer-vision\commands.txt")
# # Your hub BLE name as seen by pybricksdev - change if needed
# HUB_NAME = "test"

# # Where to write the temporary action script that will be sent to the hub
# TEMP_SCRIPT_PATH = Path(__file__).parent / "_robot_action_temp.py"


# def _generate_action_script(command: str) -> str:
#     """
#     Returns a single-file Pybricks MicroPython program that:
#     - initializes motors
#     - executes exactly one command (from the PC)
#     - stops and exits
#     This runs ON THE HUB via `pybricksdev run ble ...`.
#     """
#     # Keep this template ASCII-only (no emojis).
#     return f"""\
# from pybricks.hubs import InventorHub
# from pybricks.pupdevices import Motor
# from pybricks.parameters import Port, Stop
# from pybricks.tools import wait

# # ---- Initialize hub and motors ----
# hub = InventorHub()
# motor_base = Motor(Port.A)
# motor_shoulder = Motor(Port.B)
# motor_elbow = Motor(Port.C)
# motor_gripper = Motor(Port.F)

# # ---- Settings ----
# SPEED = 300
# GRIPPER_CLOSE_SPEED = -200
# GRIPPER_OPEN_SPEED = 200
# GRIPPER_DUTY_LIMIT = 50

# # ---- Motor bounds (degrees) ----
# SHOULDER_MIN = 0
# SHOULDER_MAX = 90
# BASE_MIN = -90
# BASE_MAX = 90
# ELBOW_MIN = 0
# ELBOW_MAX = 120
# GRIPPER_OPEN_ANGLE = 60

# # ---- Calibration Routine ----
# def calibrate():
#     print("Calibrating robot...")
#     # Move all motors to their zero/home positions
#     motor_base.run_target(SPEED, 0, Stop.HOLD, wait=True)
#     motor_shoulder.run_target(SPEED, 0, Stop.HOLD, wait=True)
#     motor_elbow.run_target(SPEED, 0, Stop.HOLD, wait=True)
#     motor_gripper.run_target(GRIPPER_OPEN_SPEED, GRIPPER_OPEN_ANGLE, Stop.HOLD, wait=True)
#     print("Calibration complete.")

# # ---- Incremental Movement Function ----
# def move_motor_by(motor, delta, min_angle, max_angle):
#     current_angle = motor.angle()
#     target_angle = current_angle + delta
#     if target_angle > max_angle:
#         target_angle = max_angle
#     elif target_angle < min_angle:
#         target_angle = min_angle
#     print("Moving motor from", current_angle, "to", target_angle, "deg")
#     motor.run_target(SPEED, target_angle, Stop.HOLD, wait=False)
#     wait(50)

# # ---- Run calibration once before command ----
# calibrate()

# # ---- Execute one command ----
# cmd = "{command}".strip()
# print("Executing command:", cmd)
# try:
#     if cmd.upper() == 'SHOULDER_UP':
#         move_motor_by(motor_shoulder, 10, SHOULDER_MIN, SHOULDER_MAX)
#     elif cmd.upper() == 'SHOULDER_DOWN':
#         move_motor_by(motor_shoulder, -10, SHOULDER_MIN, SHOULDER_MAX)
#     else:
#         parts = cmd.split(':')
#         if len(parts) >= 2:
#             name = parts[0].upper()
#             try:
#                 delta = int(parts[1])
#             except Exception:
#                 print("Invalid delta in command:", cmd)
#                 delta = None
#             if delta is not None:
#                 if name == 'BASE':
#                     move_motor_by(motor_base, delta, BASE_MIN, BASE_MAX)
#                 elif name == 'SHOULDER':
#                     move_motor_by(motor_shoulder, delta, SHOULDER_MIN, SHOULDER_MAX)
#                 elif name == 'ELBOW':
#                     move_motor_by(motor_elbow, delta, ELBOW_MIN, ELBOW_MAX)
#                 elif name == 'GRIPPER':
#                     if delta > 0:
#                         print("Gripper: Opening")
#                         motor_gripper.run_target(GRIPPER_OPEN_SPEED, GRIPPER_OPEN_ANGLE, Stop.HOLD, wait=False)
#                     else:
#                         print("Gripper: Closing until stalled")
#                         motor_gripper.run_until_stalled(GRIPPER_CLOSE_SPEED, then=Stop.HOLD, duty_limit=GRIPPER_DUTY_LIMIT)
#                 else:
#                     print("Unknown motor:", name)
#         else:
#             print("Unrecognized command format:", cmd)
# except Exception as e:
#     print("Error processing command:", e)

# # Ensure motors are stopped before exit
# try:
#     motor_base.stop(); motor_shoulder.stop(); motor_elbow.stop(); motor_gripper.stop()
# except Exception:
#     pass
# print("Done")
# """


# def _run_command_on_hub(cmd: str) -> int:
#     """Writes a temp script for the given command and runs it via pybricksdev.
#     Returns the process return code.
#     """
#     # Write the temporary script
#     TEMP_SCRIPT_PATH.write_text(_generate_action_script(cmd), encoding="utf-8")

#     run_cmd = [
#         sys.executable,
#         "-m", "pybricksdev",
#         "run", "ble",
#         "-n", HUB_NAME,
#         str(TEMP_SCRIPT_PATH)
#     ]
#     print(f"[Runner] Running on hub: {cmd}")
#     try:
#         proc = subprocess.Popen(
#             run_cmd,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.STDOUT,
#             text=True,
#             bufsize=1,
#         )
#         # Stream output
#         if proc.stdout is not None:
#             for line in proc.stdout:
#                 if line:
#                     print(f"[HUB] {line.rstrip()}")
#         return proc.wait()
#     finally:
#         # Keep the temp script for debugging; comment out to delete automatically
#         # try:
#         #     TEMP_SCRIPT_PATH.unlink(missing_ok=True)
#         # except Exception:
#         #     pass
#         pass


# def main():
#     print(f"[Runner] Watching commands file: {COMMANDS_FILE_PATH}")
#     print(f"[Runner] Hub name: {HUB_NAME}")
#     # Ensure commands file exists
#     COMMANDS_FILE_PATH.touch(exist_ok=True)

#     while True:
#         try:
#             # Read and strip commands
#             lines = [ln.strip() for ln in COMMANDS_FILE_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
#             if lines:
#                 print(f"[Runner] Found {len(lines)} command(s)")
#                 for cmd in lines:
#                     rc = _run_command_on_hub(cmd)
#                     if rc != 0:
#                         print(f"[Runner] Command failed (rc={rc}): {cmd}")
#                         # On failure, stop processing remaining commands to avoid spamming reconnects
#                         break
#                 # Clear file after processing (best effort)
#                 try:
#                     COMMANDS_FILE_PATH.write_text("", encoding="utf-8")
#                 except Exception as e:
#                     print(f"[Runner] Failed to clear commands file: {e}")
#             # Wait 1s between polls
#             time.sleep(1.0)
#         except KeyboardInterrupt:
#             print("[Runner] Stopping")
#             break
#         except Exception as e:
#             print(f"[Runner] Error: {e}")
#             time.sleep(1.0)


# if __name__ == "__main__":
#     main()

from pybricks.hubs import InventorHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait  # Correct import for wait in MicroPython

import os  # Use os module for path management (works in MicroPython)

# Absolute path to the commands file on the PC
COMMANDS_FILE_PATH = r"C:\Users\hackathon\dev\taco\taco-computer-vision\commands.txt"  # Use string paths

# Your hub BLE name as seen by pybricksdev - change if needed
HUB_NAME = "test"

# Where to write the temporary action script that will be sent to the hub
TEMP_SCRIPT_PATH = os.path.join(os.getcwd(), "_robot_action_temp.py")  # os.getcwd() gives the current working directory


def _generate_action_script(command: str) -> str:
    """
    Returns a single-file Pybricks MicroPython program that:
    - initializes motors
    - executes exactly one command (from the PC)
    - stops and exits
    This runs ON THE HUB via `pybricksdev run ble ...`.
    """
    return f"""\
from pybricks.hubs import InventorHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait

# ---- Initialize hub and motors ----
hub = InventorHub()
motor_base = Motor(Port.A)
motor_shoulder = Motor(Port.B)
motor_elbow = Motor(Port.C)
motor_gripper = Motor(Port.F)

# ---- Settings ----
SPEED = 300
GRIPPER_CLOSE_SPEED = -200
GRIPPER_OPEN_SPEED = 200
GRIPPER_DUTY_LIMIT = 50

# ---- Motor bounds (degrees) ----
SHOULDER_MIN = 0
SHOULDER_MAX = 90
BASE_MIN = -90
BASE_MAX = 90
ELBOW_MIN = 0
ELBOW_MAX = 120
GRIPPER_OPEN_ANGLE = 60

# ---- Calibration Routine ----
def calibrate():
    print("Calibrating robot...")
    motor_base.run_target(SPEED, 0, Stop.HOLD, wait=True)
    motor_shoulder.run_target(SPEED, 0, Stop.HOLD, wait=True)
    motor_elbow.run_target(SPEED, 0, Stop.HOLD, wait=True)
    motor_gripper.run_target(GRIPPER_OPEN_SPEED, GRIPPER_OPEN_ANGLE, Stop.HOLD, wait=True)
    print("Calibration complete.")

# ---- Incremental Movement Function ----
def move_motor_by(motor, delta, min_angle, max_angle):
    current_angle = motor.angle()
    target_angle = current_angle + delta
    if target_angle > max_angle:
        target_angle = max_angle
    elif target_angle < min_angle:
        target_angle = min_angle
    print("Moving motor from", current_angle, "to", target_angle, "deg")
    motor.run_target(SPEED, target_angle, Stop.HOLD, wait=False)
    wait(50)  # Use wait() for delay instead of time.sleep()

# ---- Run calibration once before command ----
calibrate()

# ---- Execute one command ----
cmd = "{command}".strip()
print("Executing command:", cmd)
try:
    if cmd.upper() == 'SHOULDER_UP':
        move_motor_by(motor_shoulder, 10, SHOULDER_MIN, SHOULDER_MAX)
    elif cmd.upper() == 'SHOULDER_DOWN':
        move_motor_by(motor_shoulder, -10, SHOULDER_MIN, SHOULDER_MAX)
    else:
        parts = cmd.split(':')
        if len(parts) >= 2:
            name = parts[0].upper()
            try:
                delta = int(parts[1])
            except Exception:
                print("Invalid delta in command:", cmd)
                delta = None
            if delta is not None:
                if name == 'BASE':
                    move_motor_by(motor_base, delta, BASE_MIN, BASE_MAX)
                elif name == 'SHOULDER':
                    move_motor_by(motor_shoulder, delta, SHOULDER_MIN, SHOULDER_MAX)
                elif name == 'ELBOW':
                    move_motor_by(motor_elbow, delta, ELBOW_MIN, ELBOW_MAX)
                elif name == 'GRIPPER':
                    if delta > 0:
                        print("Gripper: Opening")
                        motor_gripper.run_target(GRIPPER_OPEN_SPEED, GRIPPER_OPEN_ANGLE, Stop.HOLD, wait=False)
                    else:
                        print("Gripper: Closing until stalled")
                        motor_gripper.run_until_stalled(GRIPPER_CLOSE_SPEED, then=Stop.HOLD, duty_limit=GRIPPER_DUTY_LIMIT)
                else:
                    print("Unknown motor:", name)
        else:
            print("Unrecognized command format:", cmd)
except Exception as e:
    print("Error processing command:", e)

# Ensure motors are stopped before exit
try:
    motor_base.stop(); motor_shoulder.stop(); motor_elbow.stop(); motor_gripper.stop()
except Exception:
    pass
print("Done")
"""


def _run_command_on_hub(cmd: str) -> int:
    """Writes a temp script for the given command and runs it via pybricksdev."""
    with open(TEMP_SCRIPT_PATH, 'w', encoding='utf-8') as temp_script:
        temp_script.write(_generate_action_script(cmd))

    # Run the command on the LEGO hub
    run_cmd = [
        "pybricksdev",  # Command to run the script on the hub
        "run", "ble",
        "-n", HUB_NAME,
        TEMP_SCRIPT_PATH
    ]
    print(f"[Runner] Running on hub: {cmd}")
    try:
        result = subprocess.run(run_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[Runner] Error: {result.stderr}")
        return result.returncode
    finally:
        pass


def main():
    print(f"[Runner] Watching commands file: {COMMANDS_FILE_PATH}")
    print(f"[Runner] Hub name: {HUB_NAME}")
    # Ensure commands file exists
    if not os.path.exists(COMMANDS_FILE_PATH):
        open(COMMANDS_FILE_PATH, 'w').close()

    while True:
        try:
            # Read and strip commands
            with open(COMMANDS_FILE_PATH, 'r', encoding='utf-8') as f:
                lines = [ln.strip() for ln in f.readlines() if ln.strip()]
            if lines:
                print(f"[Runner] Found {len(lines)} command(s)")
                for cmd in lines:
                    rc = _run_command_on_hub(cmd)
                    if rc != 0:
                        print(f"[Runner] Command failed (rc={rc}): {cmd}")
                        break
                try:
                    with open(COMMANDS_FILE_PATH, 'w', encoding='utf-8') as f:
                        f.truncate(0)  # Clear the file after processing
                except Exception as e:
                    print(f"[Runner] Failed to clear commands file: {e}")
            wait(1000)  # Use wait() for a 1-second delay (in MicroPython)
        except KeyboardInterrupt:
            print("[Runner] Stopping")
            break
        except Exception as e:
            print(f"[Runner] Error: {e}")
            wait(1000)  # Use wait() for a 1-second delay (in MicroPython)


if __name__ == "__main__":
    main()
