import sounddevice as sd
import sys

def list_audio_devices():
    """
    Lists all available audio input devices (microphones).
    """
    print("--- Available Audio Input Devices ---")
    try:
        devices = sd.query_devices()
        input_devices_found = False
        for i, device in enumerate(devices):
            # Check if the device has input channels
            if device['max_input_channels'] > 0:
                print(f"Device ID: {i}, Name: {device['name']}")
                input_devices_found = True
        
        if not input_devices_found:
            print("\n❌ No input devices found!")
            print("Please check your microphone connection and system settings.")
        else:
             print("\n--- Instructions ---")
             print("1. Identify your main microphone in the list above (e.g., 'Microphone (Realtek Audio)', 'USB Mic', etc.).")
             print("2. Note its 'Device ID' (the number).")
             print("3. Open 'main.py' and set the 'MIC_DEVICE_ID' variable to this number.")

    except Exception as e:
        print(f"Error querying devices: {e}")
        if 'PortAudio' in str(e):
             print("\nHint: A 'PortAudio' error often means your audio drivers are in use or need an update.")

if __name__ == "__main__":
    list_audio_devices()
