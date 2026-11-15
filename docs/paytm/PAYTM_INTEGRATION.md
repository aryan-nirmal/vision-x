# Paytm Integration Spec — Paytm Vyapaar AI

Source of truth: Paytm for Business Payment Gateway and Dynamic QR APIs.

## Status

- All Paytm calls go through one interface, `PaytmClient`, with two implementations: `MockPaytm` and `RealPaytm`. They take the same inputs and return the same outputs, and the setting `PAYTM_MODE=mock|staging|production` picks between them.

## Environment

```
PAYTM_MODE=mock            # mock | staging | production
PAYTM_MID=                 # staging MID from dashboard -> Developer Settings -> API Keys -> Test API Details
PAYTM_MERCHANT_KEY=        # never sent to the browser
PAYTM_WEBSITE=WEBSTAGING   # only needed by checkout APIs; unused by links/QR
PUBLIC_API_BASE=https://<app>.up.railway.app   # must be HTTPS on port 443 (Paytm webhooks only allow 443)
```

## Hosts (two different staging hosts — do not mix them up)

| API | Staging | Production |
| --- | --- | --- |
| Create link | `POST https://securestage.paytmpayments.com/link/create` | `https://secure.paytmpayments.com/link/create` |
| Fetch link transactions | `POST https://securestage.paytmpayments.com/link/fetchTransaction` | `https://secure.paytmpayments.com/link/fetchTransaction` |
| Create dynamic QR | `POST https://securegw-stage.paytmpayments.in/paymentservices/qr/create` | `https://securegw.paytmpayments.in/paymentservices/qr/create` |
| Transaction status (v3) | `POST https://securegw-stage.paytmpayments.in/v3/order/status` | `https://securegw.paytmpayments.in/v3/order/status` |

## Checksum (signature)

- Package: `pip install paytmchecksum` (1.7.0). Import: `from paytmchecksum import PaytmChecksum`.
- **Outgoing JSON APIs:** `signature = PaytmChecksum.generateSignature(body_str, MERCHANT_KEY)`, where `body_str` is the exact JSON string of `body`.
- **Incoming webhooks (form key-value):** pop `CHECKSUMHASH` from the params dict, then call `PaytmChecksum.verifySignature(params_dict, MERCHANT_KEY, checksum)`. Reject with 400 and log if it is false.

## Create link (one per invoice)

Request:

```json
{
  "body": {
    "mid": "<MID>",
    "linkType": "INVOICE",
    "linkName": "JoshiSupermarketINV0412",
    "linkDescription": "Invoice INV-0412",
    "amount": 8500.00,
    "invoiceId": "INV-0412",
    "expiryDate": "30/11/2026",
    "linkOrderId": "PTM_INV0412_<shortuuid>",
    "statusCallbackUrl": "https://<PUBLIC_API_BASE>/webhooks/paytm/link",
    "customerContact": {"customerName": "Sharma Traders", "customerEmail": "...", "customerMobile": "..."},
    "sendSms": false,
    "sendEmail": false,
    "linkNotes": "invoice_id=<uuid>"
  },
  "head": {"tokenType": "AES", "signature": "<sig>"}
}
```

Rules from the docs:
- `linkName`: no special characters; used to build the payment link URL.
- `linkDescription`: 3–30 characters.
- `amount`: at least ₹1.
- `INVOICE` links need `invoiceId` and `expiryDate` in `dd/mm/yyyy` or `dd/mm/yyyy hh:mm:ss`.
- `linkOrderId`: up to 50 alphanumeric characters, meant for reconciliation. Set it to our invoice's `paytm_order_id` (`PTM_INV...`) so the webhook's `ORDERID` matches the invoice exactly.

## Create dynamic QR (one per invoice, same order ID)

```json
{
  "body": {"mid": "<MID>", "orderId": "PTM_INV0412_<shortuuid>", "amount": "8500.00",
           "businessType": "UPI_QR_CODE", "posId": "PTM_WEB_01",
           "displayName": "Joshi Supermarket (Pune)", "invoiceDetails": "INV-0412",
           "expiryDate": "2026-11-30 23:59:59"},
  "head": {"clientId": "C11", "version": "v1", "signature": "<sig>"}
}
```

- `amount` is a **string** with 2 decimals. `expiryDate` is `yyyy-MM-dd HH:mm:ss`. `posId` is mandatory (up to 50 characters).
- `clientId` is only needed when a merchant has more than one key; drop it if the API complains.
- Response fields: `qrCodeId`, `qrData` (UPI string), `image` (base64 PNG), `resultInfo`.
- Upload the PNG to Supabase Storage and embed it in the email by public URL. Gmail strips base64 inline images.
- **Open risk:** can the link (`linkOrderId`) and the QR (`orderId`) share one order ID? If Paytm rejects the duplicate, give the QR the suffix `_Q` and store both IDs on the invoice. Reconcile on either.

## Webhooks

- **Link payments:** Paytm POSTs S2S key-value form data to the link's `statusCallbackUrl`, and only for completed transactions. Fields: `ORDERID, MID, TXNID, TXNAMOUNT, CURRENCY, PAYMENTMODE, TXNDATE, TXNDATETIME, STATUS (TXN_SUCCESS|TXN_FAILURE), RESPCODE, RESPMSG, GATEWAYNAME, BANKTXNID, BANKNAME, CHECKSUMHASH, LINKDESCRIPTION, PAYMENTEMAILID, PAYMENTMOBILENUMBER, PAYMENTFORM, CUSTID, MERC_UNQ_REF (= link ID), LINKNOTES`. **No payer VPA.** A dashboard-level "Link Payment Status" webhook needs Paytm to configure it; we rely on `statusCallbackUrl` per link instead.
- **QR and other payments:** a "Payment Status" webhook is configured in the merchant dashboard. It sends key-value form data with `ORDERID, MID, TXNID, TXNAMOUNT, PAYMENTMODE, CURRENCY, TXNDATE, STATUS, RESPCODE, RESPMSG, GATEWAYNAME, BANKTXNID, BANKNAME, CHECKSUMHASH`.
- Paytm may send the **same notification more than once**. Insert into `webhook_events` with a unique key `(provider, TXNID)` and process only on first insert.
- Handler order:
  1. Parse the form and keep the raw payload.
  2. Verify the checksum.
  3. Do the idempotent insert.
  4. If `STATUS == TXN_SUCCESS`, find the invoice by `ORDERID` (or `MERC_UNQ_REF` = link ID) and check that `TXNAMOUNT` equals the invoice amount.
  5. In one DB transaction: mark the invoice paid, insert the `transactions` row, and add `PAYMENTMOBILENUMBER`, `PAYMENTEMAILID` and `CUSTID` to `payer_identifiers`.
  6. Return 200 quickly.
- Webhooks only reach port 443, so they never hit localhost. For local tests, use the mock sender or a tunnel.

## Transaction status (fallback and reconciliation)

```json
{"body": {"mid": "<MID>", "orderId": "<order id>"}, "head": {"signature": "<sig>"}}
```

Use the response's `body.resultInfo.resultStatus` (`TXN_SUCCESS`, `TXN_FAILURE` or `PENDING`), plus `txnId`, `bankTxnId`, `txnAmount`, `paymentMode` and `txnDate`. There is no payer VPA here either. It is used by the "Check payment" button and by `/jobs/tick` for open invoices older than 2 minutes. Status-API results go through the same idempotent upsert as webhooks.

## Staging test instruments (from Paytm's testing page)

- UPI collect: VPA `7777777777@paytm`, approved in the Paytm Test UPI app (Android sample app on GitHub: Paytm_Payments_Android_Sample_Apps → UPI_Collect_Intent_Test_App).
- Wallet: mobile `7777777777`, password `Paytm12345`, OTP `489871`.
- Cards: any Visa or Mastercard, a future expiry, CVV `123`, then pick success or failure on Paytm's page.

## Mock mode contract (`MockPaytm`)

- `create_link` returns `{link_id: "MOCK_LI_<n>", short_url: "<PUBLIC_WEB_BASE>/mock-pay/<order_id>", order_id}`.
- `create_qr` returns `{qr_code_id, qr_data: "upi://pay?pa=mock@paytm&am=<amt>&tr=<order_id>", image: <base64 PNG generated locally>}`.
- `/mock-pay/<order_id>` is a page with "Pay (success)" and "Fail" buttons. It POSTs a form-encoded webhook, signed with `PaytmChecksum` and the mock key, carrying the exact field set above, to the real webhook route.
- `order_status` reads mock state.
- The same pytest suite runs against `MockPaytm`. Contract tests for `RealPaytm` are marked `@pytest.mark.staging` and run once keys exist.

## Doc links

- Create link: https://www.paytmpayments.com/docs/api/create-link-api
- Fetch link transactions: https://www.paytmpayments.com/docs/api/fetch-transaction-link-api
- Link payment webhook: https://www.paytmpayments.com/docs/link-payment-status-webhook
- Create QR: https://www.paytmpayments.com/docs/api/create-qr-code-api
- Transaction status v3: https://www.paytmpayments.com/docs/api/v3/transaction-status-api
- Payment status webhook: https://www.paytmpayments.com/docs/payment-status
- Callback and webhook setup: https://www.paytmpayments.com/docs/callback-and-webhook
- Checksum: https://www.paytmpayments.com/docs/checksum-implementation · https://github.com/paytm/Paytm_Python_Checksum
- Test instruments: https://www.paytmpayments.com/docs/testing-integration

The pages render with JavaScript, so plain fetchers only see navigation. To re-read a page, use Playwright or Claude in Chrome. Context7 (`/websites/developer_paytm`) only has thin coverage and is not enough for this integration.
