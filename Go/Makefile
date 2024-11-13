ifneq (,$(wildcard ./.envrc))
    include .envrc
    export
endif

all:
	make clean
	make build-backend
	make build-migrations

build-backend:
	@echo "Building backend binary..."
	go build -o bin/backend cmd/run-backend/main.go

run-backend:
	@echo "Running backend..."
	DATABASE_URL=${DATABASE_URL} ./bin/backend

build-migrations:
	@echo "Building migrations binary..."
	go build -o bin/migrate cmd/migrate-database/main.go

run-migration-up:
	@echo "Running migration Up..."
	DATABASE_URL=${DATABASE_URL} GOOSE_MIGRATION_DIR=${GOOSE_MIGRATION_DIR} GOOSE_DRIVER=${GOOSE_DRIVER} GOOSE_DBSTRING=${GOOSE_DBSTRING}  ./bin/migrate up

run-migration-down:
	@echo "Running migration Down..."
	DATABASE_URL=${DATABASE_URL} GOOSE_MIGRATION_DIR=${GOOSE_MIGRATION_DIR} GOOSE_DRIVER=${GOOSE_DRIVER} GOOSE_DBSTRING=${GOOSE_DBSTRING}  ./bin/migrate down

run-migration-status:
	@echo "Running migration Status..."
	DATABASE_URL=${DATABASE_URL} GOOSE_MIGRATION_DIR=${GOOSE_MIGRATION_DIR} GOOSE_DRIVER=${GOOSE_DRIVER} GOOSE_DBSTRING=${GOOSE_DBSTRING}  ./bin/migrate status

clean:
	@echo "Cleaning up..."
	rm -rf bin