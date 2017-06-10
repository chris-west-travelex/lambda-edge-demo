require 'spec_helper'

awsenv = ENV['AWS_ENVIRONMENT']

assets_bucket = get_resource("#{awsenv}-cdn", "CDNAssets")
logging_bucket = get_resource("#{awsenv}-cdn", "CDNLogs")
cloudfront_distro = get_resource("#{awsenv}-cdn", "CDN")

context 'oai' do
  describe(cloudfront_oai("#{awsenv}-oai")) do
    it { should be }
    its(:comment) { should eq "#{awsenv}-oai" }
  end

end

context 'cloudfront' do
  describe(cloudfront_distribution(cloudfront_distro)) do
    it { should exist }
    it { should be_deployed }
    it { should have_origin_domain_name "#{assets_bucket}.s3.amazonaws.com" }
    its(:price_class) { should eq "PriceClass_100" }
    its(:http_version) { should eq "HTTP2" }
    #its(:is_ipv6_enabled) { should be_true }
  end

  xit 'redirects http to https' do
    expect(http_get("http://TODO").status_code).to eq 301
  end

  # TODO
  #  - there should be an index.html
end
