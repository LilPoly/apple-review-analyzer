run:
	uv run uvicorn app.main:app --reload

test:
	uv run pytest -v

lint:
	uv run ruff check .

format:
	uv run ruff format .

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

migrate:
	uv run alembic upgrade head

train-bert:
	uv run python ml/train_bert.py
