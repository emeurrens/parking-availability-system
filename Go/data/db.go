package data

import (
	"database/sql"
	"fmt"

	_ "github.com/lib/pq"
)

type Database struct {
	DB   *sql.DB
	Name string
}

func GetDB(dbName, dbUser, dbPassword, dbHost, dbEndpoint, region string, dbPort int) *sql.DB {

	//please help me clean this up...

	if dbName == "" {
		dbName = "burrow"
	}
	if dbUser == "" {
		dbUser = "joe"
	}
	if dbHost == "" {
		dbHost = "ec2-3-143-172-128.us-east-2.compute.amazonaws.com"
	}
	if dbPort == 0 {
		dbPort = 5432
	}
	// if dbEndpoint == "" {
	// 	dbEndpoint = fmt.Sprintf("%s:%d", dbHost, dbPort)
	// }
	if region == "" {
		region = "us-east-2"
	}
	if dbPassword == "" {
		dbPassword = "MgwIxXDkYcwqhfcD9oOc"
	}

	dsn := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s",
		dbHost, dbPort, dbUser, dbPassword, dbName,
	)

	db, err := sql.Open("postgres", dsn)
	if err != nil {
		panic(err)
	}

	err = db.Ping()
	if err != nil {
		panic(err)
	}
	return db
}
