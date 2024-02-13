# Use a node image as a parent image
FROM node:14

# Set the working directory in the container
WORKDIR /MCC

# Copy package.json and package-lock.json into the container
COPY package*.json /MCC/

# Install dependencies
RUN npm install

# Copy the current directory contents into the container at /MCC
COPY . /MCC/

# Copy the current directory contents into the container at /app
COPY client.js /app/client.js

# Run the compiled JavaScript file when the container launches
CMD ["node", "dist/client.js"]
