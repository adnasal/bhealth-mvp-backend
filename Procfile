web: sh -c "python3 manage.py migrate && gunicorn bhealthapp.wsgi --bind 0.0.0.0:$PORT"
worker: sh -c "python3 bhealthapp/rabbitmq.py && python3 bhealthapp/consumers.py"
queue: sh -c "python3 manage.py rqworker high default"

