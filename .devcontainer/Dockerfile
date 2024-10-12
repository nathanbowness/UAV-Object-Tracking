FROM ultralytics/ultralytics:latest

# Add directories to PYTHONPATH relative to the working directory
ENV PYTHONPATH="${PYTHONPATH}:$PROJECT_PATH/configuration:$PROJECT_PATH/plots:$PROJECT_PATH/tracking:/ultralytics:$PROJECT_PATH/radar_tracking:$PROJECT_PATH/video"

# Copy base files that are required
COPY ./requirements.txt .

# Install requirements
RUN pip install -r requirements.txt