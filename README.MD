# Asterisk developer con python
## Creación de base de datos

Desde la carpeta del proyecto ingresamos al container de django con el comando
```sh
docker-compose exec fastagi bash
```
Ya dentro del container activamos el ambiente de python con
```sh
source /opt/virtualenv/bin/activate
```
Procedemos a realizar el archivo de la migración con django
```sh
python3 /opt/fastagi/manage.py makemigrations
```

El último paso es migrar a base de datos los cambios realizados
```sh
python3 /opt/fastagi/manage.py migrate
```
