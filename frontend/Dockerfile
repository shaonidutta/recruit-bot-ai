# Frontend Dockerfile (Vite/React development)
FROM node:20-alpine

WORKDIR /usr/src/app

# install dependencies
COPY package*.json ./
RUN npm install

# copy source
COPY . .

# expose vite default dev port
EXPOSE 5173

# run dev server and listen on all interfaces
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
