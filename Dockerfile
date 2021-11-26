#Download Python from DockerHub and use it
FROM python:3.7.4

#Set the working directory in the Docker container
WORKDIR /srv/flagtrafo_app

#Copy the configuration files to the working directory
COPY requirements-production.txt .
COPY requirements.txt .
COPY start.sh .
COPY uwsgi.ini .
#Copy the Flask app code to the working directory
COPY src/ .

#Install nginx web server
RUN apt-get clean \
    && apt-get -y update
RUN apt-get -y install nginx \
    && apt-get -y install python3-dev \
    && apt-get -y install build-essential

#Install the dependencies
RUN pip install -r requirements-production.txt --src /usr/local/src

#Copy nginx configuration file to the nginx folder
COPY nginx.conf /etc/nginx
# Make the start file executable
RUN chmod +x ./start.sh
# What to do when the container is run: Execute start.sh
CMD ["./start.sh"]