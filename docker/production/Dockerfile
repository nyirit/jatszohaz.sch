FROM python:3

RUN apt-get update && apt-get install -y --no-install-recommends gettext
RUN pip install --upgrade pip
RUN pip install virtualenv

# Create the home directory for the new app user.
RUN mkdir -p /home/app

# Create an app user so our program doesn't run as root.
RUN groupadd -r app &&\
    useradd -r -g app -d /home/app -s /sbin/nologin -c "Docker image user" app

# Set the home directory to our app user's home.
WORKDIR /home/app

# Chown all the files to the app user.
RUN chown -R app:app .

# Change to the app user.
USER app

COPY base_9ab8bf9.txt base_req.txt
COPY prod_d5b148f.txt prod_req.txt
RUN virtualenv jh
RUN /bin/bash -c "source jh/bin/activate; pip install -r base_req.txt -r prod_req.txt"

# Start init script
EXPOSE 8000
COPY start.sh start.sh
CMD ["bash", "start.sh"]
