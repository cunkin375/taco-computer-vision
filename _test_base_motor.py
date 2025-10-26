
from pybricks.hubs import InventorHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Stop

hub = InventorHub()
motor_base = Motor(Port.A)

SPEED = 1000
BASE_MIN = -90
BASE_MAX = 90

print("Testing BASE motor...")
print(f"Current angle: {motor_base.angle()}")

# Move base by +20 degrees
current = motor_base.angle()
target = current + 20
if target > BASE_MAX:
    target = BASE_MAX

print(f"Moving from {current} to {target} degrees...")
motor_base.run_target(SPEED, target, Stop.HOLD, wait=True)

print(f"Final angle: {motor_base.angle()}")
print("Done!")
