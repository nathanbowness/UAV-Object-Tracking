# Video Processing

!!! note
    All options below, will assume you have pulled the docker image, and tagged it as `tracking-image` to simplify the following commands (so they're not platform dependant). Please see the [docker quickstart](./runningInDocker.md) section for more details.

To run only the Radar processing section of the `tracking` program, you can disable video processing. This can be beneficial if you only want to collect radar data, or do not have a video source available.

This will walk you through how to modify the container running tracking, but also applied to the local developer environment as well.

### Running ONLY Video Processing
This configuration is useful if you'd only like to collect video data, and are not worried about tracking anything. This is useful for testing video data collection and ensure the model is running. It's also useful to see the Yolo performance by itself

1.  Run the Container Interactively
``` bash
docker run -it tracking-image
```

2. Run the tracking program, with radar processing and all tracking disabled.
```bash
python3 tracking.py --skip-radar --skip-tracking
```

### Running with Video and Tracking Processing
This configuration is useful if you'd only like to collect video data and see how it influences the tracking.

1.  Run the Container Interactively
``` bash
docker run -it tracking-image
```

2. Run the tracking program, with video processing and radar tracking disabled.
```bash
python3 tracking.py --skip-radar
```

## Disable Saving Video Data
When running the tracking program, include the `--disable-save-video` option.
```bash
python3 tracking.py --disable-save-video
```