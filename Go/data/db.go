package data

import (
	"database/sql"
	"log"
	"os"

	_ "github.com/lib/pq"
)

type Database struct {
	DB   *sql.DB
	Name string
}

func MustGetEnv(key string) string {
	value := os.Getenv(key)
	if value == "" {
		log.Fatalf("FATAL: Environment variable %s is not set!", key)
	}
	return value
}

func GetDB(dbName, dbUser, dbPassword, dbHost, dbEndpoint, region string, dbPort int) *sql.DB {

	//var connString = MustGetEnv("DATABASE_URL")
	var connString = "postgres://joe:MgwIxXDkYcwqhfcD9oOc@ec2-3-143-172-128.us-east-2.compute.amazonaws.com/burrow?sslmode=disable"

	db, err := sql.Open("postgres", connString)
	if err != nil {
		panic(err)
	}

	err = db.Ping()
	if err != nil {
		panic(err)
	}
	return db
}
