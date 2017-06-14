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


Why Is This Like It Is?!
------------------------

Infrastructure automation tools should be declarative and idempotent, and
CloudFormation is great at that. However it falls short of total API coverage
and there's always that *one little thing* that you need to do outside it.

Ansible is a fantastic tool for provisioning things and has a robust set of
best practices for structuring playbooks and inventory; plus some handy tools
for secrets management and the like.

Awspec is the only AWS testing library out there, and rspec is lovely.

Here we've put the three of these tools together. So

* groups in ``group_vars/`` become environments (e.g. development; production),
  although here there is simply ``demo``. The inventory system enables us to
  set different configuration for each environment and encrypt secrets using
  vault. You could also bind groups to different git branches with a task or
  two, to create a proper release management process.

* roles are composed into groups to build up an environment. Again, this demo
  only has a single role, but it's not difficult to imagine adding more for
  enabling CloudTrail, adding an API layer, ...

* ``host_vars`` are just used as *glue*, since Ansible only has one host it
  can provision - i.e. ``localhost``.

* awspec tests all belong with the role that they are testing, so that roles
  can be extracted into their own repositories and shared between projects.
  Tests are run during the provisioning process rather than independently
  (because otherwise we'd forget to and they'd rot).

* all the comments are marked up using RST, with a view to using ``yaml2rst``
  to dynamically generate detailed documentation in the future. This works
  better than you might think :P


Further Reading
---------------

* https://medium.com/@tom.cook/edge-lambda-cloudfront-custom-headers-3d134a2c18a2
* https://scotthelme.co.uk/hardening-your-http-response-headers/
* https://observatory.mozilla.org/
* https://report-uri.io/home/pkp_analyse/
* http://docs.ansible.com/ansible/playbooks_best_practices.html
* https://github.com/k1LoW/awspec


Licence
-------

This project is open source under an MIT licence.
