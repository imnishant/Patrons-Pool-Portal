from app import app

# If you are running the application inside the docker container then uncomment the below lines
if __name__ == "__main__":
   app.run( host="0.0.0.0", port=9001)