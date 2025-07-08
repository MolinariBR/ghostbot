LNURL-withdraw extension

List withdraw links
GET /withdraw/api/v1/links
Headers
{"X-Api-Key": <invoice_key>}
Body (application/json)
Returns 200 OK (application/json)
[<withdraw_link_object>, ...]
Curl example
curl -X GET https://lnvoltz.com/withdraw/api/v1/links -H "X-Api-Key: b2f68df91c8848f6a1db26f2e403321f"

Get a withdraw link
GET /withdraw/api/v1/links/<withdraw_id>
Headers
{"X-Api-Key": <invoice_key>}
Body (application/json)
Returns 201 CREATED (application/json)
{"lnurl": <string>}
Curl example
curl -X GET https://lnvoltz.com/withdraw/api/v1/links/<withdraw_id> -H "X-Api-Key: b2f68df91c8848f6a1db26f2e403321f"

Create a withdraw link
POST /withdraw/api/v1/links
Headers
{"X-Api-Key": <admin_key>}
Body (application/json)
{"title": <string>, "min_withdrawable": <integer>, "max_withdrawable": <integer>, "uses": <integer>, "wait_time": <integer>, "is_unique": <boolean>, "webhook_url": <string>}
Returns 201 CREATED (application/json)
{"lnurl": <string>}
Curl example
curl -X POST https://lnvoltz.com/withdraw/api/v1/links -d '{"title": <string>, "min_withdrawable": <integer>, "max_withdrawable": <integer>, "uses": <integer>, "wait_time": <integer>, "is_unique": <boolean>, "webhook_url": <string>}' -H "Content-type: application/json" -H "X-Api-Key: 8fce34f4b0f8446a990418bd167dc644"

Update a withdraw link
PUT /withdraw/api/v1/links/<withdraw_id>
Headers
{"X-Api-Key": <admin_key>}
Body (application/json)
{"title": <string>, "min_withdrawable": <integer>, "max_withdrawable": <integer>, "uses": <integer>, "wait_time": <integer>, "is_unique": <boolean>}
Returns 200 OK (application/json)
{"lnurl": <string>}
Curl example
curl -X PUT https://lnvoltz.com/withdraw/api/v1/links/<withdraw_id> -d '{"title": <string>, "min_withdrawable": <integer>, "max_withdrawable": <integer>, "uses": <integer>, "wait_time": <integer>, "is_unique": <boolean>}' -H "Content-type: application/json" -H "X-Api-Key: 8fce34f4b0f8446a990418bd167dc644"

Delete a withdraw link
DELETE /withdraw/api/v1/links/<withdraw_id>
Headers
{"X-Api-Key": <admin_key>}
Returns 204 NO CONTENT
Curl example
curl -X DELETE https://lnvoltz.com/withdraw/api/v1/links/<withdraw_id> -H "X-Api-Key: 8fce34f4b0f8446a990418bd167dc644"

Get hash check (for captchas to prevent milking)
GET /withdraw/api/v1/links/<the_hash>/<lnurl_id>
Headers
{"X-Api-Key": <invoice_key>}
Body (application/json)
Returns 201 CREATED (application/json)
{"status": <bool>}
Curl example
curl -X GET https://lnvoltz.com/withdraw/api/v1/links/<the_hash>/<lnurl_id> -H "X-Api-Key: b2f68df91c8848f6a1db26f2e403321f"

Get image to embed
GET /withdraw/img/<lnurl_id>
Curl example
curl -X GET https://lnvoltz.com/withdraw/img/<lnurl_id>"

