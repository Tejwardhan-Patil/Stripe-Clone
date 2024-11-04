import os
import subprocess

# Install NGINX
def install_nginx():
    if subprocess.run(["nginx", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 0:
        subprocess.run(["sudo", "apt-get", "install", "-y", "nginx"])
        print("NGINX installed successfully")

# Update the NGINX configuration for load balancing
def update_nginx_config():
    nginx_config = """
    upstream backend_servers {
        # Define multiple backend servers for load balancing
        server backend1.website.com max_fails=3 fail_timeout=30s;
        server backend2.website.com max_fails=3 fail_timeout=30s;
        server backend3.website.com max_fails=3 fail_timeout=30s;
        server backend4.website.com max_fails=3 fail_timeout=30s;
        
        # Health check for backends
        health_check interval=5s fails=2 passes=2;
    }

    server {
        listen 80;
        server_name website.com;

        # Load balancing settings
        location / {
            proxy_pass http://backend_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts for better performance handling
            proxy_connect_timeout 30;
            proxy_send_timeout 60;
            proxy_read_timeout 60;

            # Buffer settings to handle heavy traffic
            proxy_buffer_size 128k;
            proxy_buffers 4 256k;
            proxy_busy_buffers_size 256k;
            proxy_temp_file_write_size 256k;

            # Enable gzip compression
            gzip on;
            gzip_types text/plain text/css application/json application/javascript;
            gzip_vary on;
            gzip_min_length 1000;
            gzip_proxied any;
        }

        # Error handling for failed backends
        error_page 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/share/nginx/html;
        }
    }
    """

    # Write the configuration to nginx.conf
    config_path = "/nginx/nginx.conf"
    with open(config_path, "w") as config_file:
        config_file.write(nginx_config)
    print("NGINX configuration updated successfully")

# Restart NGINX to apply the new configuration
def restart_nginx():
    subprocess.run(["sudo", "systemctl", "restart", "nginx"])
    print("NGINX restarted successfully")

# Enable NGINX logging for performance monitoring
def enable_nginx_logging():
    access_log_config = """
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    """
    config_path = "/nginx/nginx.conf"
    
    # Append logging configuration to nginx.conf
    with open(config_path, "a") as config_file:
        config_file.write(access_log_config)
    print("NGINX logging enabled")

# Function to setup load balancing and performance monitoring
def setup_nginx_load_balancing():
    install_nginx()
    update_nginx_config()
    enable_nginx_logging()
    restart_nginx()

# Install monitoring tools
def install_monitoring_tools():
    subprocess.run(["sudo", "apt-get", "install", "-y", "prometheus-node-exporter"])
    print("Prometheus Node Exporter installed for performance metrics")

# Function to monitor server performance using NGINX logs
def monitor_server_performance():
    log_file = "/var/log/nginx/access.log"

    print("Monitoring server performance from NGINX logs...")
    with open(log_file, "r") as logs:
        for line in logs:
            print(line.strip())  # Output log for real-time monitoring

# Function to configure auto-scaling based on performance metrics
def configure_auto_scaling():
    print("Configuring auto-scaling policies based on traffic...")

    # Thresholds for adding/removing backend servers
    scale_up_threshold = 75  # CPU utilization percentage
    scale_down_threshold = 25  # CPU utilization percentage

    # Fetch CPU usage and scale backend servers accordingly
    cpu_usage = get_cpu_usage()
    if cpu_usage > scale_up_threshold:
        add_backend_server()
    elif cpu_usage < scale_down_threshold:
        remove_backend_server()

# Function to retrieve current CPU usage
def get_cpu_usage():
    # Retrieve CPU usage from system stats or monitoring tools
    cpu_usage = subprocess.check_output(["grep", "cpu", "/proc/stat"])
    return int(cpu_usage.split()[1])  # Return parsed CPU usage value

# Function to dynamically add a backend server
def add_backend_server():
    print("Adding new backend server to the upstream...")
    # Update the NGINX upstream config dynamically to add a server
    new_server = "server backend5.website.com max_fails=3 fail_timeout=30s;"
    config_path = "/nginx/nginx.conf"
    
    with open(config_path, "r") as config_file:
        content = config_file.readlines()

    for i, line in enumerate(content):
        if "upstream backend_servers {" in line:
            content.insert(i + 1, new_server)

    with open(config_path, "w") as config_file:
        config_file.writelines(content)
    
    restart_nginx()

# Function to dynamically remove a backend server
def remove_backend_server():
    print("Removing a backend server from the upstream...")
    config_path = "/nginx/nginx.conf"
    
    with open(config_path, "r") as config_file:
        content = config_file.readlines()

    for i, line in enumerate(content):
        if "server backend5.website.com" in line:
            del content[i]

    with open(config_path, "w") as config_file:
        config_file.writelines(content)
    
    restart_nginx()

# Main function to run the load balancing and monitoring setup
def main():
    setup_nginx_load_balancing()
    install_monitoring_tools()
    monitor_server_performance()
    configure_auto_scaling()

if __name__ == "__main__":
    main()