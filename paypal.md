# PayPal Processing

Currently planning to use django-payments (ver 0.13.0).
    - Might want to look at django-paypal (ver 1.0.0)
    - Official [Paypal Python REST SDK](https://github.com/paypal/Checkout-Python-SDK)
Paypal Payments Pro - costs monthly fee. Paypal Standard has no additional cost.
PayPal Standard with Encrypted Buttons - may be a thing to look into creating/implementing.
Paypal Standard: Payment Data Transfer (PDT) vs. Instant Payment Notification (IPN):
IPN - probably best. Handle message on a separate endpoint. User may return sooner than confirmation from Paypal.
PDT - probably not as good. Can miss transaction response. Transaction id (confirmation) in user return route.
PayPal Checkout - is this just standard or a different integration solution?
    Orders API
? Payments API ?
Vault API - securely store customer cards w/ PayPal. Stretch goal?

## PayPal Docs

These are some notes from reading the flow from PayPal documentation. I believe these are Version 2.0 docs, but maybe django-payments only implements version 1.0 API.

### Authentication & Authorization

Use PAYPAL_CLIENT_ID and PAYPAL_SECRET (Note: may need set the Accept header to application/x-www-form-urlencoded)
with following command:

curl -v https://api.sandbox.paypal.com/v1/oauth2/token \
   -H "Accept: application/json" \
   -H "Accept-Language: en_US" \
   -u "client_id:secret" \
   -d "grant_type=client_credentials"

PayPal will return `access_token` field within JSON response formatted as:

{
  "scope": "scope",
  "access_token": "Access-Token",
  "token_type": "Bearer",
  "app_id": "APP-80W284485P519543T",
  "expires_in": 31349,
  "nonce": "nonce"
}

Include this bearer token in the `Authorization` header with the `Bearer` authentication scheme in REST API calls,
such as:

curl -v -X GET https://api.sandbox.paypal.com/v1/invoicing/invoices?page=3&page_size=4&total_count_required=true \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <Access-Token>"

To detect when an access token expires, write code to either by 1) Keep track of the expires_in value in the token response or 2) Handle the HTTP 401 Unauthorized status code. The API endpoint issues this status code when it detects an expired token.

### Make Rest API Calls

Use PAYPAL_URL and the access token from above.

curl -v -X GET PAYPAL_URL/v1/payment-experience/web-profiles/XP-8YTH-NNP3-WSVN-3C76 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <Access-Token>"

With expected result format:
{
  "id": "XP-8YTH-NNP3-WSVN-3C76",
  "name": "exampleProfile",
  "temporary": false,
  "flow_config": {
    "landing_page_type": "billing",
    "bank_txn_pending_url": "https://example.com/flow_config/"
  },
  "input_fields": {
    "no_shipping": 1,
    "address_override": 1
  },
  "presentation": {
    "logo_image": "https://example.com/logo_image/"
  }
}

[Orders API](https://developer.paypal.com/docs/api/orders/v2/)
create, update, retrieve, authorize, and capture payments between parties >=2
POST /v2/checkout/orders

[Payments API](https://developer.paypal.com/docs/api/payments/v2/)
authorize, capture, refund, show payment information, used in conjunction with Orders API
Show details: GET /v2/payments/authorizations/{authorization_id}
Capture authorized payment: POST /v2/payments/authorizations/{authorization_id}/capture
Reauthorize (after 3-day honor period): POST /v2/payments/authorizations/{authorization_id}/reauthorize
Void authorized payment: POST /v2/payments/authorizations/{authorization_id}/void
Show captured details: GET /v2/payments/captures/{capture_id}
Refund captured payment: POST /v2/payments/captures/{capture_id}/refund
Show refund details: GET /v2/payments/refunds/{refund_id}

## Django Payments

On readthedocs.io, the stable docs seem out of date. The [django-payments latest docs](https://django-payments.readthedocs.io/en/latest/index.html) seem to be the best source. There is also the [GitHub repository issues](https://github.com/mirumee/django-payments/issues) for maintenance concerns.

### Authorize & Capture

PayPal does use the [Authorize & Capture](https://django-payments.readthedocs.io/en/latest/preauth.html) payment method.

After we get confirmation we are Authorized for a payment amount, we need to issue a capture request `payment.capture()` (if payment was the instance we just received authorization).


## Scratch Notes

 id                         | integer                  |           | not null |
 variant                    | character varying(255)   |           | not null |
 status                     | character varying(10)    |           | not null |
 fraud_status               | character varying(10)    |           | not null |
 fraud_message              | text                     |           | not null |
 created                    | timestamp with time zone |           | not null |
 modified                   | timestamp with time zone |           | not null |
 transaction_id             | character varying(255)   |           | not null |
 currency                   | character varying(10)    |           | not null |
 total                      | numeric(9,2)             |           | not null |
 delivery                   | numeric(9,2)             |           | not null |
 tax                        | numeric(9,2)             |           | not null |
 description                | text                     |           | not null |
 billing_first_name         | character varying(256)   |           | not null |
 billing_last_name          | character varying(256)   |           | not null |
 billing_address_1          | character varying(256)   |           | not null |
 billing_address_2          | character varying(256)   |           | not null |
 billing_city               | character varying(256)   |           | not null |
 billing_postcode           | character varying(256)   |           | not null |
 billing_country_code       | character varying(2)     |           | not null |
 billing_country_area       | character varying(256)   |           | not null |
 billing_email              | character varying(254)   |           | not null |
 customer_ip_address        | inet                     |           |          |
 extra_data                 | text                     |           | not null |
 message                    | text                     |           | not null |
 token                      | character varying(36)    |           | not null |
 captured_amount            | numeric(9,2)             |           | not null |
 credit_applied             | numeric(9,2)             |           | not null |
 full_price                 | numeric(9,2)             |           | not null |
 multiple_purchase_discount | numeric(9,2)             |           | not null |
 pre_pay_discount           | numeric(9,2)             |           | not null |
 paid_by_id                 | integer                  |           |          |
 student_id                 | integer                  |           |          |
