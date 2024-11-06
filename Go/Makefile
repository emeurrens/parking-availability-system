ifneq (,$(wildcard ./.envrc))
    include .envrc
    export
endif

all:
	make build-backend
	make build-tests
	make build-migrations

build-backend:
	@echo "Building backend binary..."
	go build -o bin/backend cmd/run-backend/main.go

run-backend:
	@echo "Running backend..."
	./bin/backend

build-tests:
	@echo "Building tests binary..."
	go build -o bin/API_tests cmd/server-tests/API/main.go
	go build -o bin/endpoint_tests cmd/server-tests/endpoints/main.go

run-tests:
	@echo "Running tests..."
	DATABASE_URL=${DATABASE_URL} ./bin/API_tests
	DATABASE_URL=${DATABASE_URL} ./bin/endpoint_tests

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