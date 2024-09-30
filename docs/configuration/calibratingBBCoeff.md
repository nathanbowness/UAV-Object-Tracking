# Calibrating the BB Coefficients

So currently the distance calculations for objects relative to the camera must be calibrated. For best results, please individually calibrate the BB coefficient for you individual objects. 
For convience, there are some helpful functions to help calibrate a collection of objects after just calibrating from one known one -- [determine_bb_coeffs.py](../video/determine_bb_coeffs.py)

## Steps to Calibrate
1. Determine your camera's details, including horizon FOV, default zoom factor, and the videos width and height in pixels. 
2. Measure the width of an object.
3. Do the following at a few different distances from the camera to ensure the estimation is accurate. The coefficient should be mostly constant at different distances.
  * Measure the distance of an object from the camera.
  * Call the following function `determine_bb_coeff_for_object(...)` using your IDE, or the following cli command. It will use the following calcualte 

**Bounding Box (BB) Coefficient Calculation:**
$$
\text{BB Coefficient} = \frac{\text{focal length (pixels)} \times \text{object width (meters)}}{\text{distance from camera (meters)} \times \text{object pixel width (pixels)}}
$$
  
```bash
# Example: python3 -c "import video/determine_bb_coeffs; determine_bb_coeffs.determine_bb_coeff_for_object(distance_from_camera, object_name, object_width_meters, camera_horizontal_fov, image_width, image_height)"
cd video
python3 -c "import determine_bb_coeffs; determine_bb_coeffs.determine_bb_coeff_for_object(10, 'person', 0.52, 65, 1920, 1080, 'test.jpg')"
```

4. Use the determined BB coefficient, to populate the coefficients for lots of related objects. The formula can be see below.This uses the approximate width of the object you calibrated against versus the other object's width to approximate their coefficients as well.

**Bounding Box (BB) Coefficient Proportion Calculation:**
$$\text{BB Coefficient}_{\text{object}} = \text{BB Coefficient}_{\text{known}} \times \frac{\text{size of known object}}{\text{size of other object}}$$

Call this function with the determines BB coefficients for lots of related objects based off the correct one you just found. 

```bash
# Example: python3 -c "import determine_bb_coeffs; determine_bb_coeffs.determine_all_bb_coefficients(object_name, object_known_width, known_bb_coeff, "BBCoefficients.yaml")

python3 -c "import determine_bb_coeffs; determine_bb_coeffs.determine_all_bb_coefficients('person', 0.52, 0.127383, "BBCoefficients.yaml")"
```
5. That function should have created a new list of coefficients. Please use that for future tracking, and add it to the configuration file.

**Note:* Alterative is to edit the bottom of the [determine_bb_coeffs.py](../video/determine_bb_coeffs.py), which will create the BBCoefficients.yaml file for you when you run it. Just update the values to your desired ones.
