package main

import (
	"backpacktech.com/LPD/data"
)

func main() {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()
}
