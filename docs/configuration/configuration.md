# Configuration Files
## Radar Configuration File

The radar configuration can be found in the RadarConfig.yaml file. 

??? info "RadarConfig.yaml"

    ```yaml
    # Radar signal configuration - for now only FMCW Up-Ramp is supported
    minimumFrequencyMhz: 24000
    maximumFrequencyMhz: 24750
    rampTimeFmcwChirp: 1
    # Tx attenuation during measurement
    # 0 ~ 0dB, 1 ~ 0.4dB, 2 ~ 0.8dB, 3 ~ 1.4 dB, 4 ~ 2.5dB, 5 ~ 4dB, 6 ~6dB, 7 ~ 9dB
    attenuation: 0

    # Radar connection configuration
    ethernetParams:
    ethernetPort: 1024
    ethernetIp: "192.168.0.2" # IP to connect to the radar withs

    # Radar signal processing configuration
    cfarParams:
    cfarNumGuard: 5
    cfarNumTrainingCells: 10
    cfarThreshold: 10
    cfarType: "CASO" # Options are CASO, LEADING_EDGE

    # Run configuration
    run: LIVE # Options are LIVE, RERUN
    sourcePath: "/data/radar/run2-TD/" # Path to the data to be processed for RERUN mode

    recordData: True # Record radar data to disk
    recordDataPath: "/output" # Path to the data to be recorded

    # How many Radar results to keep in the buffer for analysis and CFAR 
    processingWindow: 200

    # Print radar runtime settings to console on startup
    printSettings: True
    ```
## Video Processing Configuration File (Yolo Params)

The radar configuration can be found in the YoloConfig.yaml file. 

??? info "VideoConfig.yaml"

    ```yaml
    # Configuration for the Yolo Processing
    modelWeights: "./yolov8n.pt" # If a path on disk is specified, it will not be downloaded by Yolo
    saveRawImages: True # Determine if the raw images should be saved
    saveProcessedVideo: True
    outputDirectory: "/output"
    videoSource: "https://youtu.be/LNwODJXcvt4"
    # videoSource: "/data/video/M0101.mp4"
    confidenceThreshold: 0.3
    iouThreshold: 0.5
    videoStream: True

    # Configuration for showing the Live Video During Yolo Processing
    showBoxesInVideo: True
    showVideo: False
    printDetectedObjects: False # Print the detected objects in the console as noticed

    # Camera Details
    cameraHorizontalFOV: 170
    cameraZoomFactor: 1.0
    imageWidth: 640
    imageHeight: 352
    ```

## Tracking Configuration File

??? info "TrackingConfig.yaml"

    ```yaml
    # Filter Configuration for different tracking algorithms
    activeFilter: gmPHD
    filters:
    # GM PHD 
    gmPHD:
        birthCovariance: 200 # covariance of the birth state in a distance of meters - by default this will set to the maximum resolution range of the sensors!
        expectedVelocity: 1 # expected velocity of the tracked object in meters per second
        noiseCovarianceDistance: 1 # covariance of the noise in a distance of meters
        defaultCovarianceDistance: 1 # default covariance of the tracked object in a distance of meters
        defaultConvarianceVelocity: 0.3 # default covariance of the tracked object in a velocity of meters per second
        probabilityOfDetection: 0.8 # probability of detection
        probabilityOfDeath: 0.01 # probability of death
        clusterRate: 7.0

        mergeThreshold: 5 # Threshold Squared Mahalanobis distance
        pruneThreshold: 0.00000001  # Threshold component weight i.e. 1e-8
        stateThreshold: 0.25

    # Detection clustering configuration
    minDetectionsToCluster: 1
    maxDistanceBetweenClusteredObjectsM: 2

    # Tracking plot configuration 
    trackTailLength: 0.1 # O to 1, 0 means no tail, 1 means full tail

    # Configuration for processing and memory management
    maxTrackQueueSize: 200

    # Show the Stone Soup tracking plot when the program exits
    showTrackingPlot: False

    # Output path for the tracking results
    saveTrackingResults: True
    outputDirectory: '/output'
    ```