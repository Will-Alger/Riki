# set the image to base this image on
# Note that Riki requires <= 3.9
FROM python:3.9.13-bullseye
# create the directory for our application
RUN mkdir /opt/app
# set that as our working directory
WORKDIR /opt/app
# copy the requirements file
COPY Riki/requirements.txt /opt/app/requirements.txt
# install requirements
RUN pip install -r requirements.txt
# copy the rest of the app
COPY Riki /opt/app/
# Expose network ports
EXPOSE 5000
# set the command to run 
CMD ["python", "Riki.py"]