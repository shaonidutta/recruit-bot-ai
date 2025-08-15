# Backend Dockerfile (Node.js development)
FROM node:20-alpine

# set working directory
WORKDIR /usr/src/app

# install deps first (leveraging Docker cache)
COPY package*.json ./
RUN npm install

# copy source
COPY . .

# expose dev port (adjust if your app uses a different port)
EXPOSE 3000

# use the project's dev script (expected in package.json)
CMD ["npm", "run", "dev"]
