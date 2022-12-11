import pulumi
from pulumi_aws import ec2, config, get_availability_zones
from settings import general_tags, demo_vpc_cidr, demo_private_subnet_cidrs, demo_public_subnet_cidrs, nginx_stub_status_port

"""
PR.PT-3 "The principle of least functionality is incorporated by configuring systems to provide only essential capabilities"
Responsibility Matrix:
- AWS customers are responsible for configuring their systems to enforce logical access based on approved authorizations and in accordance with their access control policy.
- AWS customers are responsible for configuring their system to provide only essential capabilities and to prohibit or restrict the use of functions, ports, protocols, and/or services as defined in their configuration management policy.

EC2 instances in VPC: 
Deploy Amazon Elastic Compute Cloud (Amazon EC2) instances within an Amazon Virtual Private Cloud (Amazon VPC) to enable secure communication between an instance and other services within the amazon VPC, without requiring an internet gateway, NAT device, or VPN connection. 
All traffic remains securely within the AWS Cloud. Because of their logical isolation, domains that reside within an Amazon VPC have an extra layer of security when compared to domains that use public endpoints. Assign Amazon EC2 instances to an Amazon VPC to properly manage access.
"""

"""
Demo Virtual Private Cloud
"""
# Create a VPC and Internet Gateway:
demo_vpc = ec2.Vpc("demo-vpc",
    cidr_block=demo_vpc_cidr,
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={**general_tags, "Name": f"demo-vpc-{config.region}"}
)

demo_igw = ec2.InternetGateway("demo-igw",
    vpc_id=demo_vpc.id,
    tags={**general_tags, "Name": f"demo-igw-{config.region}"},
    opts=pulumi.ResourceOptions(parent=demo_vpc)
)

"""
Network Access Control Lists
"""
# Creates public subnet ACL:
public_acl = ec2.NetworkAcl("demo-public-acl",
    vpc_id=demo_vpc.id,
    tags={**general_tags, "Name": f"demo-public-acl"},
    opts=pulumi.ResourceOptions(parent=demo_vpc)
)

# Creates inbound public subnet ACL rules:
public_network_acl_rule_inbound_100 = ec2.NetworkAclRule("public-nacl-inbound-100",
    network_acl_id=public_acl.id,
    rule_number=100,
    egress=False,
    protocol="tcp",
    rule_action="allow",
    cidr_block="0.0.0.0/0",
    from_port=80,
    to_port=80,
    opts=pulumi.ResourceOptions(parent=public_acl)
)

public_network_acl_rule_inbound_110 = ec2.NetworkAclRule("public-nacl-inbound-110",
    network_acl_id=public_acl.id,
    rule_number=110,
    egress=False,
    protocol="tcp",
    rule_action="allow",
    cidr_block="0.0.0.0/0",
    from_port=443,
    to_port=443,
    opts=pulumi.ResourceOptions(parent=public_acl)
)

public_network_acl_rule_inbound_120 = ec2.NetworkAclRule("public-nacl-inbound-120",
    network_acl_id=public_acl.id,
    rule_number=120,
    egress=False,
    protocol="tcp",
    rule_action="allow",
    cidr_block="0.0.0.0/0",
    from_port=1024,
    to_port=65535,
    opts=pulumi.ResourceOptions(parent=public_acl)
)

# Creates outbound public subnet ACL rules:
public_network_acl_rule_outbound_100 = ec2.NetworkAclRule("public-nacl-outbound-100",
    network_acl_id=public_acl.id,
    rule_number=100,
    egress=True,
    protocol="tcp",
    rule_action="allow",
    cidr_block="0.0.0.0/0",
    from_port=80,
    to_port=80,
    opts=pulumi.ResourceOptions(parent=public_acl)
)

public_network_acl_rule_outbound_110 = ec2.NetworkAclRule("public-nacl-outbound-110",
    network_acl_id=public_acl.id,
    rule_number=110,
    egress=True,
    protocol="tcp",
    rule_action="allow",
    cidr_block="0.0.0.0/0",
    from_port=443,
    to_port=443,
    opts=pulumi.ResourceOptions(parent=public_acl)
)

public_network_acl_rule_outbound_120 = ec2.NetworkAclRule("public-nacl-outbound-120",
    network_acl_id=public_acl.id,
    rule_number=120,
    egress=True,
    protocol="tcp",
    rule_action="allow",
    cidr_block="0.0.0.0/0",
    from_port=1024,
    to_port=65535,
    opts=pulumi.ResourceOptions(parent=public_acl)
)

# Creates private subnet ACL:
private_acl = ec2.NetworkAcl("demo-private-acl",
    vpc_id=demo_vpc.id,
    tags={**general_tags, "Name": f"demo-private-acl"},
    opts=pulumi.ResourceOptions(parent=demo_vpc)
)

# Create inbound private subnet ACL rules:
private_network_acl_rule_inbound_100 = ec2.NetworkAclRule("private-nacl-inbound-100",
    network_acl_id=private_acl.id,
    rule_number=100,
    egress=False,
    protocol="tcp",
    rule_action="allow",
    cidr_block=demo_vpc_cidr,
    from_port=80,
    to_port=80,
    opts=pulumi.ResourceOptions(parent=private_acl)
)

private_network_acl_rule_inbound_110 = ec2.NetworkAclRule("private-nacl-inbound-110",
    network_acl_id=private_acl.id,
    rule_number=110,
    egress=False,
    protocol="tcp",
    rule_action="allow",
    cidr_block=demo_vpc_cidr,
    from_port=443,
    to_port=443,
    opts=pulumi.ResourceOptions(parent=private_acl)
)

private_network_acl_rule_inbound_120 = ec2.NetworkAclRule("private-nacl-inbound-120",
    network_acl_id=private_acl.id,
    rule_number=120,
    egress=False,
    protocol="tcp",
    rule_action="allow",
    cidr_block=demo_vpc_cidr,
    from_port=int(nginx_stub_status_port),
    to_port=int(nginx_stub_status_port),
    opts=pulumi.ResourceOptions(parent=private_acl)
)

private_network_acl_rule_inbound_130 = ec2.NetworkAclRule("private-nacl-inbound-130",
    network_acl_id=private_acl.id,
    rule_number=130,
    egress=False,
    protocol="tcp",
    rule_action="allow",
    cidr_block="0.0.0.0/0",
    from_port=1024,
    to_port=65535,
    opts=pulumi.ResourceOptions(parent=private_acl)
)

# Create outbound private subnet ACL rules:
private_network_acl_rule_outbound_100 = ec2.NetworkAclRule("private-nacl-outbound-100",
    network_acl_id=private_acl.id,
    rule_number=100,
    egress=True,
    protocol="tcp",
    rule_action="allow",
    cidr_block="0.0.0.0/0",
    from_port=80,
    to_port=80,
    opts=pulumi.ResourceOptions(parent=private_acl)
)

private_network_acl_rule_outbound_110 = ec2.NetworkAclRule("private-nacl-outbound-110",
    network_acl_id=private_acl.id,
    rule_number=110,
    egress=True,
    protocol="tcp",
    rule_action="allow",
    cidr_block="0.0.0.0/0",
    from_port=443,
    to_port=443,
    opts=pulumi.ResourceOptions(parent=private_acl)
)

private_network_acl_rule_outbound_120 = ec2.NetworkAclRule("private-nacl-outbound-120",
    network_acl_id=private_acl.id,
    rule_number=120,
    egress=True,
    protocol="tcp",
    rule_action="allow",
    cidr_block="0.0.0.0/0",
    from_port=1024,
    to_port=65535,
    opts=pulumi.ResourceOptions(parent=private_acl)
)

"""
Demo Subnet Topology: two public subnets and two private subnets
"""
# Create subnets:
demo_azs = get_availability_zones(state="available").names
demo_public_subnets = []
demo_private_subnets = []

for i in range(2):
    prefix = f"{demo_azs[i]}"
    
    demo_public_subnet = ec2.Subnet(f"demo-public-subnet-{prefix}",
        vpc_id=demo_vpc.id,
        cidr_block=demo_public_subnet_cidrs[i],
        availability_zone=demo_azs[i],
        tags={**general_tags, "Name": f"demo-public-subnet-{prefix}"},
        opts=pulumi.ResourceOptions(parent=demo_vpc)
    )
    
    demo_public_nacl_association = ec2.NetworkAclAssociation(f"public-nacl-association-{prefix}",
        network_acl_id=public_acl.id,
        subnet_id=demo_public_subnet.id,
        opts=pulumi.ResourceOptions(parent=demo_public_subnet)
    )
    
    demo_public_subnets.append(demo_public_subnet)

    demo_public_route_table = ec2.RouteTable(f"demo-public-rt-{prefix}",
        vpc_id=demo_vpc.id,
        tags={**general_tags, "Name": f"demo-public-rt-{prefix}"},
        opts=pulumi.ResourceOptions(parent=demo_public_subnet)
    )
    
    demo_public_route_table_association = ec2.RouteTableAssociation(f"demo-public-rt-association-{prefix}",
        route_table_id=demo_public_route_table.id,
        subnet_id=demo_public_subnet.id,
        opts=pulumi.ResourceOptions(parent=demo_public_subnet)
    )

    demo_public_wan_route = ec2.Route(f"demo-public-wan-route-{prefix}",
        route_table_id=demo_public_route_table.id,
        gateway_id=demo_igw.id,
        destination_cidr_block="0.0.0.0/0",
        opts=pulumi.ResourceOptions(parent=demo_public_subnet)
    )

    demo_eip = ec2.Eip(f"demo-eip-{prefix}",
        tags={**general_tags, "Name": f"demo-eip-{prefix}"},
        opts=pulumi.ResourceOptions(parent=demo_vpc)
    )
    
    demo_nat_gateway = ec2.NatGateway(f"demo-nat-gateway-{prefix}",
        allocation_id=demo_eip.id,
        subnet_id=demo_public_subnet.id,
        tags={**general_tags, "Name": f"demo-nat-{prefix}"},
        opts=pulumi.ResourceOptions(
            depends_on=[demo_vpc],
            parent=demo_vpc
        )
    )

    demo_private_subnet = ec2.Subnet(f"demo-private-subnet-{prefix}",
        vpc_id=demo_vpc.id,
        cidr_block=demo_private_subnet_cidrs[i],
        availability_zone=demo_azs[i],
        tags={**general_tags, "Name": f"demo-private-subnet-{prefix}"},
        opts=pulumi.ResourceOptions(parent=demo_vpc)
    )
    
    demo_private_nacl_association = ec2.NetworkAclAssociation(f"private-nacl-association-{prefix}",
        network_acl_id=private_acl.id,
        subnet_id=demo_private_subnet.id,
        opts=pulumi.ResourceOptions(parent=demo_private_subnet)
    )
    
    demo_private_subnets.append(demo_private_subnet)

    demo_private_route_table = ec2.RouteTable(f"demo-private-rt-{prefix}",
        vpc_id=demo_vpc.id,
        tags={**general_tags, "Name": f"demo-private-rt-{prefix}"},
        opts=pulumi.ResourceOptions(parent=demo_private_subnet)
    )
    
    demo_private_route_table_association = ec2.RouteTableAssociation(f"demo-private-rt-association-{prefix}",
        route_table_id=demo_private_route_table.id,
        subnet_id=demo_private_subnet.id,
        opts=pulumi.ResourceOptions(parent=demo_private_subnet)
    )

    demo_private_wan_route = ec2.Route(f"demo-private-wan-route-{prefix}",
        route_table_id=demo_private_route_table.id,
        nat_gateway_id=demo_nat_gateway.id,
        destination_cidr_block="0.0.0.0/0",
        opts=pulumi.ResourceOptions(parent=demo_private_subnet)
    )

"""
Private Endpoints in the Demo Virtual Private Cloud
"""
# Creates an SSM Parameter Store endpoint security group:
demo_sg_ssm_endpoint = ec2.SecurityGroup("demo-vpc-ssm-security-group",
    description="Allow fetching SSM parameters from private subnets",
    vpc_id=demo_vpc.id,
    ingress=[ec2.SecurityGroupIngressArgs(
        description="Allow HTTPS communication with SSM Parameter Store",
        from_port=443,
        to_port=443,
        protocol="tcp",
        cidr_blocks=[demo_vpc_cidr]
    )],
    egress=[ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"]
    )],
    tags={**general_tags, "Name": f"demo-vpc-ssm-sg-{config.region}"},
    opts=pulumi.ResourceOptions(parent=demo_vpc)
)

# Creates VPC Endpoints to enable private communication to SSM Parameter Store:
ssm_endpoint_services = ["ssm", "ssmmessages", "ec2messages"]
ssm_vpc_endpoints = []
for endpoint_service in ssm_endpoint_services:
    ssm_vpc_endpoints.append(ec2.VpcEndpoint(f"demo-endpoint-{endpoint_service}",
        vpc_id=demo_vpc.id,
        service_name=f"com.amazonaws.{config.region}.{endpoint_service}",
        vpc_endpoint_type="Interface",
        subnet_ids=demo_private_subnets,
        security_group_ids=[demo_sg_ssm_endpoint.id],
        tags={**general_tags, "Name": f"demo-{endpoint_service}-endpoint-{config.region}"},
        opts=pulumi.ResourceOptions(parent=demo_vpc)))

# Creates an S3 endpoint security group:
demo_sg_s3_endpoint = ec2.SecurityGroup("demo-vpc-s3-security-group",
    description="Allow fetching S3 content from private subnets",
    vpc_id=demo_vpc.id,
    ingress=[ec2.SecurityGroupIngressArgs(
        description="Allow HTTPS communication with S3",
        from_port=443,
        to_port=443,
        protocol="tcp",
        cidr_blocks=[demo_vpc_cidr]
    )],
    egress=[ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"]
    )],
    tags={**general_tags, "Name": f"demo-vpc-s3-sg-{config.region}"},
    opts=pulumi.ResourceOptions(parent=demo_vpc)
)

# Creates an S3 VPC Endpoint:
demo_s3_endpoint = ec2.VpcEndpoint("demo-endpoint-s3",
    vpc_id=demo_vpc.id,
    service_name=f"com.amazonaws.{config.region}.s3",
    vpc_endpoint_type="Interface",
    subnet_ids=demo_private_subnets,
    security_group_ids=[demo_sg_s3_endpoint.id],
    tags={**general_tags, "Name": f"demo-s3-endpoint-{config.region}"},
    opts=pulumi.ResourceOptions(parent=demo_vpc))