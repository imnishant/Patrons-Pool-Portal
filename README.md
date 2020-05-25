# Patron Hunter

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
