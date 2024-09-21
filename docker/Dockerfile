FROM ultralytics/ultralytics:8.2.93

# Setup working DIR
RUN mkdir -p /tracking
RUN mkdir -p /tracking/UAV-Object-Tracking/
WORKDIR /tracking/UAV-Object-Tracking/

# Copy base files that are required
COPY ./requirements.txt .

# Install requirements
RUN pip install -r requirements.txt

# Copy over folders
COPY ./radar_tracking ./radar_tracking
COPY ./tracking ./tracking
COPY ./plots ./plots
COPY ./video ./video

# Copy over tracking file
COPY ./object_tracking.py .
COPY ./constants.py .
COPY ./config.py .

# Copy over configuration
RUN mkdir -p /configuration
COPY ./configuration /configuration
