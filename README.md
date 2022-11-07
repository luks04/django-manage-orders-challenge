# Run Docker

### Build the image

```sh
docker build -t backend/manage-orders-challenge:latest .
```

### Run the image on a local container

```sh
docker run --name manage-orders-challenge -dp 8080:8080 backend/manage-orders-challenge:latest
```

Go to <http://localhost:8080> in your browser

# Run server

```sh
conda create -n dj_env Python=3.10
conda activate dj_env
conda install pip
pip install -r requirements.txt
cd app
python manage.py makemigrations core
python manage.py migrate core
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8080
```

Go to <http://localhost:8080> in your browser
