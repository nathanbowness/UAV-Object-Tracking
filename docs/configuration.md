
The Ultralytics image was used as the base image for this project. It includes the requried GPU tools to run yolo, and was easy to modify so it was used as a base image.

The configuration, data, output and tracking directories are added to the image after it's built for this project. Each of those sections is described in below.
* **Data** - Directory recomended for the user to mount pre-recorded data/samples to run the tracking algorithm against. This is configurable, but this is shown as a placeholder.
* **Configuration** - Directory that contains the required configuration files for the application to run. If not configured, it will use default configuration.
* **Output** - Output directory where files from tracking will be saved, it is recommeded to mount this directory to a local volume to grab the data for ease.
* **tracking** - directory that contains the additional radar tracking and object tracking pipeline

## Container Structure After Additions

<pre>
|-- bin/
|-- boot/
|-- <b>configuration/</b>
|   |-- <b>RadarConfig.yaml</b>
|   |-- <b>VideoConfig.yaml</b>
|   |-- <b>TrackingConfig.yaml</b>
|-- <b>data/</b>
|   |-- <b>radar</b>
|   |-- <b>video</b>
|-- dev/
|-- etc/
|-- home/
|-- media/
|-- <b>output</b>
|   |-- <b>2024-09-15_21-45-01</b>
|   |-- <b>other-outputs</b>
|-- <b>tracking/</b>
|   |-- <b>UAV-Object-Tracking/</b>
|   |   |-- <b>tracking.py</b>
|-- ultralytics/
|   |-- CITATION.cff
|   |-- CONTRIBUTING.md
|   |-- LICENSE
|   |-- README.md
|   |-- README.zh-CN.md
|   |-- calibration_image_sample_data_20x128x128x3_float32.npy
|   |-- docker/
|   |-- docs/
|   |-- examples/
|   |-- mkdocs.yml
|   |-- pyproject.toml
|   |-- tests/
|   |-- ultralytics/
|   |-- ultralytics.egg-info
|   `-- yolov8n.pt
|-- var/

| <other system unix folders>
</pre>

