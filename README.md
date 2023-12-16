Run RabbitMQ docker image: 
docker run -d --hostname my-rabbit --name some-rabbit -p 5672:5672 -p 8080:15672 rabbitmq:3-management

Run Celery worker:
celery -A library_service worker -l INFO

We are going to use the above code for running celert tasks
like borrowing overdue with telegram notification. I am going to
make better readme it just for beginning.
