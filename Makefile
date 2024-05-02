.PHONY: all

all: install create_virtualenv activate_virtualenv install_requirements install_pyinstaller create_spec build_exe

install:
	pip install pipenv -i https://pypi.tuna.tsinghua.edu.cn/simple/

create_virtualenv:
	pipenv install

activate_virtualenv:
	pipenv run pip install -r require.txt

install_requirements:
	pipenv run pip install -r require.txt

install_pyinstaller:
	pipenv run pip install pyinstaller

create_spec:
	pipenv run pyi-makespec -F -i favicon.ico final.py

build_exe:
	pipenv run pyinstaller final.spec
