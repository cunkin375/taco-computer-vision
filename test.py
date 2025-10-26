from pybricks.hubs import InventorHub
from pybricks.tools import wait

hub = InventorHub()
print("Hub connected!")
for i in range(10):
    print(f"Still running... {i}")
    wait(1000)
print("Test complete!")