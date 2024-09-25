FROM ultralytics/ultralytics:8.2.93

ENV PROJECT_PATH=/tracking/UAV-Object-Tracking

# Setup working DIR
RUN mkdir -p /tracking
RUN mkdir -p $PROJECT_PATH
WORKDIR $PROJECT_PATH

# Copy base files that are required
COPY ./requirements.txt .

# Install requirements
RUN pip install -r requirements.txt

# Copy over folders
COPY ./radar_tracking ./radar_tracking
COPY ./tracking ./tracking
COPY ./plots ./plots
COPY ./video ./video

# Add directories to PYTHONPATH relative to the working directory
ENV PYTHONPATH="${PYTHONPATH}:$PROJECT_PATH/configuration:$PROJECT_PATH/plots:$PROJECT_PATH/tracking:/ultralytics:$PROJECT_PATH/radar_tracking:$PROJECT_PATH/video"

# Copy over tracking file
COPY ./tracking.py .
COPY ./constants.py .
COPY ./config.py .

# Copy over configuration
RUN mkdir -p /configuration
COPY ./configuration /configuration

# Add /data to allow for mounting incoming data into the container
RUN mkdir /data