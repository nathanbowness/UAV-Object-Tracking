clc; clear all;
close all;

mainfolder = cd;
folderlist = dir([mainfolder, '\Data\2024-10-18*']);

%%%%% For recording Oct18_CFAR_Dist1p3meter: folderSelectorCntr=1,
%%%%% For recording Oct18_CFAR_Dist5p0meter: folderSelectorCntr=2,
%%%%% For recording Oct18_CFAR_Dist15p0meter: folderSelectorCntr=3,
%%%%% For recording Oct18_CFAR_Dist29p0meter: folderSelectorCntr=4,
%%%%% For recording Oct18_CFAR_Dist20p0meter: folderSelectorCntr=5,
folderSelectorCntr = 4;

% CFAR Detector setup
detector = phased.CFARDetector('Method','CA','NumTrainingCells',10, ...
    'NumGuardCells',4,'ThresholdFactor','Custom', ...
    'CustomThresholdFactor',4,'ThresholdOutputPort',true, ...
    'NoisePowerOutputPort',true);

% Video setup
v = VideoWriter('Oct18_CFAR_Voltage_UsingTD-Nov3rd.avi');
v.FrameRate = 5;
open(v);

fc = 24.35e9;
c = 3e8;
d = 6.25e-3;
bin_size = 199.939e-3;
max_range = 512*bin_size;

% Define range vector for the bins, assuming each bin corresponds to a specific distance
range_vector = (0:511) * 199.939e-3; % Adjust based on your range resolution

% Calculate the SFC gain (R^2 amplitude curve)
SFC_gain = range_vector.^2;

foldername = ['.\Data\', folderlist(folderSelectorCntr).name, '\TD\'];
files_list = dir([mainfolder, foldername, '*.txt']);

% Create figure handles before the loop
polar_fig = figure; % Handle for the polar plot figure
cartesian_fig = figure; % Handle for the Cartesian plot figure

for cntr2 = 1:length(files_list)
    % Open the text file
    filename = files_list(cntr2).name;
    time_second(cntr2) = str2num(filename(end-9:end-4));
    fileID = fopen([mainfolder, foldername, filename], 'r');

    % Skip metadata
    for i = 1:17
        fgetl(fileID);
    end

    % Read data
    data = textscan(fileID, '%f %f %f %f', 'HeaderLines', 1);
    fclose(fileID);

    % Extract I1, Q1, I2, Q2 data as 1024x1 matrices
    I1 = data{1};
    Q1 = data{2};
    I2 = data{3};
    Q2 = data{4};

    I1_fft = fft(I1, 1024);
    Q1_fft = fft(Q1, 1024);
    I2_fft = fft(I2, 1024);
    Q2_fft = fft(Q2, 1024);
    
    % uncomment to apply window
    %window = hann(length(Q1));
    %I1_fft = fft(I1 .* window, 1024);
    %Q1_fft = fft(Q1 .* window, 1024);
    %I2_fft = fft(I2 .* window, 1024);
    %Q2_fft = fft(Q2 .* window, 1024);

    I1_fft = I1_fft(1:512);
    Q1_fft = Q1_fft(1:512);
    I2_fft = I2_fft(1:512);
    Q2_fft = Q2_fft(1:512);

    % Calculate phase difference between the receivers Rx1 and Rx2 before
    % SFC gain is added
    phase_diff = angle(I1_fft .* conj(I2_fft));  % Element-wise phase difference between FFTs
    angles = asind((phase_diff * c) / (2 * pi * d * fc));  % Resulting angle vector
    angles = max(min(angles, 90), -90);

    % Apply SFC gain to each FFT output
    I1_fft = I1_fft .* SFC_gain';
    Q1_fft = Q1_fft .* SFC_gain';
    I2_fft = I2_fft .* SFC_gain';
    Q2_fft = Q2_fft .* SFC_gain';

    % Optionally exclude the first FFT bin
    I1_fft(1) = 0;
    Q1_fft(1) = 0;
    I2_fft(1) = 0;
    Q2_fft(1) = 0;

    % Calculate amplitude in dBm and phase in degrees
    I1_amp = abs(I1_fft);        % Amplitude for I1
    I1_phase = rad2deg(angle(I1_fft));       % Phase in degrees for I1

    Q1_amp = abs(Q1_fft);        % Amplitude for Q1    
    Q1_phase = rad2deg(angle(Q1_fft));       % Phase in degrees for Q1

    I2_amp = abs(I2_fft);        % Amplitude for I2
    I2_phase = rad2deg(angle(I2_fft));       % Phase in degrees for I2

    Q2_amp = abs(Q2_fft);        % Amplitude for Q2
    Q2_phase = rad2deg(angle(Q2_fft));       % Phase in degrees for Q2
    x1= I1_amp.*exp(1i*deg2rad(I1_phase))+(Q1_amp.*exp(1i*deg2rad(Q1_phase)));
    x2= I2_amp.*exp(1i*deg2rad(I2_phase))+(Q2_amp.*exp(1i*deg2rad(Q2_phase)));
    
    % Now proceed with CFAR detection and plotting as in the original code
    % Here we use the I1_amp and I1_phase for CFAR detection
    [x_detected, th] = detector(abs(x1), 1:length(x1));

    % Print detections to the console
    detected_distances = find(x_detected) * 199.939e-3; % Calculate distances for each detection
    fprintf('Detections for file %s:\n', filename);
    
    % Initialize arrays for polar plot data as empty row vectors
    polar_distances = []; % To store radial distances for the polar plot
    polar_angles = []; % To store angles in radians for the polar plot
    
    for i = 1:length(detected_distances)
        detection_indices = find(x_detected, i); % Get indices of each detection
        
        for j = 1:length(detection_indices) % Loop over multiple detections, if any
            detection_index = detection_indices(j); % Access each detection index
            detection_value_dB = db(abs(x1(detection_index))); % Get detection level in dB
            angle_i = angles(detection_index); % Get the angle for the detection
    
            fprintf(' - Distance: %.2f meters, Amplitude: %.2f dB, Angle: %.2f degrees\n', ...
                    detected_distances(i), detection_value_dB, angle_i);
            
            % Store for polar plot (convert angle_i to radians)
            polar_distances = [polar_distances, detected_distances(i)]; % Append scalar distance
            polar_angles = [polar_angles, deg2rad(angle_i)]; % Append scalar angle in radians
        end
    end
    
    % Polar Plot for the detections
    figure(polar_fig); % Use existing polar figure
    clf; % Clear previous plot
    
    polarplot(polar_angles, polar_distances, 'k*', 'MarkerSize', 8, 'LineWidth', 2);
    title('Radar Detections - Polar Plot');
    
    % Set angular and radial limits
    thetalim([-90 90]); % Limit angle range from -90° to 90°, with 0° pointing upwards
    rlim([0, max_range]); % Set max range to max radar distance
    
    % Customize radial and angular ticks
    rticks([10,20,30,40,50,60,70,80,90,100]);
    thetaticks(-90:30:90); % Set angle ticks every 30 degrees within the limited range

    % Point the polar plot north
    set(gca, 'ThetaZeroLocation', 'top'); % Set 0° to be at the top
    set(gca, 'ThetaDir', 'counterclockwise'); % Ensure angles increase counterclockwise
    
    % Enable grid for better readability
    grid on;

    % Cartesian Plot for CFAR detection results
    figure(cartesian_fig); % Use existing Cartesian figure
    clf; % Clear previous plot
    hold all;
    plot((1:length(x1)) * bin_size, db(abs(x1)), 'LineWidth', 2);
    plot((1:length(x1)) * bin_size, db(th), 'r', 'LineWidth', 2);
    plot(find(x_detected) * bin_size, db(abs(x1(x_detected))), 'k*', 'LineWidth', 3);
    grid on;
    legend('Signal', 'CFAR Threshold From FD Data', 'Detections', 'Location', 'southeast');
    xlabel('Distance (meter)');
    ylabel('Level (dB)');
    ylim([-20, 80]);
    pause(0.1);
    frame = getframe(gcf);
    writeVideo(v, frame);
end

% Close the video
close(v);
