import pulumi

project_config = pulumi.Config()
stack = pulumi.get_stack()
project = pulumi.get_project()

"""
General Resource Tags
"""
general_tags = {
    "pulumi-project": f"{project}",
    "pulumi-stack": f"{stack}"
}

"""
VPC Configuration
"""
demo_vpc_cidr = "10.100.0.0/16"
demo_public_subnet_cidrs = [
    "10.100.0.0/20",
    "10.100.16.0/20"
]
demo_private_subnet_cidrs = [
    "10.100.32.0/20",
    "10.100.48.0/20"
]

"""
EC2 Instance Configuration
"""
ssh_key_name = project_config.require("ssh-key-name")

"""
Autoscaling Configuration
"""
cluster_name = "demoWebCluster"

"""
SSM Parameter Store Configuration
"""
nginx_stub_status_config_parameter_path = f"/{cluster_name}/nginx_stub_status_config"

"""
Nginx Configuration
"""
nginx_config_file_path = "/etc/nginx/conf.d/nginx-status.conf"
nginx_stub_status_port = "8113"
nginx_stub_statuc_path = "metrics"