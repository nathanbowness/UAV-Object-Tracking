# Using Webcam in a Container
You may want to use a local webcam for the video processing or calibration.

## Connect a Webcam to WSL (Windows Machine)
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

### Test the Camera
You can test the camera is mounted to WSL and working by running this command
```
apt-get install ffmpeg
ffmpeg -f v4l2 -framerate 1 -video_size 640x480 -i /dev/video0 -vframes 1 output_image.jpg
```

## Mount the Camera to the Container
Mount the camera from your computer to video0 of the container to easily use it. Add the following line to your docker run command:
```
# Command: --device=<path-to-video-device>:/dev/video0"
# Example:
--device=/dev/video0:/dev/video0
```
