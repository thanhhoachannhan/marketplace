
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
	rm -fr uploads
	rm -fr locale
	rm -fr logs
	rm -fr db.sqlite3
mock:
	python ${MANAGE_FILE}.py mock_data
git:
	git add .
	git commit -m update
	git push
trans_init:
	# https://github.com/vslavik/gettext-tools-windows/releases
	# sudo apt-get install gettext
	django-admin makemessages --all --ignore=env
trans:
	django-admin compilemessages --ignore=env