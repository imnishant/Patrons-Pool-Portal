# Patrons Pool Portal

## Run these below commands in the terminal to build and run the project

```
python3 -m venv venv
```
```
source venv/bin/activate
```
```
pip3 install -r requirements.txt
```

## Run the local mail server

```
 docker run -p 3000:80 -p 2525:25 rnwood/smtp4dev:linux-amd64-v3

``` 
## To view the mail server type this below in browser
```
localhost:3000
```

## To run the application 

##### Activate the virtual environment first and then type the below command

```
flask run 
```

## Start the MongoDB server

```
sudo systemctl start mongod
```

## To go inside the MongoDB shell

```
mongo
```

## Containarizing the Application

##### When creating the docker image from the Dockerfile do the following changes mentioned below:

1. Uncomment the main function specified in the main.py file.
2. Uncomment the line app.config['MONGO_URI'] = "mongodb://mongo:27017/FYP" in the __init__.py file under the app folder.
3. Comment the line app.config['MONGO_URI'] = "mongodb://localhost:27017/FYP" in the __init__.py file under the app folder.
4. Replace PyYAML==3.12 with PyYAML==3.13 in the requirements.txt
5. Remove the pkg-resources==0.0.0 from the requirements.txt

Once the above changes are done run the below commands:

###### Build the docker image using the DockerFile
```
docker build -t patrons-pool-app .
```
###### First create a docker network so that your front-end and back-end can communicate  
```
docker network create patrons-pool-network
```
###### Run the mongo container in the patronspool docker network
```
docker run --name=mongo --rm --network=patrons-pool-network mongo
```
###### Run the mongo container in the patronspool docker network
```
docker run --name=patrons-pool-app --rm --network=patrons-pool-network -p 9005:9001 -e MONGO_URL=mongodb://mongo:27017/FYP patrons-pool-app
```