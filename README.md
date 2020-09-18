# Check generator

## About

Here is my solution of Smena company [test assignment](https://github.com/smenateam/assignments/tree/master/backend) for Python backend developer.

In short, it is a service for generating checks for customers and staff of the delivery restaurant. Follow the link above to find out more.

## Installation

### Code

- Clone the repo <br>
  `git clone https://github.com/ElFanzo/Check-generator.git`
- Go to the project directory <br>
  `cd Check-generator`

### Python & dependencies

- Install Python >=3.6
- Create virtual environment <br>
  `python3 -m venv env`
- Install dependencies: <br>
  `pip install -r requirements.txt`

### Docker

This project using [PostgreSQL v9.6](https://hub.docker.com/_/postgres/), [Redis](https://hub.docker.com/_/redis/) and [wkhtmltopdf](https://hub.docker.com/r/openlabs/docker-wkhtmltopdf-aas/) docker images. Be sure that Docker is installed.

## Run

- Activate virtual environment <br>
  `. env/bin/activate`
- There are default environment variables in the [.env.example](.env.example) file. You can change them and export with <br>
  `. .env.example` <br>
 or set them manually
- Run docker containers <br>
  `docker-compose up -d`
- Change directory <br>
  `cd check_generator`
- Create DB <br>
  `python manage.py migrate`
- Create a superuser for an access to the Django admin panel <br>
  `python manage.py createsuperuser`
- Run RQ worker <br>
  `python manage.py rqworker`
- Run app <br>
  `python manage.py runserver`

## Test

To test the service you can run the command below <br>
`python manage.py test`

## API

API endpoints with examples of requests and responses are available in [api.yaml](api.yaml) file. It can be rendered using [Online Editor](https://editor.swagger.io/).
