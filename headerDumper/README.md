# Header Dumper
## This web server returns HTTP request headers in reply

# Usage example

## From server side

```bash
$ python3 headerDumper/headerDumper.py 
127.0.0.1 - - [09/Mar/2023 17:14:37] "GET /headers HTTP/1.1" 202 -
```

## From client side

```bash
$ curl -sv http://localhost:8080/headers | jq
*   Trying 127.0.0.1:8080...
* Connected to localhost (127.0.0.1) port 8080 (#0)
> GET /headers HTTP/1.1
> Host: localhost:8080
> User-Agent: curl/7.79.1
> Accept: */*
> 
* Mark bundle as not supporting multiuse
* HTTP 1.0, assume close after body
< HTTP/1.0 202 Accepted
< Server: BaseHTTP/0.6 Python/3.10.9
< Date: Thu, 09 Mar 2023 14:17:05 GMT
< content-type: application/json
< 
{ [99 bytes data]
* Closing connection 0
{
  "request_headers": [
    {
      "Host": "localhost:8080"
    },
    {
      "User-Agent": "curl/7.79.1"
    },
    {
      "Accept": "*/*"
    }
  ]
}
```