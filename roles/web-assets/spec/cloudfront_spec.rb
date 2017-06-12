require 'spec_helper'

awsenv = ENV['AWS_ENVIRONMENT']

assets_bucket = get_resource("#{awsenv}-cdn", "CDNAssets")
cloudfront_distro = get_resource("#{awsenv}-cdn", "CDN")
edge_lambda = get_resource("#{awsenv}-cdn", "CDNLambda")

context 'oai' do
  describe(cloudfront_oai("#{awsenv}-oai")) do
    it { should be }
    its(:comment) { should eq "#{awsenv}-oai" }
  end

end

# TODO: this doesn't work because the ACM cert is in a different region!
#context 'acm' do
#  describe(acm(cloudfront_domain)) do
#    it { should exist }
#  end
#end

context 'cloudfront' do
  describe(cloudfront_distribution(cloudfront_distro)) do
    it { should exist }
    it { should be_deployed }
    it { should have_origin_domain_name "#{assets_bucket}.s3.amazonaws.com" }
    its(:price_class) { should eq "PriceClass_100" }
    its(:http_version) { should eq "HTTP2" }
    its(:is_ipv6_enabled) { should be true }
  end

  it 'redirects http to https' do
    expect(http_get("http://#{cloudfront_domain}").status_code).to eq 301
  end

  describe(http_get("https://#{cloudfront_domain}")) do
    its(:status_code) { should eq 200 }
    its(:headers) { should include("X-Content-Type-Options" => "nosniff") }
    its(:headers) { should include("X-Frame-Options" => "DENY") }
    its(:headers) { should include("X-XSS-Protection" => "1; mode=block") }
    its(:headers) { should include("Referrer-Policy" => "same-origin") }
    its(:headers) { should include("Content-Security-Policy" => "default-src 'none'; script-src 'self'; connect-src 'self'; img-src 'self'; style-src 'self';") }
    its(:headers) { should include("Expect-CT" => "enforce; max-age=31536000;") }
  end
  # TODO
  #  - there should be an index.html
  #  - a GET on index.html should return the right headers
  #  - logs should be written in the right places in the logging bucket
  #    (or at least the prefixes exist)
end

context 'lambda' do
  payload = <<-EOF
    {
      "Records": [{
        "cf": {
          "config": {"distributionId": "EXAMPLE"},
          "response": {
            "status": "200",
            "headers": {
              "Last-Modified": ["2016-11-25"],
              "Vary": ["*"],
              "X-Amz-Meta-Last-Modified": ["2016-01-01"]
            },
            "statusDescription": "HTTP OK",
            "httpVersion": "2.0"
          }
        }
      }]
    }
  EOF
  describe(lambda_config(edge_lambda)) do
    its(:runtime) { should eq "nodejs4.3-edge" }
  end

  describe(lambda_call(edge_lambda, payload)) do
    its(:status_code) { should eq 200 }
    its(:function_error) { should be_nil }

    # TODO
    #  - the right headers are set
  end
end
