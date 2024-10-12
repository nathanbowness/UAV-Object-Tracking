# Detections

Detections from both Radar and Video will be put into the following central format. 
This is the datashape the ObjectTracking.py expects the data to be in, when reading from the MP Queue for object tracking

This will allow them to both be used by StoneSoup's tracking algorithms. This also offers abstraction, incase later the radar or video processing algorithm changes. As long as this format is used, the different segments can be swapped out.

```json
{
    "timestamp": "<some-datetime>",
    "type": "radar | video",
    "detections": [
            {
                "object": "<typeOfObject1>",
                "detection":  [x1, x_v1, y, y_v1]
            },
            {
                "object": "<typeOfObject2>",
                "detection":  [x2, x_v2, y, y_v2]
            } 
        ]
}
```