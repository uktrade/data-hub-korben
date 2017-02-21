test-tier0:
	docker-compose -f test-tier0.yml down && docker-compose -f test-tier0.yml build && docker-compose -f test-tier0.yml run --service-ports test

test-unit:
	docker-compose -f test-unit.yml build && docker-compose -f test-unit.yml run --service-ports test

test-flake8:
	docker build -f Dockerfile-flake8 -t korben-flake8 . && docker run korben-flake8 flake8 /src
