.. |pypi-badge| image:: https://badge.fury.io/py/gocardless_pro.svg
    :target: https://pypi.python.org/pypi/gocardless_pro

GoCardless Pro Python client library
============================================

A Python client for interacting with the GoCardless Pro API.

|pypi-badge|

Tested against Python 3.8, 3.9, 3.10, 3.11 and 3.12.

- `"Getting Started" guide <https://developer.gocardless.com/getting-started/api/introduction/?lang=python>`_ with copy and paste Python code samples
- `API reference`_

------------

Install from PyPI:

.. code:: bash

    $ pip install gocardless_pro


Usage
-----

Create a ``Client`` instance, providing your access token and the environment
you want to use:

.. code:: python

    import gocardless_pro
    token = os.environ['ACCESS_TOKEN']
    client = gocardless_pro.Client(access_token=token, environment='live')

Access API endpoints using the corresponding methods on the client object:

.. code:: python

    # Create a new customer. We automatically add idempotency keys to requests to create
    # resources, stopping duplicates accidentally getting created if something goes wrong
    # with the API (e.g. networking problems) - see https://developer.gocardless.com/api
    # -reference/#making-requests-idempotency-keys for details
    customer = client.customers.create(params={'email': 'jane@example.com'})

    # Fetch a payment by its ID
    payment = client.payments.get("PA123")

    # Loop through a page of payments, printing each payment's amount
    for payment in client.payments.list().records:
        decimal_amount = decimal.Decimal(payment.amount) / 100
        print('Payment for £{0}'.format(decimal_amount))

    # Create a mandate PDF in a specific language
    client.mandate_pdfs.create(
        params={'links': {'mandate': 'MD00001234XYZ'}},
        headers={'Accept-Language': 'fr'}
    )

Rate limit response headers can be read:

.. code:: python

    # Note these properties will be None until you make an API request with the client
    client.rate_limit.limit
    client.rate_limit.remaining
    client.rate_limit.reset


For full documentation, see our `API reference`_.

.. _API reference: https://developer.gocardless.com/api-reference


Available resources
```````````````````

Balances
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # List balances
    client.balances.list(params={...})

    # Iterate through all balances
    client.balances.all(params={...})

Bank account details
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Get encrypted bank details
    client.bank_account_details.get('BA123', params={...})

Bank authorisations
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a Bank Authorisation
    client.bank_authorisations.create(params={...})

    # Get a Bank Authorisation
    client.bank_authorisations.get('BAU123', params={...})

Bank details lookups
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Perform a bank details lookup
    client.bank_details_lookups.create(params={...})

Billing requests
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a Billing Request
    client.billing_requests.create(params={...})

    # Collect customer details
    client.billing_requests.collect_customer_details('BRQ123', params={...})

    # Collect bank account details
    client.billing_requests.collect_bank_account('BRQ123', params={...})

    # Confirm the payer details
    client.billing_requests.confirm_payer_details('BRQ123', params={...})

    # Fulfil a Billing Request
    client.billing_requests.fulfil('BRQ123', params={...})

    # Cancel a Billing Request
    client.billing_requests.cancel('BRQ123', params={...})

    # List Billing Requests
    client.billing_requests.list(params={...})

    # Iterate through all billing_requests
    client.billing_requests.all(params={...})

    # Get a single Billing Request
    client.billing_requests.get('BRQ123', params={...})

    # Notify the customer
    client.billing_requests.notify('BRQ123', params={...})

    # Trigger fallback
    client.billing_requests.fallback('BRQ123', params={...})

    # Change currency
    client.billing_requests.choose_currency('BRQ123', params={...})

    # Select institution for a Billing Request
    client.billing_requests.select_institution('BRQ123', params={...})

Billing request flows
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a Billing Request Flow
    client.billing_request_flows.create(params={...})

    # Initialise a Billing Request Flow
    client.billing_request_flows.initialise('BRF123', params={...})

Billing request templates
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # List Billing Request Templates
    client.billing_request_templates.list(params={...})

    # Iterate through all billing_request_templates
    client.billing_request_templates.all(params={...})

    # Get a single Billing Request Template
    client.billing_request_templates.get('BRT123', params={...})

    # Create a Billing Request Template
    client.billing_request_templates.create(params={...})

    # Update a Billing Request Template
    client.billing_request_templates.update('BRQ123', params={...})

Billing request with actions
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a Billing Request with Actions
    client.billing_request_with_actions.create_with_actions(params={...})

Blocks
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a block
    client.blocks.create(params={...})

    # Get a single block
    client.blocks.get('BLC123', params={...})

    # List multiple blocks
    client.blocks.list(params={...})

    # Iterate through all blocks
    client.blocks.all(params={...})

    # Disable a block
    client.blocks.disable('BLC123', params={...})

    # Enable a block
    client.blocks.enable('BLC123', params={...})

    # Create blocks by reference
    client.blocks.block_by_ref(params={...})

Creditors
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a creditor
    client.creditors.create(params={...})

    # List creditors
    client.creditors.list(params={...})

    # Iterate through all creditors
    client.creditors.all(params={...})

    # Get a single creditor
    client.creditors.get('CR123', params={...})

    # Update a creditor
    client.creditors.update('CR123', params={...})

Creditor bank accounts
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a creditor bank account
    client.creditor_bank_accounts.create(params={...})

    # List creditor bank accounts
    client.creditor_bank_accounts.list(params={...})

    # Iterate through all creditor_bank_accounts
    client.creditor_bank_accounts.all(params={...})

    # Get a single creditor bank account
    client.creditor_bank_accounts.get('BA123', params={...})

    # Disable a creditor bank account
    client.creditor_bank_accounts.disable('BA123', params={...})

Currency exchange rates
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # List exchange rates
    client.currency_exchange_rates.list(params={...})

    # Iterate through all currency_exchange_rates
    client.currency_exchange_rates.all(params={...})

Customers
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a customer
    client.customers.create(params={...})

    # List customers
    client.customers.list(params={...})

    # Iterate through all customers
    client.customers.all(params={...})

    # Get a single customer
    client.customers.get('CU123', params={...})

    # Update a customer
    client.customers.update('CU123', params={...})

    # Remove a customer
    client.customers.remove('CU123', params={...})

Customer bank accounts
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a customer bank account
    client.customer_bank_accounts.create(params={...})

    # List customer bank accounts
    client.customer_bank_accounts.list(params={...})

    # Iterate through all customer_bank_accounts
    client.customer_bank_accounts.all(params={...})

    # Get a single customer bank account
    client.customer_bank_accounts.get('BA123', params={...})

    # Update a customer bank account
    client.customer_bank_accounts.update('BA123', params={...})

    # Disable a customer bank account
    client.customer_bank_accounts.disable('BA123', params={...})

Customer notifications
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Handle a notification
    client.customer_notifications.handle('PCN123', params={...})

Events
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # List events
    client.events.list(params={...})

    # Iterate through all events
    client.events.all(params={...})

    # Get a single event
    client.events.get('EV123', params={...})

Exports
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Get a single export
    client.exports.get('EX123', params={...})

    # List exports
    client.exports.list(params={...})

    # Iterate through all exports
    client.exports.all(params={...})

Instalment schedules
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create (with dates)
    client.instalment_schedules.create_with_dates(params={...})

    # Create (with schedule)
    client.instalment_schedules.create_with_schedule(params={...})

    # List instalment schedules
    client.instalment_schedules.list(params={...})

    # Iterate through all instalment_schedules
    client.instalment_schedules.all(params={...})

    # Get a single instalment schedule
    client.instalment_schedules.get('IS123', params={...})

    # Update an instalment schedule
    client.instalment_schedules.update('IS123', params={...})

    # Cancel an instalment schedule
    client.instalment_schedules.cancel('IS123', params={...})

Institutions
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # List Institutions
    client.institutions.list(params={...})

    # Iterate through all institutions
    client.institutions.all(params={...})

    # List institutions for Billing Request
    client.institutions.list_for_billing_request('BRQ123', params={...})

Logos
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a logo associated with a creditor
    client.logos.create_for_creditor(params={...})

Mandates
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a mandate
    client.mandates.create(params={...})

    # List mandates
    client.mandates.list(params={...})

    # Iterate through all mandates
    client.mandates.all(params={...})

    # Get a single mandate
    client.mandates.get('MD123', params={...})

    # Update a mandate
    client.mandates.update('MD123', params={...})

    # Cancel a mandate
    client.mandates.cancel('MD123', params={...})

    # Reinstate a mandate
    client.mandates.reinstate('MD123', params={...})

Mandate imports
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a new mandate import
    client.mandate_imports.create(params={...})

    # Get a mandate import
    client.mandate_imports.get('IM000010790WX1', params={...})

    # Submit a mandate import
    client.mandate_imports.submit('IM000010790WX1', params={...})

    # Cancel a mandate import
    client.mandate_imports.cancel('IM000010790WX1', params={...})

Mandate import entries
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Add a mandate import entry
    client.mandate_import_entries.create(params={...})

    # List all mandate import entries
    client.mandate_import_entries.list(params={...})

    # Iterate through all mandate_import_entries
    client.mandate_import_entries.all(params={...})

Mandate pdfs
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a mandate PDF
    client.mandate_pdfs.create(params={...})

Negative balance limits
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # List negative balance limits
    client.negative_balance_limits.list(params={...})

    # Iterate through all negative_balance_limits
    client.negative_balance_limits.all(params={...})

Outbound payments
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create an outbound payment
    client.outbound_payments.create(params={...})

    # Create a withdrawal outbound payment
    client.outbound_payments.withdraw(params={...})

    # Cancel an outbound payment
    client.outbound_payments.cancel('OUT01JR7P5PKW3K7Q34CJAWC03E82', params={...})

    # Approve an outbound payment
    client.outbound_payments.approve('OUT01JR7P5PKW3K7Q34CJAWC03E82', params={...})

    # Get an outbound payment
    client.outbound_payments.get('OUT01JR7P5PKW3K7Q34CJAWC03E82', params={...})

    # List outbound payments
    client.outbound_payments.list(params={...})

    # Iterate through all outbound_payments
    client.outbound_payments.all(params={...})

    # Update an outbound payment
    client.outbound_payments.update('OUT01JR7P5PKW3K7Q34CJAWC03E82', params={...})

Payer authorisations
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Get a single Payer Authorisation
    client.payer_authorisations.get('PA123', params={...})

    # Create a Payer Authorisation
    client.payer_authorisations.create(params={...})

    # Update a Payer Authorisation
    client.payer_authorisations.update('PA123', params={...})

    # Submit a Payer Authorisation
    client.payer_authorisations.submit('PA123', params={...})

    # Confirm a Payer Authorisation
    client.payer_authorisations.confirm('PA123', params={...})

Payer themes
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a payer theme associated with a creditor
    client.payer_themes.create_for_creditor(params={...})

Payments
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a payment
    client.payments.create(params={...})

    # List payments
    client.payments.list(params={...})

    # Iterate through all payments
    client.payments.all(params={...})

    # Get a single payment
    client.payments.get('PM123', params={...})

    # Update a payment
    client.payments.update('PM123', params={...})

    # Cancel a payment
    client.payments.cancel('PM123', params={...})

    # Retry a payment
    client.payments.retry('PM123', params={...})

Payouts
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # List payouts
    client.payouts.list(params={...})

    # Iterate through all payouts
    client.payouts.all(params={...})

    # Get a single payout
    client.payouts.get('PO123', params={...})

    # Update a payout
    client.payouts.update('PO123', params={...})

Payout items
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Get all payout items in a single payout
    client.payout_items.list(params={...})

    # Iterate through all payout_items
    client.payout_items.all(params={...})

Redirect flows
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a redirect flow
    client.redirect_flows.create(params={...})

    # Get a single redirect flow
    client.redirect_flows.get('RE123456', params={...})

    # Complete a redirect flow
    client.redirect_flows.complete('RE123456', params={...})

Refunds
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a refund
    client.refunds.create(params={...})

    # List refunds
    client.refunds.list(params={...})

    # Iterate through all refunds
    client.refunds.all(params={...})

    # Get a single refund
    client.refunds.get('RF123', params={...})

    # Update a refund
    client.refunds.update('RF123', params={...})

Scenario simulators
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Simulate a scenario
    client.scenario_simulators.run('payment_failed', params={...})

Schemeentifiers
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a scheme identifier
    client.scheme_identifiers.create(params={...})

    # List scheme identifiers
    client.scheme_identifiers.list(params={...})

    # Iterate through all scheme_identifiers
    client.scheme_identifiers.all(params={...})

    # Get a single scheme identifier
    client.scheme_identifiers.get('SU123', params={...})

Subscriptions
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a subscription
    client.subscriptions.create(params={...})

    # List subscriptions
    client.subscriptions.list(params={...})

    # Iterate through all subscriptions
    client.subscriptions.all(params={...})

    # Get a single subscription
    client.subscriptions.get('SB123', params={...})

    # Update a subscription
    client.subscriptions.update('SB123', params={...})

    # Pause a subscription
    client.subscriptions.pause('SB123', params={...})

    # Resume a subscription
    client.subscriptions.resume('SB123', params={...})

    # Cancel a subscription
    client.subscriptions.cancel('SB123', params={...})

Tax rates
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # List tax rates
    client.tax_rates.list(params={...})

    # Iterate through all tax_rates
    client.tax_rates.all(params={...})

    # Get a single tax rate
    client.tax_rates.get('GB_VAT_1', params={...})

Transferred mandates
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Get updated customer bank details
    client.transferred_mandates.transferred_mandates('MD123', params={...})

Verification details
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # Create a verification detail
    client.verification_details.create(params={...})

    # List verification details
    client.verification_details.list(params={...})

    # Iterate through all verification_details
    client.verification_details.all(params={...})

Webhooks
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    # List webhooks
    client.webhooks.list(params={...})

    # Iterate through all webhooks
    client.webhooks.all(params={...})

    # Get a single webhook
    client.webhooks.get('WB123', params={...})

    # Retry a webhook
    client.webhooks.retry('WB123', params={...})



Running tests
-------------

First, install the development dependencies:

.. code:: bash

    $ pip install -r requirements-dev.txt

To run the test suite against the current Python version, run ``pytest``.

To run the test suite against multiple Python versions, run ``tox``.

If you don't have all versions of Python installed, you can run the tests in
a Docker container by running ``make``.
