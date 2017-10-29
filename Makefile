all: up

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build --force-rm

initdb:
	docker-compose run --rm -v `pwd`/data:/service/data web bash /service/initdb.sh

test:
	docker-compose run --rm -v `pwd`/test_data:/service/data -e DATADIR=/service/data web bash /service/tests.sh

clean-none:
	# Be careful! This command will remove all of your 'none' image
	docker image ls --filter "dangling=true" -q --no-trunc | xargs docker image rm

clean:
	docker-compose down --rmi all

clean-volume:
	docker-compose down -v
