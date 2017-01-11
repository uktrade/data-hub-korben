web: gunicorn -w 5 -b 0.0.0.0:8080 --access-logfile=- --preload korben.bau.webserver:wsgi_app
worker: korben bau poll
sync_cdms: ./scrape-forever.sh
sync_ch: korben sync ch
sync_django: korben sync django
sync_es: korben sync es
