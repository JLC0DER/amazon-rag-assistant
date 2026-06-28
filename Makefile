run-docker-compose:
	uv sync
	docker compose up --build

index-demo:
	uv sync
	uv run --env-file .env --directory apps/api python ../../scripts/index_demo.py

clean-notebook-outputs:
	jupyter nbconvert --clear-output --inplace notebooks/**/*.ipynb

run-evals-retriever:
	uv sync
	PYTHONPATH="$(CURDIR)/apps/api:$(CURDIR)/apps/api/src:$$PYTHONPATH" uv run --env-file .env python -m evals.eval_retriever
