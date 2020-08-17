# Patrons Pool Portal

## Development
Want to contribute? Great!

Follow the below instructions to setup the project for development on your machine
Step 1: Run these below commands in the terminal to download all the dependencies for the project
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
Step 2: Make sure you install the MongoDB on your system and start the mongoDB daemon using the below command
```
sudo systemctl start mongod
```
Step 3: Run the application using the below command
```
flask run 
```
Bonus Step: If you want to go inside the mongoDB shell, type the below command
```
mongo
```

## Containarizing the Application
When you are done with the development and testing, you can create the docker image of your application by making the changes mentioned below:
1. Uncomment the main function specified in the main.py file.
2. Uncomment the line app.config['MONGO_URI'] = "mongodb://mongo:27017/FYP" in the __init__.py file under the app folder.
3. Comment the line app.config['MONGO_URI'] = "mongodb://localhost:27017/FYP" in the __init__.py file under the app folder.
4. Replace PyYAML==3.12 with PyYAML==3.13 in the requirements.txt
5. Remove the pkg-resources==0.0.0 from the requirements.txt

Make sure you haven't missed anything that is mentioned above that has to be changed. Once your are all done, follow the below steps to start building the docker image using the Dockerfile
```
docker build -t patrons-pool-app .
```

## Installing
If you want to just run the application using docker, follow the Steps mentioned below.

Step 1: Create a docker network named "patrons-pool-network" to establish communication between the front-end and back-end part of Patrons Pool applicaiton.
```
docker network create patrons-pool-network
```
Step 2: Run the "mongo" container in the "patrons-pool-network" docker network
```
docker run -d --restart unless-stopped --name=mongo --network=patrons-pool-network mongo
```
Step 3: Run the "sankalpsaxena/patrons-pool:4.0.0" container in the "patrons-pool-network" docker network
```
docker run -d --restart unless-stopped --name=patrons-pool-app --network=patrons-pool-network -p 9005:9001 -e MONGO_URL=mongodb://mongo:27017/FYP sankalpsaxena/patrons-pool:4.0.0
```
## Note
The sankalpsaxena/patrons-pool:5.0.0 image in the dockerhub is kubernetes compatible image, the environment variable for MONGO_URI has to be provided in the deployment file as the application ingest the value from the environment variable and no default path for the MONGO_URI has been specified in the image.

To run the application inside the docker network with the mongo conatainer and patronspool application container only make use of image sankalpsaxena/patrons-pool:4.0.0

## Setup nginx to redirect the traffic to the docker container
Go to the directory sites-enabled using the below command
```
sudo cd /etc/nginx/sites-enabled/
```
Edit the default file using the vi editor
```
sudo vi default
```
Delete all the content present in the file and add the below contents to it
```
server {
        listen 80 default_server;
        listen [::]:80 default_server;

        location / {
                proxy_pass  http://0.0.0.0:9005;
        }
}
```
Finally, restart the nginx service using the below command
```
sudo systemctl restart nginx
```
   
   
   

