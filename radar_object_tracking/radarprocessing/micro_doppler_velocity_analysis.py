import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import stft

# Constants
SPEED_OF_LIGHT = 3e8  # Speed of light in m/s

def calculate_doppler(phase_array, time_interval):
    phase_unwrapped = np.unwrap(phase_array)  # Unwrap the phase to avoid discontinuities
    phase_diff = np.diff(phase_unwrapped)
    doppler_freq = phase_diff / (2 * np.pi * time_interval)  # Convert phase difference to frequency
    return doppler_freq

def calculate_velocity(doppler_freq, carrier_frequency=((24000 + (750 / 2)) * (10**6))):
    """
    Calculate the velocity from the Doppler frequency shift.
    """
    velocity = (doppler_freq * SPEED_OF_LIGHT) / (2 * carrier_frequency)
    return velocity

def micro_doppler_analysis(phase_I1_over_time, phase_Q1_over_time, phase_I2_over_time, phase_Q2_over_time, time_interval=0.245, carrier_frequency=((24000 + (750 / 2)) * (10**6))):
    """
    Perform micro-Doppler analysis on the raw data.
    The function takes the phase data for the I and Q components of the radar signal over time.
    It must be called for each range bin individually.
    """
    
    # Calculate the Doppler shifts for all four signals
    doppler_I1 = calculate_doppler(phase_I1_over_time, time_interval)
    doppler_Q1 = calculate_doppler(phase_Q1_over_time, time_interval)
    doppler_I2 = calculate_doppler(phase_I2_over_time, time_interval)
    doppler_Q2 = calculate_doppler(phase_Q2_over_time, time_interval)

    # Average Doppler shifts
    doppler_avg = (doppler_I1 + doppler_Q1 + doppler_I2 + doppler_Q2) / 4
    
    # Perform Short-Time Fourier Transform (STFT) to get time-frequency representation\
    nperseg = min(256, len(doppler_avg)) # Number of samples per segment
    f, t, Zxx = stft(doppler_avg, fs=1/time_interval, nperseg=nperseg, return_onesided=False)
    
    # Parameters for drone detection (example thresholds)
    frequency_threshold = 100  # Example: frequencies above 100 Hz could indicate drone
    magnitude_threshold = 5.0  # Example: magnitude threshold

    # Extract relevant frequency indices (e.g., those above the threshold)
    drone_frequency_indices = np.where(f > frequency_threshold)

    # Extract magnitudes at those frequencies
    drone_magnitude = np.abs(Zxx[drone_frequency_indices, :])

    # Check if there are significant magnitudes at high frequencies
    drone_detected = np.any(drone_magnitude > magnitude_threshold)
    
    if drone_detected:
        print('Drone detected!')
        
        
    # Get the magnitude of the STFT results
    magnitude_Zxx = np.abs(Zxx)
    
    # Get the maximum magnitude at each time step (across all frequency bins)
    max_magnitude_per_time = np.max(magnitude_Zxx, axis=0)
    
    # Get the maximum magnitude across all time and frequency bins
    max_magnitude_overall = np.max(max_magnitude_per_time)
        
    return f, t, Zxx, doppler_avg, carrier_frequency, drone_detected, max_magnitude_per_time, max_magnitude_overall

def generate_sample_drone_data(length=1024, frequency=150, noise_level=2):
    """
    Generate sample drone data with a specific frequency component.
    """
    t = np.arange(length)
    signal = np.sin(2 * np.pi * frequency * t / length)  # Sinusoidal signal
    noise = noise_level * np.random.randn(length)  # Add noise
    return signal + noise

def generate_high_velocity_sample(length=1000, high_frequency=1400, noise_level=0.5):
    """
    Generate sample data with a high frequency component to simulate high velocity.
    """
    t = np.arange(length)
    signal = np.sin(2 * np.pi * high_frequency * t / length)  # High frequency sinusoidal signal
    noise = noise_level * np.random.randn(length)  # Add noise
    return signal + noise

def main():
    # Generate high velocity sample data for two time intervals
    phase_I1 = generate_high_velocity_sample()
    phase_Q1 = generate_high_velocity_sample()
    phase_I2 = generate_high_velocity_sample()
    phase_Q2 = generate_high_velocity_sample()
    time_interval = 0.245

    # Perform micro-Doppler analysis
    f, t, Zxx, doppler_avg, carrier_frequency, drone_detected, max_magnitude_per_time, max_magnitude_overall = micro_doppler_analysis(phase_I1, phase_Q1, phase_I2, phase_Q2, time_interval)
    
    print(f)

    # Calculate velocity
    velocity = calculate_velocity(doppler_avg, carrier_frequency)

    # Plot the results
    plt.figure(figsize=(10, 6))
    plt.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
    plt.title('Micro-Doppler Time-Frequency Representation')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [s]')
    plt.colorbar(label='Magnitude')
    plt.show(block=False)

    # Plot the velocity
    plt.figure(figsize=(10, 6))
    plt.plot(velocity)
    plt.title('Velocity over Time')
    plt.ylabel('Velocity [m/s]')
    plt.xlabel('Time [s]')
    plt.show()
    print("test")

if __name__ == "__main__":
    main()