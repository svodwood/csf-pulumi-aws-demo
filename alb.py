import pulumi
from pulumi_aws import lb, ec2, config
from vpc import demo_vpc, demo_public_subnets, demo_private_subnets
from settings import general_tags, nginx_stub_status_port, nginx_stub_statuc_path

"""
PR.PT-5 "Mechanisms (e.g., failsafe, load balancing, hot swap) are implemented to achieve resilience requirements in normal and adverse situations."
Responsibility matrix:
- AWS customers are responsible for developing an information security architecture for the information system that: 
    1) Describes the overall philosophy, requirements, and approach to be taken with regard to protecting the confidentiality, integrity, and availability of organizational information, 
    2) Describes how the information security architecture is integrated into and supports the enterprise architecture, and 
    3) Describes any information security assumptions about and dependencies on external services. 
- AWS customers are responsible for configuring their systems to protect the availability of resources by allocating organization-defined resources by priority, quota, or other organization-defined security safeguard.

Cross-zone Load Balancing:
Enable cross-zone load balancing for your Elastic Load Balancers (ELBs) to help maintain adequate capacity and availability. 
The cross-zone load balancing reduces the need to maintain equivalent numbers of instances in each enabled availability zone. 
It also improves your application's ability to handle the loss of one or more instances.

Elastic Load Balancing Health Checks:
The Elastic Load Balancer (ELB) health checks for Amazon Elastic Compute Cloud (Amazon EC2) Auto Scaling groups support maintenance of adequate capacity and availability. 
The load balancer periodically sends pings, attempts connections, or sends requests to test Amazon EC2 instances health in an auto-scaling group. 
If an instance is not reporting back, traffic is sent to a new Amazon EC2 instance.

Elastic Load Balancer Deletion Protection:
Ensure that Elastic Load Balancing has deletion protection enabled. 
Use this feature to prevent your load balancer from being accidentally or maliciously deleted, which can lead to loss of availability for your applications.
"""

"""
Demo AWS Application Load Balancer
"""
# Creates an Application Load Balancer security group:
demo_sg_alb = ec2.SecurityGroup("demo-alb-security-group",
    description="Allow inbound traffic from WAN over HTTP",
    vpc_id=demo_vpc.id,
    ingress=[ec2.SecurityGroupIngressArgs(
        description="Allow HTTP from WAN",
        from_port=80,
        to_port=80,
        protocol="tcp",
        cidr_blocks=["0.0.0.0/0"]
    )],
    egress=[ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"]
    )],
    tags={**general_tags, "Name": f"demo-sg-{config.region}"},
    opts=pulumi.ResourceOptions(parent=demo_vpc)
)
# Creates an internet-facing Application Load Balancer in public subnets:
demo_alb = lb.LoadBalancer("demo-pub-alb",
    internal=False,
    load_balancer_type="application",
    security_groups=[demo_sg_alb.id],
    subnets=demo_public_subnets,
    enable_cross_zone_load_balancing=True, # <-------------PR.PT-5 Control (Cross-zone Load Balancing)
    enable_deletion_protection=True, # <------------------ PR.PT-5 Control (ALB Deletion Protection)
    tags={**general_tags, "Name": "demo-public-alb"}
)

# Creates an Application Load Balancer Target Group:
demo_target_group = lb.TargetGroup("demo-target-group",
    port=80,
    protocol="HTTP",
    vpc_id=demo_vpc.id,
    tags={**general_tags, "Name": "demo-alb-target-group"},
    health_check=lb.TargetGroupHealthCheckArgs(
        enabled=True, # <--------------------------------- PR.PT-5 Control (Healthchecks Enabled)
        healthy_threshold=3,
        interval=6,
        protocol="HTTP",
        port=nginx_stub_status_port,
        path=f"/{nginx_stub_statuc_path}"
    ),
    opts=pulumi.ResourceOptions(parent=demo_alb)
)

# Creates a listener for the Application Load Balancer:
demo_listener = lb.Listener("demo-pub-alb-listener",
    load_balancer_arn=demo_alb.arn,
    port=80,
    protocol="HTTP",
    default_actions=[lb.ListenerDefaultActionArgs(
        type="forward",
        target_group_arn=demo_target_group.arn,
    )],
    opts=pulumi.ResourceOptions(parent=demo_alb)
)