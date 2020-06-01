FROM python:3.7.1
MAINTAINER Sankalp Saxena "sankalp.saxena.sta@gmail.com"

ADD . /PatronsPool
WORKDIR /PatronsPool

RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 9001
ENTRYPOINT ["python3"]
CMD ["main.py"]

# When creating the docker image do the following mentioned below:
# --------------------------------------------------------------------------------------------------------
# 1. Uncomment the main function specified in the main.py file.
# 2. Uncomment the line app.config['MONGO_URI'] = "mongodb://mongo:27017/FYP" in the __init__.py file under the app folder.
# 3. Comment the line app.config['MONGO_URI'] = "mongodb://localhost:27017/FYP" in the __init__.py file under the app folder.
# 4. Replace PyYAML==3.12 with PyYAML==3.13 in the requirements.txt
# 5. Remove the pkg-resources==0.0.0 from the requirements.txt