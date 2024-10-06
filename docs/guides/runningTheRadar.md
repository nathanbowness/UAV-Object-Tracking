# Radar Processing

!!! note
    All options below, will assume you have pulled the docker image, and tagged it as `tracking-image` to simplify the following commands (so they're not platform dependant). Please see the [docker quickstart](./runningInDocker.md) section for more details.

To run only the Radar processing section of the `tracking` program, you can disable video processing. This can be beneficial if you only want to collect radar data, or do not have a video source available.

This will walk you through how to modify the container running tracking, but also applied to the local developer environment as well.

### Running ONLY Radar Processing
This configuration is useful if you'd only like to collect Radar data, and are not worried about tracking anything. This is useful for testing radar data collection.

1.  Run the Container Interactively
``` bash
docker run -it tracking-image
```

2. Run the tracking program, with video processing and radar tracking disabled.
```bash
python3 tracking.py --skip-video --skip-tracking
```

### Running with Radar and Tracking Processing
This configuration is useful if you'd only like to collect Radar data and see how it influences the tracking.

1.  Run the Container Interactively
``` bash
docker run -it tracking-image
```

2. Run the tracking program, with video processing and radar tracking disabled.
```bash
python3 tracking.py --skip-video
```

## Disable Saving Radar Data
When running the tracking program, include the `--disable-record`.
```bash
python3 tracking.py --disable-record
```
