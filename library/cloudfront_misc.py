#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '0.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cloudfront_misc
short_description: Change miscellaneous CloudFront distribution attributes
description:
  - Manages attributes of a CloudFront distribution that can't be updated via CloudFormation (e.g. IPV6; Lambda@Edge)
requirements:
  - boto3 >= 1.0.0
  - python >= 2.6
author: chris.west@travelex.com
options:
  id:
    description:
      - CloudFront distribution id
    required: true
  is_ipv6_enabled:
    description:
      - Whether to enable IPv6 in this distribution
    required: false
    choices: ['true', 'false']
  lambda_assoc_eventtype:
    description:
      - Define the EventType for a single lambda function association
    required: false
    choices: ['viewer-request', 'viewer-response', 'origin-request', 'origin-response']
  lambda_assoc_arn:
    description:
      - Define the ARN for a single lambda function association
    required: false
'''

import json
import traceback
from ansible.module_utils.basic import AnsibleModule

try:
    import botocore
    HAS_BOTOCORE = True
except ImportError:
    HAS_BOTOCORE = False

try:
    import boto3
except ImportError:
    # will be caught by imported HAS_BOTO3
    pass

from ansible.module_utils.ec2 import ec2_argument_spec, get_aws_connection_info, boto3_conn, HAS_BOTO3, camel_dict_to_snake_dict

def update_is_ipv6_enabled(distro_config, is_ipv6_enabled):
    if distro_config['IsIPV6Enabled'] != is_ipv6_enabled:
        distro_config['IsIPV6Enabled'] = is_ipv6_enabled
        return True
    else:
        return False

def update_lambda_assoc(distro_config, eventtype, arn):
    if distro_config['DefaultCacheBehavior']['LambdaFunctionAssociations']['Quantity'] != 1 or \
      distro_config['DefaultCacheBehavior']['LambdaFunctionAssociations']['Items'][0]['EventType'] != eventtype or \
      distro_config['DefaultCacheBehavior']['LambdaFunctionAssociations']['Items'][0]['LambdaFunctionARN'] != arn:
        # we're going to be changing _something_ !
        distro_config['DefaultCacheBehavior']['LambdaFunctionAssociations'] = {
            'Quantity': 1,
            'Items': [{
                'EventType': eventtype,
                'LambdaFunctionARN': arn
            }]
        }
        return True

    else:
        return False
        
def core(module):
    region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
    if not region:
        module.fail_json(msg='region must be specified')

    client = None
    try:
        client = boto3_conn(module, conn_type='client', resource='cloudfront',
                            region=region, endpoint=ec2_url, **aws_connect_kwargs)
    except (botocore.exceptions.ClientError, botocore.exceptions.ValidationError) as e:
        module.fail_json(msg='Failed while connecting to the cloudfront service: %s' % e, exception=traceback.format_exc())

    changed = False

    is_ipv6_enabled = module.params['is_ipv6_enabled']
    lambda_assoc_eventtype = module.params['lambda_assoc_eventtype']
    lambda_assoc_arn = module.params['lambda_assoc_arn']

    try:
        distro = client.get_distribution_config(Id=module.params['id'])
        etag = distro['ETag']
        distro_config = distro['DistributionConfig']
    except (botocore.exceptions.NoSuchDistribution) as e:
        module.fail_json(msg='Failed to retrieve distribution %s: %s' % (module.params['Id'], e), exception=traceback.format_exc())

    if is_ipv6_enabled is not None:
        changed = update_is_ipv6_enabled(distro_config, is_ipv6_enabled) or changed

    if lambda_assoc_eventtype is not None and lambda_assoc_arn is not None:
        changed = update_lambda_assoc(distro_config, lambda_assoc_eventtype, lambda_assoc_arn) or changed

    if changed:
        response = client.update_distribution(
            DistributionConfig=distro_config,
            Id=module.params['id'],
            IfMatch=etag
        )
        distro_config = response['Distribution']['DistributionConfig']

    module.exit_json(changed=changed, config=camel_dict_to_snake_dict(distro_config))

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
        id=dict(type='str', required=True),
        is_ipv6_enabled=dict(type='bool', required=False),
        lambda_assoc_eventtype=dict(type='str', required=False),
        lambda_assoc_arn=dict(type='str', required=False),
    ))

    module = AnsibleModule(argument_spec=argument_spec)

    if not HAS_BOTO3:
        module.fail_json(msg='Python module "boto3" is missing, please install it')

    if not HAS_BOTOCORE:
        module.fail_json(msg='Python module "botocore" is missing, please install it')

    try:
        core(module)
    except (botocore.exceptions.ClientError, Exception) as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())

if __name__ == '__main__':
    main()
