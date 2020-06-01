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
# Remove the pkg-resources==0.0.0 from the requirements.txt
# Replace PyYAML==3.12 with PyYAML==3.13 in the requirements.txt
# Uncomment the line in the __init__.py files under the app folder.