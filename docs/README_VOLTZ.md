# LNVOLTZ API Documentation

**Node URL:** https://lnvoltz.com  
**Wallet ID:** f3c366b7fb6f43fa9467c4dccedaf824  
**Admin key:** 8fce34f4b0f8446a990418bd167dc644  
**Invoice/read key:** b2f68df91c8848f6a1db26f2e403321f  

---

## Get wallet details

**Endpoint:**  
`GET /api/v1/wallet`

**Headers:**  
`{"X-Api-Key": "b2f68df91c8848f6a1db26f2e403321f"}`

**Returns:**  
`200 OK (application/json)`  
`{"id": <string>, "name": <string>, "balance": <int>}`

**Curl example:**  
`curl https://lnvoltz.com/api/v1/wallet -H "X-Api-Key: b2f68df91c8848f6a1db26f2e403321f"`

---

## Create an invoice (incoming)

**Endpoint:**  
`POST /api/v1/payments`

**Headers:**  
`{"X-Api-Key": "b2f68df91c8848f6a1db26f2e403321f"}`

**Body (application/json):**  
`{"out": false, "amount": <int>, "memo": <string>, "expiry": <int>, "unit": <string>, "webhook": <url:string>, "internal": <bool>}`

**Returns:**  
`201 CREATED (application/json)`  
`{"payment_hash": <string>, "payment_request": <string>}`

**Curl example:**  
`curl -X POST https://lnvoltz.com/api/v1/payments -d '{"out": false, "amount": <int>, "memo": <string>}' -H "X-Api-Key: b2f68df91c8848f6a1db26f2e403321f" -H "Content-type: application/json"`

---

## Pay an invoice (outgoing)

**Endpoint:**  
`POST /api/v1/payments`

**Headers:**  
`{"X-Api-Key": "8fce34f4b0f8446a990418bd167dc644"}`

**Body (application/json):**  
`{"out": true, "bolt11": <string>}`

**Returns:**  
`201 CREATED (application/json)`  
`{"payment_hash": <string>}`

**Curl example:**  
`curl -X POST https://lnvoltz.com/api/v1/payments -d '{"out": true, "bolt11": <string>}' -H "X-Api-Key: 8fce34f4b0f8446a990418bd167dc644" -H "Content-type: application/json"`

---

## Decode an invoice

**Endpoint:**  
`POST /api/v1/payments/decode`

**Body (application/json):**  
`{"data": <string>}`

**Returns:**  
`200 (application/json)`

**Curl example:**  
`curl -X POST https://lnvoltz.com/api/v1/payments/decode -d '{"data": <bolt11/lnurl, string>}' -H "Content-type: application/json"`

---

## Check an invoice (incoming or outgoing)

**Endpoint:**  
`GET /api/v1/payments/<payment_hash>`

**Headers:**  
`{"X-Api-Key": "b2f68df91c8848f6a1db26f2e403321f"}`

**Returns:**  
`200 OK (application/json)`  
`{"paid": <bool>}`

**Curl example:**  
`curl -X GET https://lnvoltz.com/api/v1/payments/<payment_hash> -H "X-Api-Key: b2f68df91c8848f6a1db26f2e403321f" -H "Content-type: application/json"`

