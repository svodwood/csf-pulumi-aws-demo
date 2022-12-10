# csf-pulumi-aws-demo
Demo CSF V1.1 controls using Pulumi

## Introducton
This repository contains a sample deployment of a simple Nginx web server powered by Amazon Linux 2. 
A web server is provisioned as part of an autoscaling group, deployed to a pair of private VPC subnets.
A public Application load balancer fronts the web servers and is accessible from WAN.

## CSF V1.1 Controls
The sample deployment explores implementing several controls, namely:
- PR.PT-3 "The principle of least functionality is incorporated by configuring systems to provide only essential capabilities"
- PR.PT-5 "Mechanisms (e.g., failsafe, load balancing, hot swap) are implemented to achieve resilience requirements in normal and adverse situations."

## PR.PT-3
The AWS Responsibility Matrix allignment:
1. AWS customers are responsible for configuring their systems to enforce logical access based on approved authorizations and in accordance with their access control policy. 
2. AWS customers are responsible for configuring their system to provide only essential capabilities and to prohibit or restrict the use of functions, ports, protocols, and/or services as defined in their configuration management policy. 

The following actions are implemented:
- EC2 Instance profile is attached.
- Instance in VPC.
- Instance has no public IP.

## PR.PT-5
The AWS Responsibility Matrix allignment:
1. AWS customers are responsible for developing an information security architecture for the information system that: 1) Describes the overall philosophy, requirements, and approach to be taken with regard to protecting the confidentiality, integrity, and availability of organizational information, 2) Describes how the information security architecture is integrated into and supports the enterprise architecture, and 3) Describes any information security assumptions about and dependencies on external services.
2. AWS customers are responsible for reviewing and updating the information security architecture at an organization-defined frequency to reflect updates in the enterprise architecture. Planned information security architecture changes must be reflected in the security plan, the security Concept of Operations (CONOPS), and organizational procurements/acquisitions.
3. AWS customers are responsible for configuring their systems to protect the availability of resources by allocating organization-defined resources by priority, quota, or other organization-defined security safeguard.

The following actions are implemented:
- Enable cross-zone load balancing for your Elastic Load Balancers (ELBs) to help maintain adequate capacity and availability. The cross-zone load balancing reduces the need to maintain equivalent numbers of instances in each enabled availability zone. It also improves your application's ability to handle the loss of one or more instances.
- The Elastic Load Balancer (ELB) health checks for Amazon Elastic Compute Cloud (Amazon EC2) Auto Scaling groups support maintenance of adequate capacity and availability. The load balancer periodically sends pings, attempts connections, or sends requests to test Amazon EC2 instances health in an auto-scaling group. If an instance is not reporting back, traffic is sent to a new Amazon EC2 instance.
- Ensure that Elastic Load Balancing has deletion protection enabled. Use this feature to prevent your load balancer from being accidentally or maliciously deleted, which can lead to loss of availability for your applications.

## Provisioning the Stack
Use the button below to provision the stack:

[![Deploy](https://get.pulumi.com/new/button.svg)](https://app.pulumi.com/new?template=https://github.com/svodwood/csf-pulumi-aws-demo)

## Deleting the Stack
1. Make sure you have the correct AWS CLI profile configured
2. Run 'pulumi destroy'
