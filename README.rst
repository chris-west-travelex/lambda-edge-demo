Lambda@Edge Demo
================

This is a simple demo that uses Lambda@Edge to secure the HTTP headers of a
web-site hosted in CloudFront and S3. Resources are provisioned using a
combination of Ansible and CloudFormation, and tested using ``awspec``.

In detail, this creates:

* a CloudFront distribution with a secure set of defaults
* S3 buckets for the web-site and CDN/S3 access logs
* an ACM certificate for a custom domain
* a Lambda@Edge function that injects secure headers in the viewer response


Installation
------------

Here's the laundry-list of dependencies that you need for this to work:

* Python + pip
* Ruby + bundler
* jq
* openssl

To install the remainder of the command-line and library dependencies, run:

.. code-block:: bash

    $ pip install -r requirements.txt
    $ bundle install

You will also need to have administrative access to a DNS domain, so that you
can create the relevant DNS entry for the service, and pick up the ACM
confirmation e-mail.


Configuration
-------------

Tweak the file ``group_vars/demo/vars`` to suit your environment. Also look at
``roles/web-assets/defaults/main.yml`` to discover other settings that can be
modified.


Deployment
----------

To deploy this in your own AWS account, configure some AWS credentials, then:

.. code-block:: bash

    $ ansible-playbook -i inv/demo -v site.yml

... this will also run the automated tests to prove that everything was built
correctly. The first run will wait for the domain administrator to confirm the
new ACM certificate for your domain. The tests will create a dummy web page in
S3 if one is missing.


Testing
-------

To run the tests independently of the deployment, try:

.. code-block:: bash

    $ AWS_ENVIRONMENT=demo rake spec:all

``ansible-lint -v site.yml`` and ``yamllint .`` should also give the code a
clean bill-of-health.


Further Reading
---------------

* https://medium.com/@tom.cook/edge-lambda-cloudfront-custom-headers-3d134a2c18a2
* https://scotthelme.co.uk/hardening-your-http-response-headers/
* https://observatory.mozilla.org/
* https://report-uri.io/home/pkp_analyse/


Licence
-------

This project is open source under an MIT licence.
