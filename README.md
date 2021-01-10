# short-url Application

Simple app to create short URLs.
The App is written in python and uses MongoDb as data store.



## Local Testing Setup using Docker Compose

1. Clone the Repository. 
2. Install all the python packages. 
   
   `pip3 install -r requirements.txt`

   
3. Run docker build to build the image
   
   `docker build  -t url-short:latest .`

4. Use docker compose to start the app and the data store

    `docker-compose up -d`

## Local development Setup with flask run

 By default the docker compose uses waitress to run the app. This is not suitable for development and testing of apis. To enable hot reload follow these steps

1. Change `serve(app, host='0.0.0.0', port=8000)` to  `app.run(debug=True)` in shorturl.py
   
   
2. Pull the mongo image 
   
   `docker run -d -p 27017:27017 --name mongo-short-url mongo:4.2-bionic`
   
3. Export the MongoDb URL 

    `export MONGO_URL="mongodb://localhost:27017/"`

4. Run the app

   `python3 shorturl.py`



## Testing
After the local setup is done. We can use the following apis to test
```
$ curl -i  localhost:8000/shorten -H "content-type: application/json" --data '{"url":"https://google.com"}'

HTTP/1.1 200 OK
Content-Length: 19
Content-Type: text/html; charset=utf-8
Date: Sun, 10 Jan 2021 11:58:20 GMT
Server: waitress

Shortened: r/99999

```

Now that we have got the shortened url we test redirection by using the following curl 

```
$ curl -i localhost:8000/r/99999

HTTP/1.1 302 FOUND
Content-Length: 243
Content-Type: text/html; charset=utf-8
Date: Sun, 10 Jan 2021 11:59:29 GMT
Location: https://google.com
Server: waitress

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to target URL: <a href="https://google.com">https://google.com</a>.  If not click the link.%
```
We can check the mongo data store values to see if the mappings are stored properly 
```
$ mongo

MongoDB shell version v4.2.0
connecting to: mongodb://127.0.0.1:27017/?compressors=disabled&> 

> show dbs
admin   0.000GB
config  0.000GB
local   0.000GB
url_db  0.000GB

> use url_db
switched to db url_db

> show collections
mappings

> db.mappings.find({})
{ "_id" : ObjectId("5ffaebdce9f6e14e54c399f7"), "url" : "https://google.com", "short" : "99999" }
```

## Deployment 

Ansible playbook in the deployment folder can be used to do the entire prod like setup on a single machine. The APP will be running on port 8000.


### Helm Chart


There is also a helm chart for the application. Following command can be used to create the kubernetes yaml.
```
cd helm
helm template -f values.yaml . > short-url.yml
cat short-url.yml
```
Note:

This helm chart creates two deployments one for app and other for mongo. There will be a lot of changes required in the chart based on the kuberenetes cluster version, ingress used etc. 
