# Python Web Development HW 12 - Tests

## Installation

Rename .env_example to .env and edit the credentials if necessary

```shell
mv .env_example .env
```
## Running the App

```shell
docker-compose up --build
```

Test the API with Swagger: http://localhost:8000/docs

## Running Tests

```shell
pytest --cov=src --cov-report=term-missing --disable-warnings
```
or make tests report in html format

```shell
pytest --cov=src tests/ --cov-report=html
```
Report will be available in /htmlcov/ directory

## Generate the documentation
Go to the docs directory
```bash
cd docs
```
execute for Windows
```bash
.\\make.bat html
```
execute for Linux
```bash
make html
```
Documentation will be available in /docs/_build/html/ directory