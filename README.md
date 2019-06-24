# Jatszohaz.sch
[![Build Status](https://travis-ci.org/bubi24/jatszohaz.sch.svg?branch=master)](https://travis-ci.org/bubi24/jatszohaz.sch)

This Django site is for our university board game group. Main features are keeping inventory of games and administrate their lendings.
Live site is available at http://jatszohaz.sch.bme.hu

# Quick start
## Requirements
The installation requires you to have the following tools already installed:
* Git
* Docker

## Installation
The developer environment uses Docker hence there is no need to install anything else, except the listed tools above.

First of all, make sure to pull the repository using the following command: 
`git clone https://github.com/bubi24/jatszohaz.sch.git`

After changing the directory to the git root, run the following to set up the and run the containers:
`docker-compose up`

This command will download all the necessery containers and also start them. If this was successful you can already access your local copy of the site on http://localhost:8000

The webserver will restart automatically as soon as the source files are modified, so there's no need to restart anything manually.

Be advised, that the Auth.Sch login will not automatically work in local environment, this can only be done by configuring an OAuth client [here](https://auth.sch.bme.hu/console/index). However an admin user was created during the previous process, this allows to login under the Login2 option with the username `admin` and the password `admin`.

## Useful commands
* In case it's needed to access the Django shell (e.g. in order to apply migrations) or anything else inside the container, run the following commands:
  * `docker-compose exec web bash`. It is required to have the containers up and running (using `docker-compose up`). This command will run a shell inside the container.
  * `. jh/bin/activate`: to activate the virtual environment.
  * `jatszohaz.sch/jatszohaz/manage.py shell_plus`: in order to run the Django shell (replace `shell_plus` with any other command, e.g. `migrate`).

* To restart the `web` container: `docker-compose restart web`
