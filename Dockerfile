# Use an official Node.js image with Debian (easy to install Python)
FROM node:20-bullseye

# Set working directory inside the container
WORKDIR /app

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Copy only the Server folder contents into /app inside container
COPY Server/ ./

# Install Node.js dependencies
RUN npm install

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose port (adjust if your server uses a different port)
EXPOSE 3000

# Default command to run Node.js server
CMD ["node", "server.js"]
