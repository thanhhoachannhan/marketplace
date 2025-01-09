
MANAGE_FILE = manage
PORT = 2000
HOST = localhost
init:
	rm -fr migrations
	rm -fr db.sqlite3
	python ${MANAGE_FILE}.py makemigrations app
	python ${MANAGE_FILE}.py migrate
	python ${MANAGE_FILE}.py shell -c "from django.contrib.auth import get_user_model; get_user_model().objects.filter(username='admin').exists() or get_user_model().objects.create_superuser('admin', 'admin@admin.com', 'admin')"
	# python ${MANAGE_FILE}.py runserver ${HOST}:${PORT}
up:
	python ${MANAGE_FILE}.py runserver ${HOST}:${PORT}
clean:
	pyclean .
	rm -fr app/migrations
	rm -fr emails
	rm -fr db.sqlite3
	rm log.log
mock:
	python ${MANAGE_FILE}.py mock_data
git:
	git add .
	git commit -m update
	git push