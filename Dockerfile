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
#Copy nginx configuration file to the nginx folder
COPY nginx.conf /etc/nginx

#Install nginx web server
RUN apt-get clean \
    && apt-get -y update
RUN apt-get -y install nginx

#Install the dependencies
RUN pip install -r requirements-production.txt




#Run the container
RUN chmod +x ./start.sh
CMD ["./start.sh"]