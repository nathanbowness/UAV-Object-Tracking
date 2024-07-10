import numpy as np
from datetime import datetime, timedelta
from stonesoup.types.state import GaussianState, State
from stonesoup.types.groundtruth import GroundTruthPath, GroundTruthState

class ExtendedObjectMetadata():
    def __init__(self, length, width, orientation):
        self.length = length
        self.width = width
        self.orientation = orientation
        
    def get_metadata_as_dict(self):
        return {"length": self.length, "width": self.width, "orientation": self.orientation}
    
class GaussianStateWrapperPolar():
    def __init__(self, range, angle, angular_vel, covaraince_vector,
                 start_time= datetime.now().replace(microsecond=0)):
        x = range * np.cos(angle)
        x_vel = angular_vel * np.cos(angle)
        y = range * np.sin(angle)
        y_vel = angular_vel * np.sin(angle)       
    
        self.state = GaussianState(np.array([x, x_vel, y, y_vel]),
                              np.diag(covaraince_vector),
                              timestamp=start_time)
        
    def getState(self) -> GaussianState:
        return self.state
    
    def get_orientation_angle(self):
        return np.arctan(self.state.state_vector[3]/self.state.state_vector[1])
        
class GaussianStateWrapper():
    """
    state_vector: [x, x_vel, y, y_vel]
    covaraince_vector: [x_cov, x_vel_cov, y_cov, y_vel_cov]
    """
    def __init__(self, state_vector,
                 covaraince_vector,
                 start_time= datetime.now().replace(microsecond=0)):
        
        self.state = GaussianState(np.array(state_vector),
                              np.diag(covaraince_vector),
                              timestamp=start_time)
        
    def getState(self) -> GaussianState:
        return self.state
    
    def get_orientation_angle(self):
        return np.arctan(self.state.state_vector[3]/self.state.state_vector[1])
    
    def get_position_polar(self):
        x, y = self.state.state_vector[0], self.state.state_vector[2]
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)
        return r, theta
    
    def get_velocity_polar(self):
        x_vel, y_vel = self.state.state_vector[1], self.state.state_vector[3]
        speed = np.sqrt(x_vel**2 + y_vel**2)
        direction = np.arctan2(y_vel, x_vel)
        return speed, direction
      
def get_target_1(start_time = datetime.now().replace(microsecond=0)):
    """
    South-East Moving Object
    Start at -450, 200
    """
    # First potential target object
    target = GaussianStateWrapper([-450, 1.3, 200, -1.4], [5, 0.5, 5, -0.5], start_time)
    metadata_tg = ExtendedObjectMetadata(10, 5, target.get_orientation_angle())
    return target.state, metadata_tg.get_metadata_as_dict()

def get_target_2(start_time = datetime.now().replace(microsecond=0)):
    """
    South-West Moving Object
    Start at 3000, 700
    """
    target = GaussianStateWrapper([3000, -0.1, 700, -1.6], [3, 0.5, 3, 0.5], start_time)
    metadata_tg = ExtendedObjectMetadata(20, 10, target.get_orientation_angle())
    return target.state, metadata_tg.get_metadata_as_dict()

def get_target_3(start_time = datetime.now().replace(microsecond=0)):
    """
    North-West Moving Object
    Start at 400, -200
    """
    target = GaussianStateWrapper([400, -1.2, -200, 1.4], [5, -0.5, 5, 0.5], start_time)
    metadata_tg = ExtendedObjectMetadata(8, 3, target.get_orientation_angle())
    return target.state, metadata_tg.get_metadata_as_dict()

def get_target_4(start_time = datetime.now().replace(microsecond=0)):
    """
    North-East Moving Object
    Start at -600, -500
    """
    target = GaussianStateWrapper([-600, 2, -500, 2], [5, 0.5, 5, 0.5], start_time)
    metadata_tg = ExtendedObjectMetadata(12, 6, target.get_orientation_angle())
    return target.state, metadata_tg.get_metadata_as_dict()

def get_target_5(start_time = datetime.now().replace(microsecond=0)):
    """
    North Moving Object
    Start at 0, -900
    """
    target = GaussianStateWrapper([0, 0.05, -900, 0.9], [5, 0.5, 5, 0.5], start_time)
    metadata_tg = ExtendedObjectMetadata(12, 6, target.get_orientation_angle())
    return target.state, metadata_tg.get_metadata_as_dict()

def get_5_object_targets(start_time = datetime.now().replace(microsecond=0)):
    """
    Returns the states of 5 target objects, that all start at the centre and move outwards
    """
    target_state1, metadata_tg1 = get_target_1(start_time)
    target_state2, metadata_tg2 = get_target_2(start_time)
    target_state3, metadata_tg3 = get_target_3(start_time)
    target_state4, metadata_tg4 = get_target_4(start_time)
    target_state5, metadata_tg5 = get_target_5(start_time)
    
    targets = [target_state1, target_state2, target_state3, target_state4, target_state5]
    metadatas = [metadata_tg1, metadata_tg2, metadata_tg3, metadata_tg4,  metadata_tg5]
    
    return targets, metadatas

def get_truths_for_targets(targets, metadatas, num_steps, 
                          transition_model, start_time = datetime.now().replace(microsecond=0), time_measurement_delta = 5):
    truths = set()
    for itarget in range(len(targets)):

        # initialise the truth
        truth = GroundTruthPath(GroundTruthState(targets[itarget].state_vector,
                                                timestamp=start_time,
                                                metadata=metadatas[itarget]))

        for k in range(1, num_steps):  # loop over the timesteps
            # Evaluate the new state
            new_state = transition_model.function(truth[k-1],
                                                noise=True,
                                                time_interval=timedelta(seconds=5))

            # create a new dictionary from the old metadata and evaluate the new orientation
            new_metadata = {'length': truth[k - 1].metadata['length'],
                            'width': truth[k - 1].metadata['width'],
                            'orientation': np.arctan2(new_state[3], new_state[1])}

            truth.append(GroundTruthState(new_state,
                                        timestamp=start_time + timedelta(seconds=time_measurement_delta*k),
                                        metadata=new_metadata))

        truths.add(truth)
    return truths

if __name__ == "__main__":
    
    thing = range(np.random.poisson(5))
    for test in thing:
        print('hi')
    
    targets, metadatas = get_5_object_targets()
    for target, metadata in zip(targets, metadatas):
        print(target, metadata)


    