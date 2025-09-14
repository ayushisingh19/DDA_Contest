# Vite + React (dev) image
FROM node:20-alpine
WORKDIR /workspace/frontend
COPY frontend/package.json frontend/pnpm-lock.yaml* frontend/yarn.lock* frontend/npm-shrinkwrap.json* ./
RUN npm install || true
COPY frontend /workspace/frontend
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
