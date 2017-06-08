require 'awspec'
require 'httpclient'

# cloudformation
def get_resource(stack_name, logical_resource)
  cf_client = Aws::CloudFormation::Client.new
  resource_data = cf_client.describe_stack_resource(stack_name: stack_name, logical_resource_id: logical_resource)
  resource_data[:stack_resource_detail][:physical_resource_id]
end

# s3
def s3_owner()
  s3_client = Aws::S3::Client.new
  s3_client.list_buckets[:owner][:id]
end

def s3_all_users()
  "http://acs.amazonaws.com/groups/global/AllUsers"
end

def s3_log_delivery()
  "http://acs.amazonaws.com/groups/s3/LogDelivery"
end

def s3_authenticated_users()
  "http://acs.amazonaws.com/groups/global/AuthenticatedUsers"
end

# http
def http_get(url)
  http = HTTPClient.new
  http.get url
end
