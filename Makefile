.PHONY: colab-setup tests

colab-setup:
	pip install -r requirements.txt -c constraints.txt

tests:
	pytest -q
