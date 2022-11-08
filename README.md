# Run Docker

### Build the image

```sh
docker build -t backend/manage-orders-challenge:latest .
```

### Run the image on a local container

```sh
docker run --name manage-orders-challenge -dp 8080:8080 backend/manage-orders-challenge:latest
```

Start testing backend endpoints at <http://localhost:8080/api>. You can use the following Postman collection:
<https://www.getpostman.com/collections/5b1dc2563b68bb43237c>

# Run server

### Create venv

```sh
conda create -n dj_env Python=3.10
conda activate dj_env
conda install pip
pip install -r requirements.txt
```

### Run Unit Tests

In path: ./

```sh
cd app
python manage.py test
```

### Update models structure

In path: ./

```sh
cd app
python manage.py makemigrations core
python manage.py migrate core
python manage.py makemigrations
python manage.py migrate
```

### Run server

```sh
python manage.py runserver 8080
```

Start testing backend endpoints at <http://localhost:8080/api>. You can use the following Postman collection:
<https://www.getpostman.com/collections/5b1dc2563b68bb43237c>

# Notes

Implement server database to persist data.
