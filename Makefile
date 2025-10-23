clean:
	find . -name '*.pyo' -delete
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	find . -name '*~' -delete

lint:
	flake8 --max-line-length 88 beanstalk_dispatch && black --check beanstalk_dispatch && isort --check-only --recursive beanstalk_dispatch

test: lint
	test_app/manage.py test beanstalk_dispatch

installdeps:
	pip install --upgrade pip
	pip install -e .
	pip install -r dev-requirements.txt

release: clean lint test
	@if [ -z "$(TAG_NAME)" ]; then \
		echo "Usage: make release TAG_NAME=<tag-name>"; \
		exit 1; \
	fi
	# NOTE(joshblum): First you should update the changelog and bump the
	# version in setup.py
	git clean -dxf
	git tag $(TAG_NAME)
	git push --tags
	# Create the wheels for Python2 and Python3.
	python3 setup.py sdist bdist_wheel --universal
	# To check whether the README formats properly.
	twine check dist/*
	# Upload to pypi.
	twine upload dist/*
