# Detections

Detections from both Radar and Video will be put into the following central format.
This will allow them to both be used by StoneSoup's tracking algorithms.

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