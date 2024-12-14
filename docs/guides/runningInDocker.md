# Running In Docker

This project publishes docker images to [DockerHub](https://hub.docker.com/r/nbowness/uav-experiments/tags) to allow users to quickly run the software. Two variants of the images are published, for linux and for Jetson5 devices. For more details on the published images please see the [Image Details](../configuration/imageDetails.md) page.

To get started with the latest images, please pull it onto your computer. 

## Pulling the Images

=== "Linux"

    ``` bash
    docker pull nbowness/uav-experiments:latest
    ```

=== "Jetson5"

    ``` bash
    docker pull nbowness/uav-experiments:latest-jetson-jetpack5
    ```

## Tag Images
To simplify future command, you can tag the images to a shorter name. **All commands shown below** will use the short form `tracking-image`.

=== "Linux"

    ``` bash
    docker tag nbowness/uav-experiments:latest tracking-image
    ```

=== "Jetson5"

    ``` bash
    docker tag nbowness/uav-experiments:latest-jetson-jetpack5 tracking-image
    ```

## Running the Container
To run the container interactively, you can run the following command to launch the container. To run, non-interactively remove the `-it` option. 

=== "Linux"

    ``` bash
    docker run -it tracking-image
    ```

=== "Jetson5"

    ``` bash
    docker run --ipc=host --runtime=nvidia -it tracking-image
    ```

### Running the Tracking Software

After launching the container on either platform, you can run the following command to start the program. Use this default configuration, the radar and video process will run on "live" data, until told to exit with `q+ENTER` (or `CTRL+c`).

```bash
python3 tracking.py 
```

### Saving Data Output Locally
You can save all output of the container to a local folder, by mounting a local folder on disk to the `/output`directory of the container.
The below command will mount a local output folder to the container, feel free to modify it.

=== "Linux"

    ``` bash
    docker run -it -v "$(pwd)"/output:/output tracking-image
    ```

=== "Jetson5"

    ``` bash
    docker run --ipc=host --runtime=nvidia -it -v "$(pwd)"/output:/output tracking-image 
    ```

## Configuration

By default the above commands will run the program with default configuration. This will use the default configuration files, for more details please review the [configuration page](../configuration/configuration.md).

To change the configuration, there are 2 options
1. Change options with [CLI arguments](../configuration/cliArguments.md) when running `tracking.py`. 
1. Mount configuration files to the container with updated arguments.

### CLI Arguments for Program
The are numerous [CLI arguments](../configuration/cliArguments.md) for the `tracking.py` program.
To see all options you can run the `--help` command. 

``` bash
python3 tracking.py --help 
```

An example of updating the Radar's IP address can be see below.

```bash
python3 tracking.py --radar-ip 10.0.1.60
```

### Mounting Configuration Files
To mount configuration files that you can change locally, and will get used by the container you can mount a volume to the `/configuration` directory in the container.
=== "Linux"

    ``` bash
    docker run -it -v "$(pwd)"/configuration:/configuration tracking-image 
    ```

=== "Jetson5"

    ``` bash
    docker run --ipc=host --runtime=nvidia -it -v "$(pwd)"/configuration:/configuration tracking-image
    ```

### Running with Different Configurations - Samples
* Running the container on previously collected data - [details](./runningOnCollectedData.md)
* Running the container with only radar processing - [details](./runningOnCollectedData.md)
* Running the container with only video processing - [details](./runningVideoProcessing.md)
* Running the container with displayed results - [datails](./runningWithVisuals.md)