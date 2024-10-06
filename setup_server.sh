#!/bin/bash

# Define Nginx configuration file path
NGINX_CONF="/etc/nginx/sites-available/default"

# Backup the original config
sudo cp $NGINX_CONF ${NGINX_CONF}.bak

# Write a new server block configuration to forward requests to port 5000
sudo tee $NGINX_CONF > /dev/null <<EOL
server {
    listen 80;

    location / {
        proxy_pass http://127.0.0.1:5000/api/v1/;
    }
}
EOL
# Test Nginx configuration and reload if successful
sudo nginx -t && sudo systemctl reload nginx

echo "Nginx is now forwarding all requests to port 5000."