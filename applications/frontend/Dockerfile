FROM nginx:alpine

# Copy frontend files into nginx html directory
COPY src/ /usr/share/nginx/html

# Replace default nginx config with ours
COPY nginx.conf /etc/nginx/conf.d/default.conf
