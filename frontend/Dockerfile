# Use Node.js base image
FROM node:24-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy the frontend source
COPY . .

# Expose development port
EXPOSE 3000

# Start the frontend
CMD ["npm", "start"]
