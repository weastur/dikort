.PHONY: release build clean push py_build py_push docker_build docker_push
VERSION=`python -c "import dikort; print(dikort.__version__)"`

release: push

push: py_push docker_push

build: py_build docker_build

py_build: clean
	python -m build

docker_build: clean
	docker build . -t weastur/dikort:latest -t weastur/dikort:${VERSION}

py_push: py_build
	twine upload dist/dikort-${VERSION}*

docker_push: docker_build
	docker push weastur/dikort:latest
	docker push weastur/dikort:${VERSION}

clean:
	rm -rf build/ dikort.egg-info/ dist