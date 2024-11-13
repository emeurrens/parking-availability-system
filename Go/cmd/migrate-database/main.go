package main

import (
	"context"
	"flag"
	"log"
	"os"

	"backpacktech.com/LPD/data"
	_ "backpacktech.com/LPD/data/migrations"
	_ "github.com/jackc/pgx/v5/stdlib"
	"github.com/pressly/goose/v3"
)

var (
	flags = flag.NewFlagSet("goose", flag.ExitOnError)
	dir   = flags.String("dir", ".", "directory with migration files")
)

func main() {
	flags.Parse(os.Args[1:])
	args := flags.Args()

	command := args[0]

	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	ctx := context.Background()
	arguments := []string{}
	if len(args) > 1 {
		arguments = append(arguments, args[1:]...)
	}

	if err := goose.RunContext(ctx, command, prodDB.DB, *dir, arguments...); err != nil {
		log.Fatalf("goose %v: %v", command, err)
	}
}
