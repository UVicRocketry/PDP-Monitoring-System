# Use an official Python runtime as a parent image
FROM python:3

# Set the working directory in the container
WORKDIR /VC

# Copy the current directory contents into the container at /app
COPY server.py /VC/server.py

# Run the server.py script when the container launches
CMD ["python", "server.py"]
