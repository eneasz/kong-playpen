![Screenshot](img/kong_logo.png)
# Kong-Playpen


Playing with Kong API Gateway [https://getkong.org/](https://getkong.org/)

## Setup

Reference: [https://getkong.org/install/docker/](https://getkong.org/install/docker/)

Start a Kong stack...

```
docker-compose up
```
This starts...

* Kong
  * Kong Admin API - [http://localhost:8001/status](http://localhost:8001/status)
  * Kong API Proxy - [http://localhost:8000/](http://localhost:8000)
  
* Postgress: DB for Kong config data

* Kong-UI: An optional GUI for configuring Kong - [http://localhost:8090/](http://localhost:8090)
  * When the UI asks you for your Kong server enter: ```http://kong:8001```

* Foo1 and Foo2: A basic REST app - [http://localhost:8091](http://localhost:8091) | [http://localhost:8092](http://localhost:8092)

Note: You'll need to wait about a minute for startup to complete.

## Use Kong

### Adding an API

Reference: [https://docs.konghq.com/0.15.x/getting-started/configuring-a-service/](https://docs.konghq.com/0.15.x/getting-started/configuring-a-service/)

#####  Add blue service using the Admin API

Call the Kong API:

```
http POST http://localhost:8001/services/ \
   name="blue" \
   url="http://foo1:8091/"
```


#####  Add green service using the Admin API

```
http POST http://localhost:8001/services/ \
   name="green" \
   url="http://foo2:8092/"
```

#####  UPDATE blue Service using the Admin API

```
http PUT http://localhost:8001/services/blue \
   name="blue" \
   url="http://foo1:8091/"
```

#####  Add a Route for the Service

```
http POST http://localhost:8001/services/blue/routes  \
   hosts:='["deployment1.com"]'
```

#####  Add 2nd Route for the Service

```
http POST http://localhost:8001/services/green/routes  \
   hosts:='["deployment2.com"]'
```


#### Call the world1 service through Kong (Using Hosts)

```
http http://localhost:8000/ \
   Host:deployment1.com
```

##### Call the world2 service through Kong (Using Hosts)

```
http http://localhost:8000/ \
   Host:deployment2.com
```



### Authentication

Reference: [https://getkong.org/plugins/key-authentication/](https://getkong.org/plugins/key-authentication/)

#### Enable Key Auth for the Foo API

```
http http://localhost:8001/services/blue/plugins/ \
   name='key-auth' \
   config.hide_credentials:true
```

##### Try to call the deployment1 via gateway now...

```
http http://localhost:8000/ \
   Host:deployment1.com
```

You will be unauthorized.

##### To get authorized create a user:

```
http http://localhost:8001/consumers/ \
   username='Damian'
```

##### Make note of the id returned for use in the next command.

Bellow I've hardcoded key however if key value isn't provided gateway will generate and return key
```
http http://localhost:8001/consumers/Damian/key-auth/ \
   key='VerySecretKeyExample'
```

Use the key to call apigw:

```
http http://localhost:8000/ \
   Host:deployment1.com \
   apikey:'VerySecretKeyExample'
 ```


## Blue Green Deployments

##### Create an upstream

```
http  --form http://localhost:8001/upstreams \
   name='blue.v1.prod' \
   healthchecks.active.https_verify_certificate:false \
   healthchecks.active.unhealthy.tcp_failures:=2 \
   healthchecks.active.unhealthy.timeouts:=2 \
   healthchecks.active.unhealthy.http_failures:=1 \
   healthchecks.active.unhealthy.interval:=5 \
   healthchecks.active.timeout:=3 \
   healthchecks.active.healthy.interval:=10 \
   healthchecks.active.healthy.successes:=3 \
   healthchecks.active.type='http'
```

Fallowing settings works as bellow:
- healthchecks.active.unhealthy.tcp_failures 
    Number of TCP failures in active probes to consider a target unhealthy.

- healthchecks.active.unhealthy.timeouts
    Number of timeouts in active probes to consider a target unhealthy.

- healthchecks.active.unhealthy.http_failures
   Number of HTTP failures in active probes (as defined by healthchecks.active.unhealthy.http_statuses) to consider a target unhealthy.

- healthchecks.active.unhealthy.interval
   Interval between active health checks for unhealthy targets (in seconds). A value of zero indicates that active probes for unhealthy targets should not be performed.

- healthchecks.active.timeout
   Socket timeout for active health checks (in seconds).

- healthchecks.active.healthy.interval
   Interval between active health checks for healthy targets (in seconds). A value of zero indicates that active probes for healthy targets should not be performed.

- healthchecks.active.healthy.successes
   Number of successes in active probes (as defined by healthchecks.active.healthy.http_statuses) to consider a target healthy.

- healthchecks.active.type
   Specify whether to perform HTTP or HTTPS probes (setting it to "http" or "https"), or by simply testing if the connection to a given host and port is successful (setting it to "tcp")

- healthchecks.active.http_path
   The path that should be used when issuing the HTTP GET request to the target. The default value is "/"

- healthchecks.active.healthy.http_statuses
   To consider a target healthy. Default 200 and 302


##### Add two targets to the upstream

```
http http://localhost:8001/upstreams/blue.v1.prod/targets \
   target='foo1:8091' \
   weight:=100
```

```
http http://localhost:8001/upstreams/blue.v1.prod/targets \
   target='example.com:80' \
   weight:=50
```


##### Create a LIVE Service targeting the Blue upstream

```
http http://localhost:8001/services \
   name="live" \
   host="blue.v1.prod" \
   path="/"
```

##### Finally, add a Route as an entry-point into the Service

```
http POST http://localhost:8001/services/live/routes/ \
   hosts:='["live.company.com"]'
```

##### Test loadbalancing

```
while true; do http  http://live.company.com:8000/ ; sleep 2; clear; done
```


### Create a new Green upstream for address service v2

##### Create an upstream

```
http  --form http://localhost:8001/upstreams \
   name='green.v2.prod' \
   healthchecks.active.https_verify_certificate:false \
   healthchecks.active.unhealthy.tcp_failures:=2 \
   healthchecks.active.unhealthy.timeouts:=2 \
   healthchecks.active.unhealthy.http_failures:=1 \
   healthchecks.active.unhealthy.interval:=5 \
   healthchecks.active.timeout:=3 \
   healthchecks.active.healthy.interval:=10 \
   healthchecks.active.healthy.successes:=3 \
   healthchecks.active.type='http'
```

##### Add targets to the upstream

```
http http://localhost:8001/upstreams/green.v2.prod/targets \
   target='foo2:8092' \
   weight:=100
```


##### Switch the API from Blue to Green upstream, v1 -> v2

```
http PATCH http://localhost:8001/services/live \
   host="green.v2.prod"
```

To make it switch every 15s
```
while true; do http PATCH http://localhost:8001/services/live host="blue.v1.prod"; sleep 15; http PATCH http://localhost:8001/services/live host="green.v2.prod"; sleep 15; done
```

##### Confirm trafic is now going to green V2

```
http  http://live.company.com:8000/
```

Back to TOC

Permalink

### EndPoints

http://live.company.com:8000/ - Live

| URL                              | Description      |
| :-------------------------------:|:----------------:|
| http://live.company.com:8000/        | Live traffic url |
| http://deployment1.com:8000/     | Access to deployment1 service via APIGW |
| http://deployment2.com:8000/     | Access to deployment2 service via APIGW |
| http://deployment1.com:8091/     | Access to deployment1 directly |
| http://deployment2.com:8092/     | Access to deployment2 directly |
| http://localhost:8001/           | Display gateway settings |
| http://localhost:8090            | WebUI interface|

### Clean up

```
docker-compose down
docker volume rm kong-playpen_kong_data
```

TODO 

### Metrics

TODO
