
from get_all_sensor_data import get_fd_data_from_radar
from plots.FrequencySignalPlot import FreqSignalPlot
from resources.FDDataMatrix import FDSignalType
from RadarDevKit.Interfaces.Ethernet.EthernetConfig import EthernetParams

from config import RunParams, get_run_params
from config import get_radar_module

from resources.RadarDataWindow import RadarDataWindow
from resources.RunType import RunType

def data_processing(run_params: RunParams, radar_window : RadarDataWindow):
    
    radar_module = get_radar_module()
    bin_index = 1
    signal_type_to_plot = FDSignalType.I1
    plotter = FreqSignalPlot(bin_index, signal_type_to_plot)  # Create a plotter instance
    
    # Infinite loop
    while True:
        # If this is a re-run, use existing data to similar a "LIVE"
        if(run_params.runType == RunType.RERUN):
          exit("Re-runs not implemented yet - but coming soon.")
        
        # Grab new data, add it to the window of saved data
        radar_window.update_window_data(run_params, radar_module)
        
        # Until we have enough records for CFAR or analysis, just continue 
        if(len(radar_window.get_records()) < run_params.data_window_size):
            continue
        
        signals, plot_timedelta = radar_window.get_signal_for_bin(bin_index, signal_type_to_plot)
        plotter.update_plot(signals, plot_timedelta)

if __name__ == "__main__":
    run_params = get_run_params()
    radar_data_window = RadarDataWindow(run_params.data_window_size,  30)
    
    data_processing(run_params, radar_data_window)
    print("test")