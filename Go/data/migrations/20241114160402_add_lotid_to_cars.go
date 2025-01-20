package migrations

import (
	"context"
	"database/sql"

	"backpacktech.com/LPD/data"
	"github.com/pressly/goose/v3"
)

func init() {
	goose.AddMigrationContext(upAddLotidToCars, downAddLotidToCars)
}

func upAddLotidToCars(ctx context.Context, tx *sql.Tx) error {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	query := "ALTER TABLE cars ADD COLUMN lotid uuid"
	_, err := tx.Exec(query)
	if err != nil {
		return err
	}

	return nil
}

func downAddLotidToCars(ctx context.Context, tx *sql.Tx) error {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	query := "ALTER TABLE cars DROP COLUMN lotid"
	_, err := tx.Exec(query)
	if err != nil {
		return err
	}
	return nil
}
