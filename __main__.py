"""Select CSF V1.1 controls using Pulumi"""

"""
The stack incorporates AWS best-practices to enforce several CSF V1.1 controls in the PR.PT-3 and PR.PT-5 families.
"""

import pulumi

import settings
import vpc
import alb
import nginx_config
import user_data
import autoscaling_group