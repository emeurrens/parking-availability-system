package migrations

import (
	"context"
	"database/sql"

	"backpacktech.com/LPD/data"
	"github.com/pressly/goose/v3"
)

func init() {
	goose.AddMigrationContext(upEvchargingLotTable, downEvchargingLotTable)
}

func upEvchargingLotTable(ctx context.Context, tx *sql.Tx) error {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	query := "ALTER TABLE lots ADD COLUMN evCharging BOOLEAN DEFAULT FALSE"

	_, err := tx.Exec(query)
	if err != nil {
		return err
	}

	return nil
}

func downEvchargingLotTable(ctx context.Context, tx *sql.Tx) error {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	query := "ALTER TABLE lots DROP COLUMN evCharging"
	_, err := tx.Exec(query)
	if err != nil {
		return err
	}

	return nil
}
