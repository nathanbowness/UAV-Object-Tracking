Scratch pad of commands for various issues.
```
export QT_QPA_PLATFORM=offscreen
sudo apt-get install python3-tk

# Debugging
pip uninstall opencv-python
pip install opencv-python-headless
# Fix issues
export QT_QPA_PLATFORM=offscreen
apt install libxcb-cursor0 # / Maybe??

python tracking.py --radar-only
python tracking.py --video-only
python tracking.py --show-plots
```