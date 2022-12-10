from jinja2 import Template
import base64

from pulumi_aws import config
from settings import nginx_stub_status_config_parameter_path, nginx_config_file_path

"""
EC2 Web Server Instance User Data Script
"""
# Creates user data bash script template:
demo_webserver_user_data_template = Template("""
#!/bin/bash
# Run an update
yum update -y

# Install Nginx and configure the stub_status module
amazon-linux-extras install nginx1.12 -y
aws ssm get-parameter --name {{ nginx_stub_status_config_parameter_path }} --region {{ region }} --output text --query Parameter.Value > {{ nginx_config_file_path }}

# Start Nginx
systemctl daemon-reload && systemctl enable nginx && systemctl start nginx
""")

# Renders the user data template:
demo_webserver_user_data = demo_webserver_user_data_template.render(
    nginx_stub_status_config_parameter_path=nginx_stub_status_config_parameter_path, 
    region=config.region,
    nginx_config_file_path=nginx_config_file_path
)

# Encodes the user data to be used in a launch template:
demo_webserver_user_data_b64 = base64.b64encode(demo_webserver_user_data.encode()).decode()