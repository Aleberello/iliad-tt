.PHONY: build up down logs shell migrate makemigrations createsuperuser test collectstatic loadfixtures

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

shell:
	docker-compose exec web python manage.py shell

migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

createsuperuser:
	docker-compose exec web python manage.py createsuperuser --noinput

test:
	docker-compose exec web python manage.py test

collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

loadfixtures:
	docker-compose exec web python manage.py loaddata products orders

# Command to run an arbitrary command
# Usage: make run cmd="python manage.py your_command"
run:
	docker-compose exec web $(cmd)

# Command to rebuild and restart the containers
rebuild:
	docker-compose down
	docker-compose build
	docker-compose up -d

# Command to enter the bash shell of the web container
bash:
	docker-compose exec web bash