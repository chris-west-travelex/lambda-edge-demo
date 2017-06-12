require 'awspec'
require 'httpclient'
require 'yaml'

# cloudformation
def get_resource(stack_name, logical_resource)
  cf_client = Aws::CloudFormation::Client.new
  begin
    resource_data = cf_client.describe_stack_resource(stack_name: stack_name, logical_resource_id: logical_resource)
    resource_data[:stack_resource_detail][:physical_resource_id]
  rescue Aws::CloudFormation::Errors::ValidationError
    "__Resource_Missing__"
  end
end

def get_parameter(stack_name, parameter_key)
  cf_client = Aws::CloudFormation::Client.new
  begin
    params = cf_client.describe_stacks(stack_name: stack_name)[:stacks][0][:parameters]
    params.select {|p| p[:parameter_key] == parameter_key}[0][:parameter_value]
  rescue Aws::CloudFormation::Errors::ValidationError
    "__Resource_Missing__"
  rescue NoMethodError
    "__Parameter_Missing__"
  end
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

# cloudfront
def cloudfront_oai(comment)
  cf_client = Aws::CloudFront::Client.new
  matching_idents = cf_client.list_cloud_front_origin_access_identities[:cloud_front_origin_access_identity_list][:items].select {|x| x[:comment] == comment}
  if matching_idents.length == 1 then
    matching_idents[0]
  else
    # duplicates will also cause trouble! make the tests fail
    nil
  end
end

def cloudfront_domain
  # ... from ansible(!)
  YAML::load_file(File::dirname(__FILE__) + "/../group_vars/" + ENV['AWS_ENVIRONMENT'] + "/vars")['domain_name']
end

# lambda
def lambda_call(fn, payload)
  l_client = Aws::Lambda::Client.new
  l_client.invoke function_name: fn, payload: payload
end

def lambda_config(fn)
  l_client = Aws::Lambda::Client.new
  l_client.get_function_configuration function_name: fn
end

# http
def http_get(url)
  http = HTTPClient.new
  begin
    http.get url
  rescue Exception => e
    # swallow errors and return, so that we don't crash rspec
    {error: e}
  end
end
