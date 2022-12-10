from jinja2 import Template
from pulumi_aws import ssm
from settings import nginx_stub_status_port, nginx_stub_status_config_parameter_path, general_tags, demo_vpc_cidr, nginx_stub_statuc_path

"""
Configures Nginx to enable stub status module:
"""
# Creates a stub status configuration file template:
demo_nginx_stub_status_configuration_file = Template("""
server {
        listen 0.0.0.0:{{ port }};
        access_log off;
        allow {{ cidr }};
        location = /{{ path }} {
                stub_status;
        }
}
""")

# Renders demo_nginx_stub_status_configuration_file template:
demo_nginx_stub_status_configuration = demo_nginx_stub_status_configuration_file.render(port=nginx_stub_status_port, path=nginx_stub_statuc_path, cidr=demo_vpc_cidr)

# Creates an SSM Parameter for stub status configuration:
demo_nginx_configuration_parameter = ssm.Parameter("demo-nginx-stub-config",
    type="String",
    data_type="text",
    name=nginx_stub_status_config_parameter_path,
    tags={**general_tags, "Name": "demo-nginx-config"},
    value=demo_nginx_stub_status_configuration
)