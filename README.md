# poukidex

I need some poukidex to remember what I saw.

## How to start application

Install docker and docker-compose

Add `.env` file in root directory, with below values, to run docker-compose from root

```
COMPOSE_PROJECT_NAME=poukidex
COMPOSE_FILE=docker/development.yml
```

- Add `.env file` in app/config, copying it from .env.dist and replacing values
- Run `docker-compose up -d` and wait for build
- Run `docker-compose exec django bash` to execute a bash into docker image
- Inside container, run `python manage.py createsuperuser` and create admin user
- Go to http://localhost:8000/api/docs# in browser to show api
