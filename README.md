# Pharmacies

---

## How to run

---

Run services

`docker-compose up`

Stop services

`docker-compose stop`

Down services

`docker-compose down`

---

## Migrations

---

Generate migration

`alembic revision --autogenerate -m "name of migration"`

Upgrade database to last migration

`alembic upgrade heads`
