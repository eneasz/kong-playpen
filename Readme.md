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
  
* Cassandra: DB for Kong config data

* Kong-UI: An optional GUI for configuring Kong - [http://localhost:8090/](http://localhost:8090)
  * When the UI asks you for your Kong server enter: ```http://kong:8001```

* Foo1 and Foo2: A basic REST app - [http://localhost:8091](http://localhost:8091) | [http://localhost:8092](http://localhost:8092)

Note: You'll need to wait about a minute for startup to complete.

## Use Kong

### Adding an API

Reference: [https://docs.konghq.com/0.14.x/getting-started/configuring-a-service/](https://docs.konghq.com/0.14.x/getting-started/configuring-a-service/)

#####  Add your Service using the Admin API

Call the Kong API:

```
curl -i -X POST \
  --url http://localhost:8001/services/ \
  --data 'name=world1' \
  --data 'url=http://world1:8091/'
```


#####  Add your 2nd Service using the Admin API

```
curl -i -X POST \
  --url http://localhost:8001/services/ \
  --data 'name=world2' \
  --data 'url=http://world2:8092/'
```

#####  UPDATE 1st Service using the Admin API

```
curl -i -X PUT \
  --url http://localhost:8001/services/world1 \
  --data 'name=world1' \
  --data 'url=http://world1:8091/'
```

#####  Add a Route for the Service

```
curl -i -X POST \
  --url http://localhost:8001/services/world1/routes \
  --data 'hosts[]=world1.com'
```

#####  Add 2nd Route for the Service

```
curl -i -X POST \
  --url http://localhost:8001/services/world2/routes \
  --data 'hosts[]=world2.com'
```


#### Call the world1 service through Kong (Using Hosts)

```
curl -i -X GET \
  --url http://localhost:8000/ \
  --header 'Host: world1.com'
```

##### Call the world2 service through Kong (Using Hosts)

```
curl -i -X GET \
  --url http://localhost:8000/ \
  --header 'Host: world2.com'
```



### Authentication

Reference: [https://getkong.org/plugins/key-authentication/](https://getkong.org/plugins/key-authentication/)

#### Enable Key Auth for the Foo API

```
curl -i -X POST \
  --url http://localhost:8001/services/world1/plugins/ \
  --data 'name=key-auth' \
  --data "config.hide_credentials=true"
```

##### Try to call the API now...

```
curl -i -X GET \
  --url http://localhost:8000/ \
  --header 'Host: world1.com'
```

You will be unauthorized.

##### To get authorized create a user:

```
curl -i -X POST \
  --url http://localhost:8001/consumers/ \
  --data "username=Damian"
```

##### Make note of the id returned for use in the next command.

```
curl -i -X POST \
  --url http://localhost:8001/consumers/Damian/key-auth/ \
  --data ''
```

Use the Key:

```
curl -i -X GET \
  --url http://localhost:8000 \
  --header "Host: world1.com" \
  --header "apikey: {key from last step}"
 ```


## Blue Green Deployments

##### Create an upstream

```
curl -X POST http://localhost:8001/upstreams \
    --data "name=blue.v1.prod"
```

##### Add two targets to the upstream

```
curl -X POST http://localhost:8001/upstreams/blue.v1.prod/targets \
    --data "target=world1:8091" \
    --data "weight=100"
```

```
curl -X POST http://localhost:8001/upstreams/blue.v1.prod/targets \
    --data "target=example.com:80" \
    --data "weight=50"
```


##### Create a LIVE Service targeting the Blue upstream

```
curl -X POST http://localhost:8001/services \
     --data 'name=live' \
     --data "host=blue.v1.prod" \
     --data "path=/"
```

##### Finally, add a Route as an entry-point into the Service

```
curl -X POST http://localhost:8001/services/live/routes/ \
    --data "hosts[]=live.world.com"
```

##### Test loadbalancing

```
curl -i -X GET \
  --url http://localhost:8000/ \
  --header 'Host: live.world.com'
```


### Create a new Green upstream for address service v2

##### Create an upstream

```
curl -X POST http://localhost:8001/upstreams \
    --data "name=green.v2.prod"
```

##### Add targets to the upstream

```
curl -X POST http://localhost:8001/upstreams/green.v2.prod/targets \
    --data "target=world2:8092" \
    --data "weight=100"
```


##### Switch the API from Blue to Green upstream, v1 -> v2

```
curl -X PATCH http://localhost:8001/services/live \
    --data "host=green.v2.prod"
```

##### Confirm trafic is now going to green V2

```
curl -i -X GET \
  --url http://localhost:8000/ \
  --header 'Host: live.world.com'
```

Back to TOC

Permalink

### Logging

TODO 

### Metrics

TODO
