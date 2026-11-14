




curl -sS -X POST 'http://127.0.0.1:8000/extract' \
  -H 'Content-Type: application/json' \
  -d '{"text":"Invoice INV-1 from Acme for 100.00 USD"}'


Server log (uvicorn terminal) should show something like extract_ok with request_id and retries: 0.


Request 422 (missing body field):

curl -sS -o /tmp/out.json -w '%{http_code}\n' -X POST 'http://127.0.0.1:8000/extract' \
  -H 'Content-Type: application/json' \
  -d '{}'
cat /tmp/out.json