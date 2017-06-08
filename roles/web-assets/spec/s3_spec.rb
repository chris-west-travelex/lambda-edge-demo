require 'spec_helper'

awsenv = ENV['AWS_ENVIRONMENT']

assets_bucket = get_resource("#{awsenv}-cdn", "CDNAssets")
logging_bucket = get_resource("#{awsenv}-cdn", "CDNLogs")

context 'assets bucket' do
  describe s3_bucket(assets_bucket) do
    it { should exist }
    it { should have_acl_grant(grantee: s3_owner, permission: 'FULL_CONTROL') }
    it { should have_acl_grant(grantee: s3_all_users, permission: 'READ') }
    it { should have_cors_rule(
                  allowed_methods: ['GET', 'HEAD'],
                  allowed_origins: ['*']
                ) }
    it { should have_logging_enabled(target_bucket: logging_bucket, target_prefix: 's3/') }
  end

  its 'content is public' do
    expect(http_get("http://s3-eu-west-1.amazonaws.com/#{assets_bucket}").status_code).to eq 200
  end

end

context 'logging bucket' do
  describe s3_bucket(logging_bucket) do
    it { should exist }
    it { should have_acl_grant(grantee: s3_log_delivery, permission: 'WRITE') }
    it { should_not have_acl_grant(grantee: s3_all_users, permission: 'READ') }
  end

  its 'content is not public' do
    expect(http_get("http://s3-eu-west-1.amazonaws.com/#{logging_bucket}").status_code).to eq 403
  end

  its 'logs cannot be deleted' do
    s3 = Aws::S3::Client.new
    a_log = s3.list_objects(bucket: logging_bucket, prefix: "s3/")[:contents][0]
    expect { s3.delete_object(bucket: logging_bucket, key: a_log.key) }.to raise_error Aws::S3::Errors::AccessDenied
  end
end
