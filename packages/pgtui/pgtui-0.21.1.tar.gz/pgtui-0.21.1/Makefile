run:
	textual run --dev pgtui.cli:main

dist:
	python -m build

publish :
	twine upload dist/*.tar.gz dist/*.whl

clean:
	rm -rf build dist pgtui.egg-info
