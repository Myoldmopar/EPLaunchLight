clean:
	rm -rf build/ dist/

package:
	python3 setup.py py2app

html:
	make -C docs html

listimports:
	grep -r '^import' --include="*.py" * | cut -d: -f2 | sort | uniq | cut -c 8-
