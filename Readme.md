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
curl -X POST \
   http://localhost:8001/upstreams \
   -H 'Content-Type: application/x-www-form-urlencoded' \
   -H 'cache-control: no-cache' \
   -d 'name=blue.v1.prod' \
   -d 'healthchecks.active.https_verify_certificate=false' \
   -d 'healthchecks.active.unhealthy.tcp_failures=2' \
   -d 'healthchecks.active.unhealthy.timeouts=2' \
   -d 'healthchecks.active.unhealthy.http_failures=1' \
   -d 'healthchecks.active.unhealthy.interval=3' \
   -d 'healthchecks.active.timeout=3' \
   -d 'healthchecks.active.healthy.interval=10' \
   -d 'healthchecks.active.healthy.successes=3' \
   -d 'healthchecks.active.type=http' \
   -d 'healthchecks.active.http_path=%2F' \
   -d 'healthchecks.active.healthy.http_statuses=200' |jq .
```

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
   hosts:='["live.lbg.com"]'
```

##### Test loadbalancing

```
while true; do http  http://live.lbg.com:8000/ ; sleep 2; clear; done
```


### Create a new Green upstream for address service v2

##### Create an upstream

```
curl -X POST \
   http://localhost:8001/upstreams \
   -H 'Content-Type: application/x-www-form-urlencoded' \
   -H 'cache-control: no-cache' \
   -d 'name=green.v2.prod' \
   -d 'healthchecks.active.https_verify_certificate=false' \
   -d 'healthchecks.active.unhealthy.tcp_failures=2' \
   -d 'healthchecks.active.unhealthy.timeouts=2' \
   -d 'healthchecks.active.unhealthy.http_failures=1' \
   -d 'healthchecks.active.unhealthy.interval=3' \
   -d 'healthchecks.active.timeout=3' \
   -d 'healthchecks.active.healthy.interval=10' \
   -d 'healthchecks.active.healthy.successes=3' \
   -d 'healthchecks.active.type=http' \
   -d 'healthchecks.active.http_path=%2F' \
   -d 'healthchecks.active.healthy.http_statuses=200' |jq .
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

##### Confirm trafic is now going to green V2

```
http  http://live.lbg.com:8000/
```

Back to TOC

Permalink

### Logging

TODO 

### Metrics

TODO
