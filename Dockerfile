# set the image to base this image on
# Note that Riki requires <= 3.9
FROM python:3.9.13-bullseye
# create the directory for our applicationls
RUN mkdir /opt/app
RUN mkdir /var/db
RUN mkdir /opt/img
RUN apt update
RUN apt install sqlite3
# set that as our working directory
WORKDIR /opt/app
# copy the requirements file
COPY Riki/requirements.txt /opt/app/requirements.txt
# install requirements
RUN pip install -r requirements.txt
# copy the rest of the app
COPY Riki /opt/app/
# Expose network ports
EXPOSE 5001
# set the command to run
RUN chmod +x /opt/app/entrypoint.sh
ENTRYPOINT ["/opt/app/entrypoint.sh"]
# set the command to run 
CMD ["debug"]