import random
import time

def radar_object_tracking():
    # sleep for 1 seconds
    # return an array of length n, of random x and y coordinate with (0, 90)
    num_points = 5
    return [(random.randint(0, 90), random.randint(0, 90)) for _ in range(num_points)]
    