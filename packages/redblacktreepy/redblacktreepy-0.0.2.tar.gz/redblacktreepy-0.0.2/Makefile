
dist:
	python3 -m build

.PHONY: clean deploy

clean:
	rm -rf dist

deploy:
	twine upload dist/* --verbose
