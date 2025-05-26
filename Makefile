.PHONY: up down reset

up:
	bash setup.sh

down:
	docker compose down -v

reset: down
	docker system prune -f
	make up