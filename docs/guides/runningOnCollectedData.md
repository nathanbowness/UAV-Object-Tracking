# Running on previously collected data

To run the `tracking.py` program on previously recorded data, there are 2 options:

1. Pass the CLI arguments to the program with required details.
2. Mount configuration files for Radar and/or Video processing with required details.

!!! note
    All options below, will assume you have pulled the docker image, and tagged it as `tracking-image` to simplify the following commands (so they're not platform dependant). Please see the [docker quickstart](./runningInDocker.md) section for more details.

## Radar

### Using CLI Arguments to Run on Collected Data
To run on collected data by changing CLI arguments, you can do that following.

1. Run Container with Data Mount
    To access data within the container you'll need to mount the local data into it. This example mounts the pwd/data folder into the /data location in the container. These can both be configured as you'd like.

    === "Linux"

        ``` bash
        docker run -it tracking-image -v "$(pwd)"/data:/data
        ```

    === "Jetson5"

        ``` bash
        docker run --ipc=host --runtime=nvidia -it tracking-image -v "$(pwd)"/data:/data
        ```

2. Run the tracking program, specify the location to the data

    ```bash
    python3 tracking.py --radar-from-file --radar-from-file <path-to-file>
    ```


### Mounting Configuration Files 
Mount the RadarConfig.yaml file to the `/configuration` section of the container when running. You may also want to mount `/data` to the container to easily pass data into it.

1. Running Container with Configuration/Data Mounts


    === "Linux"

        ``` bash
        docker run -it tracking-image -v "$(pwd)"/configuration:/configuration -v "$(pwd)"/data:/data
        ```

    === "Jetson5"

        ``` bash
        docker run --ipc=host --runtime=nvidia -it tracking-image -v "$(pwd)"/configuration:/configuration -v "$(pwd)"/data:/data
        ```

2. Modify these 2 settings in the `RadarConfig.yaml` configuration file

    ``` yaml 
    # Run configuration
    run: RERUN # Changed to RERUN
    sourcePath: "/data/radar/run2-TD/" # Path to the data to be processed for RERUN mode
    ```

    For full details on the RadarConfig.yaml file please see the [configuration](../configuration/configuration.md) section.

3. Run the tracking program, specify the configuration file location. By default it's set to `/configuration/RadarConfig.yaml`.

    ```bash
    python3 tracking.py --radar-config <path-to-config-file>
    ```

## Video

### CLI Arguments to Run on Collected Data

1. Run Container with Data Mount
    To access data within the container you'll need to mount the local data into it. This example mounts the pwd/data folder into the /data location in the container. These can both be configured as you'd like.

    === "Linux"

        ``` bash
        docker run -it tracking-image -v "$(pwd)"/data:/data
        ```

    === "Jetson5"

        ``` bash
        docker run --ipc=host --runtime=nvidia -it tracking-image -v "$(pwd)"/data:/data
        ```

2. Run the tracking program, specify the location to the data

    ```bash
    python3 tracking.py --video-source <path-to-file>
    ```

### Mounting Configuration Files 
Mount the VideoConfig.yaml file to the `/configuration` section of the container when running. You may also want to mount `/data` to the container to easily pass data into it.

1. Running Container with Configuration/Data Mounts


    === "Linux"

        ``` bash
        docker run -it tracking-image -v "$(pwd)"/configuration:/configuration -v "$(pwd)"/data:/data
        ```

    === "Jetson5"

        ``` bash
        docker run --ipc=host --runtime=nvidia -it tracking-image -v "$(pwd)"/configuration:/configuration -v "$(pwd)"/data:/data
        ```

2. Modify these 2 settings in the `VideoConfig.yaml` configuration file

    ``` yaml 
    # Yolo Options
    videoSource: "<absolutePathToFileOnDisk>"
    ```

    For full details on the RadarConfig.yaml file please see the [configuration](../configuration/configuration.md) section.

3. Running the tracking command.
    Optionally, if you mounted the configuration at a different path you can specify that path too. By default it's set to `/configuration/VideoConfig.yaml`.
    ```bash
    python3 tracking.py --video-config <my-data-path>
    ```


