test-korben-tier0:
	docker-compose -f test-tier0.yml build && docker-compose -f test-tier0.yml run --service-ports test

test-korben-unit:
	docker-compose -f test-unit.yml build && docker-compose -f test-unit.yml run --service-ports test
