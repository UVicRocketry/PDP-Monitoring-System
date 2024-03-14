# Use an official Python runtime as a parent image
FROM python:3

# Set the working directory in the container
WORKDIR /VC

# Copy the current directory contents into the container at /VC
COPY . /VC

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /VC/requirements.txt

# Run the server.py script when the container launches
CMD ["python", "server.py"]
