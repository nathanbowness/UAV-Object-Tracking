# Connect a Webcam (Windows Machine)
Since this project is expected to run in a Developer Container, the container must have access to a webcam to properly work.

On windows the main way to run developer containers is to run them using WSL. Therefore the webcam must be accessible to your WSL instance. To do this, follow the instructions below. More details can be found on this webpage - [Microsoft - Connect USB Devices to WSL](https://learn.microsoft.com/en-us/windows/wsl/connect-usb#attach-a-usb-device)

1. List all USB devices connected to Windows by openning powershell in Admin mode and entering this command:
  ```usbipd list```
2. Before attaching the USB device, the command usbipd bind must be used to share the device, allowing it to be attached to WSL. Select the bus ID of the device you would like to use in WSL and run the following command:
  ```usbipd bind --busid 4-4```
3. To attach the USB device, run the following command. (You no longer need to use an elevated administrator prompt.) Ensure that a WSL command prompt is open in order to keep the WSL 2 lightweight VM active: 
  ```usbipd attach --wsl --busid <busid>```
4. Open Ubuntu (or your preferred WSL command line) and list the attached USB devices using the command:
  ```lsusb```
5. Once you are done using the device in WSL, you can either physically disconnect the USB device or run this command from PowerShell:
  ```usbipd detach --busid <busid>```