import json
from pulumi_aws import ec2, iam, autoscaling, config
from pulumi import ResourceOptions

from user_data import demo_webserver_user_data_b64
from settings import ssh_key_name, general_tags, cluster_name, nginx_stub_status_port
from vpc import demo_private_subnets, demo_s3_endpoint, demo_sg_s3_endpoint, demo_vpc
from alb import demo_target_group, demo_sg_alb

"""
PR.PT-3 "The principle of least functionality is incorporated by configuring systems to provide only essential capabilities"
Responsibility Matrix:
- AWS customers are responsible for configuring their systems to enforce logical access based on approved authorizations and in accordance with their access control policy.
- AWS customers are responsible for configuring their system to provide only essential capabilities and to prohibit or restrict the use of functions, ports, protocols, and/or services as defined in their configuration management policy.

EC2 Instance profile is attached:
EC2 instance profiles pass an IAM role to an EC2 instance. 
Attaching an instance profile to your instances can assist with least privilege and permissions management.

Instance has no public IP:
Manage access to the AWS Cloud by ensuring Amazon Elastic Compute Cloud (Amazon EC2) instances cannot be publicly accessed. 
Amazon EC2 instances can contain sensitive information and access control is required for such accounts.
"""

"""
EC2 Configuration: Launch Template, Autoscaling Group and Security Group
"""
# Fetch an Amazon Linux 2 AMI
demo_ami = ec2.get_ami(most_recent=True,
    filters=[
        ec2.GetAmiFilterArgs(
            name="name",
            values=["amzn2-ami-kernel-5.10-*"],
        ),
        ec2.GetAmiFilterArgs(
            name="virtualization-type",
            values=["hvm"],
        ),
        ec2.GetAmiFilterArgs(
            name="root-device-type",
            values=["ebs"],
        ),
        ec2.GetAmiFilterArgs(
            name="architecture",
            values=["x86_64"]
        )
    ],
    owners=["amazon"]
)

# Create a least-privilege IAM role to allow fetching configuration from SSM Parameter Store:
aws_managed_instance_profile_policy_arns = [
    "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
    "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
]

demo_instance_role = iam.Role("demo-instance-role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Sid": "",
            "Principal": {
                "Service": "ec2.amazonaws.com",
            },
        }],
    }),
    tags={**general_tags, "Name": "demo-instance-role"}
)

for i, policy_arn in enumerate(aws_managed_instance_profile_policy_arns):
    demo_role_policy_attachment = iam.RolePolicyAttachment(f"demo-role-policy-attachment-{i}",
        role=demo_instance_role.name,
        policy_arn=policy_arn
    ),
    opts=ResourceOptions(parent=demo_instance_role)

# Creates a list-privilege instance profile:
demo_instance_profile = iam.InstanceProfile("demo-instance-profile", role=demo_instance_role.name)

# Creates a web server security group:
demo_sg_webserver = ec2.SecurityGroup("demo-webserver-security-group",
    description="Allow HTTP from the Public ALB",
    vpc_id=demo_vpc.id,
    tags={**general_tags, "Name": f"demo-webserver-sg-{config.region}"}
)

# Creates web server security group rules:
sgr_webserver_traffic = ec2.SecurityGroupRule("sgr-webserver-traffic",
    type="ingress",
    from_port=80,
    to_port=80,
    protocol="tcp",
    source_security_group_id=demo_sg_alb.id,
    security_group_id=demo_sg_webserver.id
)
sgr_webserver_healthcheck = ec2.SecurityGroupRule("sgr-webserver-healthcheck",
    type="ingress",
    from_port=int(nginx_stub_status_port),
    to_port=int(nginx_stub_status_port),
    protocol="tcp",
    source_security_group_id=demo_sg_alb.id,
    security_group_id=demo_sg_webserver.id
)
sgr_webserver_egress = ec2.SecurityGroupRule("sgr-webserver-egress",
    type="egress",
    from_port=0,
    to_port=0,
    protocol="-1",
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=demo_sg_webserver.id
)

# Creates an autoscaling group launch template:
demo_launch_template = ec2.LaunchTemplate("demo-launch-template",
    key_name=ssh_key_name,
    instance_type="t3.small",
    iam_instance_profile=ec2.LaunchTemplateIamInstanceProfileArgs(
        name=demo_instance_profile.name # <------------------------ PR.PT-3 Control (EC2 Instance profile is attached)
    ),
    image_id=demo_ami.image_id,
    network_interfaces=[ec2.LaunchTemplateNetworkInterfaceArgs(
        associate_public_ip_address="false", # <------------------- PR.PT-3 Control (EC2 Instance has no public IP)
        security_groups=[demo_sg_webserver.id]
    )],
    tags={**general_tags, "Name": "demo-launch-template"},
    user_data=demo_webserver_user_data_b64,
    update_default_version=True,
    tag_specifications=[ec2.LaunchTemplateTagSpecificationArgs(
        resource_type="instance",
        tags={**general_tags, "Name": "demo-webserver"}
    )],
    opts=ResourceOptions(depends_on=[demo_s3_endpoint])
)

# Creates an autoscaling group:
demo_autoscaling_group = autoscaling.Group("demo-autoscaling-group",
    max_size=4,
    min_size=4,
    name=cluster_name,
    enabled_metrics=["GroupMinSize","GroupMaxSize","GroupDesiredCapacity","GroupInServiceInstances","GroupPendingInstances","GroupStandbyInstances","GroupTerminatingInstances","GroupTotalInstances"],
    vpc_zone_identifiers=demo_private_subnets,
    launch_template=autoscaling.GroupLaunchTemplateArgs(
        id=demo_launch_template.id,
        version=demo_launch_template.latest_version
    ),
    default_instance_warmup=2,
    instance_refresh=autoscaling.GroupInstanceRefreshArgs(
        strategy="Rolling",
        preferences=autoscaling.GroupInstanceRefreshPreferencesArgs(
            min_healthy_percentage=50
        ),
        triggers=["tag"],
    ),
    tags=[autoscaling.GroupTagArgs(
        key="Name",
        value="demo-workload-node",
        propagate_at_launch=True
    )],
    opts=ResourceOptions(
        ignore_changes=["target_group_arns"],
        depends_on=[demo_vpc, demo_s3_endpoint, demo_sg_s3_endpoint]
    )
)

# Creates an autoscaling group to ALB target group attachment:
demo_autoscaling_group_attachment = autoscaling.Attachment("demo-autoscaling-attachment",
    autoscaling_group_name=demo_autoscaling_group,
    lb_target_group_arn=demo_target_group.arn
)