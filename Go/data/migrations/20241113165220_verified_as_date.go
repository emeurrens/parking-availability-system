package migrations

import (
	"context"
	"database/sql"

	"backpacktech.com/LPD/data"
	"github.com/pressly/goose/v3"
)

func init() {
	goose.AddMigrationContext(upVerifiedAsDate, downVerifiedAsDate)
}

func upVerifiedAsDate(ctx context.Context, tx *sql.Tx) error {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	query := "ALTER TABLE lots DROP COLUMN verified"
	_, err := tx.Exec(query)
	if err != nil {
		return err
	}

	query = "ALTER TABLE lots ADD COLUMN verified DATE DEFAULT '1901-01-01'"
	_, err = tx.Exec(query)
	if err != nil {
		return err
	}

	return nil
}

func downVerifiedAsDate(ctx context.Context, tx *sql.Tx) error {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	query := "ALTER TABLE lots DROP COLUMN verified"
	_, err := tx.Exec(query)
	if err != nil {
		return err
	}

	query = "ALTER TABLE lots ADD COLUMN verified BOOLEAN DEFAULT FALSE"
	_, err = tx.Exec(query)
	if err != nil {
		return err
	}

	return nil
}
