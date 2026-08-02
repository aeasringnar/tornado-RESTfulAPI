

# tornado-RESTfulAPI

An asynchronous project template based on tornado 6.X with RESTful API style, designed for quickly building enterprise-grade, high-performance, and high-concurrency server-side applications.

## Tech Stack

- **Framework Selection**: Based on tornado 6.X
- **Data Model**: Stored using PyMySQL
- **Authorization/Authentication**: Based on JWT
- **Built-in Features**: User system, exception handling, asynchronous processing, dynamic permissions, formatted API responses, log formatting, pagination, fuzzy search, filtering, sorting, caching, export, etc.

tornado provides the basic web framework
peewee provides ORM support
peewee-async provides asynchronous database operations
marshmallow provides data validation and serialization support. Note: Dropped wtforms for data validation.
aioredis provides asynchronous Redis operations
pyjwt provides authentication/authorization support

## Quick Start

For further information, see the [tornado documentation](https://www.tornadoweb.org/en/stable/index.html).

### Local Development

```bash
$ pip install -r requirements.txt # Install dependencies
$ python manage.py migrate # Migrate basic models
$ python apps/users/tests.py # Create default data
$ python manage.py ruserver 8080 # Run the server
$ open http://localhost:8000/
```

### Production Deployment

1. Standard Deployment on Linux Servers

```bash
# Get help: bash sever.sh help. Default startup port is 8080
bash server.sh start  # Starts debug service by default, single-threaded, uses config/dev_settings.py as config file
bash server.sh start prod # Command for production deployment, enables multi-threading based on CPU cores, uses config/prod_settings.py as config file
```

2. Docker Deployment. Note: Since the base image in the Dockerfile is a custom Python environment built by the author, please contact the author if you need it.

```bash
# Just run the following command to start the service in debug mode. To run in prod mode, change CMD ["./docker_start.sh", "8080"] in Dockerfile to CMD ["./docker_start.sh", "8080", "prod"]
# Note: The first argument of docker_start.sh specifies the port, and the second argument specifies the mode.
docker-compose up -d
```
