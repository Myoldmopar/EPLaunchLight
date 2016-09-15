clean:
	rm -rf build/ dist/

package:
	python setup.py py2app

html:
	make -C docs html

