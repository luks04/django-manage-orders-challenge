# Run Docker

docker build -t backend/manage-orders-challenge:latest .
docker run --name manage-orders-challenge -dp 8080:8080 backend/manage-orders-challenge:latest

Go to localhost:8080 in yout browser

# Run server

conda create -n dj_env Python=3.10
conda activate dj_env
conda install pip
pip install -r requirements.txt
cd app
python manage.py runserver 8080

Go to localhost:8080 in yout browser
