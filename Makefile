test-tier0:
	docker-compose -f test-tier0.yml build && docker-compose -f test-tier0.yml run --service-ports test

test-unit:
	docker-compose -f test-unit.yml build && docker-compose -f test-unit.yml run --service-ports test

test-flake8:
	docker-compose -f test-flake8.yml build && docker-compose -f test-flake8.yml run flake8 flake8 korben
