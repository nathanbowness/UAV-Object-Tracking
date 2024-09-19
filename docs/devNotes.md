```
export PYTHONPATH="$PYTHONPATH:/workspaces/UAV-Object-Tracking/yolo_video_object_tracking"
export QT_QPA_PLATFORM=offscreen
sudo apt-get install python3-tk

python3 object_tracking.py --weights yolo_video_object_tracking/yolov7.pt --source data/video/M0101.mp4 --conf-thres 0.4 --no-download --view-img

# Run just the radar tracking from recorded data
python3 object_tracking.py --weights yolo_video_object_tracking/yolov7.pt --source data/video/M0101.mp4 --conf-thres 0.4 --no-download --view-img --skip-video --radar-from-file --radar-source data/radar/run1_FD

# Debugging
pip uninstall opencv-python
pip install opencv-python-headless
# Fix issues
export QT_QPA_PLATFORM=offscreen
apt install libxcb-cursor0 # / Maybe??

python object_tracking.py --radar-only
python object_tracking.py --video-only
python object_tracking.py --show-plots
```