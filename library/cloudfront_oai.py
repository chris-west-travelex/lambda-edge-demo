#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '0.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cloudfront_facts
short_description: Obtain facts about an AWS CloudFront distribution
description:
  - Gets information about an AWS CloudFront distribution
requirements:
  - boto3 >= 1.0.0
  - python >= 2.6
author: chris.west@travelex.com
options:
  state:
    description:
      - Create or delete the OAI
    required: false
    choices: ['present', 'absent']
    default: 'present'
  comment:
    description:
      - Comment on the OAI
    required: true
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

def create_oai(module, client, oai, comment):
    if oai:
        # if there's one with this comment already, do nothing!
        changed = False
        oai_out = oai
    else:
        # create a new one (using the comment as the CallerReference)
        response = client.create_cloud_front_origin_access_identity(
            CloudFrontOriginAccessIdentityConfig={
                'CallerReference': comment,
                'Comment': comment
            }
        )
        changed = True
        oai_out = {
            'Comment': comment,
            'Id': response['CloudFrontOriginAccessIdentity']['Id'],
            'S3CanonicalUserId': response['CloudFrontOriginAccessIdentity']['S3CanonicalUserId']
        }

    return (changed, oai_out)

def delete_oai(module, client, oai):
    if oai:
        etag = client.get_cloud_front_origin_access_identity(Id=oai['Id'])['ETag']
        client.delete_cloud_front_origin_access_identity(
            Id=oai['Id'],
            IfMatch=etag
        )
        changed = True
    else:
        # don't delete if it doesn't exist
        changed = False

    return (changed, {})

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
    state = module.params['state']
    comment = module.params['comment']

    all_oais = client.list_cloud_front_origin_access_identities()

    # TODO: page if there's more than 100!
    if all_oais['CloudFrontOriginAccessIdentityList']['IsTruncated']:
        module.fail_json(msg='CloudFront OAI list was truncated; cowardly giving up')

    oai = next((o for o in all_oais['CloudFrontOriginAccessIdentityList']['Items'] if o['Comment'] == comment), None)

    if state == 'absent':
        changed, response_dict = delete_oai(module, client, oai)
    elif state == 'present':
        changed, response_dict = create_oai(module, client, oai, comment)

    module.exit_json(changed=changed, identity=camel_dict_to_snake_dict(response_dict))

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
        comment=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
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
