package migrations

import (
	"context"
	"database/sql"

	"backpacktech.com/LPD/data"
	"github.com/pressly/goose/v3"
)

func init() {
	goose.AddMigrationContext(upNameColumnLotTable2, downNameColumnLotTable2)
}

func upNameColumnLotTable2(ctx context.Context, tx *sql.Tx) error {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	lots, err := data.GetAllLots(&prodDB)
	if err != nil {
		return err
	}

	query := "DROP TABLE lots"
	_, err = tx.Exec(query)
	if err != nil {
		return err
	}

	query = `CREATE TABLE LOTS (
		lotid uuid PRIMARY KEY,
		latitude Decimal(8,6),
		longitude Decimal(9,6),
		name VARCHAR(100),
		address VARCHAR(100),
		open time,
		close time,
		days VARCHAR(1)[],
		decals VARCHAR[],
		occupancy integer,
		capacity integer,
		notes VARCHAR(100),
		verified BOOLEAN
	)`
	_, err = tx.Exec(query)
	if err != nil {
		return err
	}

	for _, lot := range lots {
		newLot := lot.ConvertToInternalLot()
		psqlOpen := newLot.Open.FormatAsPSQLTime()
		psqlClose := newLot.Close.FormatAsPSQLTime()
		psqlDays := newLot.Days.ValueAsPSQLArray()
		psqlDecals := newLot.Decals.ValueAsPSQLArray()
		query = `INSERT INTO lots (lotid, latitude, longitude, name, address, open, close, days, decals, occupancy, capacity, notes, verified) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)`
		_, err = tx.Exec(query, newLot.LotID, newLot.Latitude, newLot.Longitude, "new_attribute_test", newLot.Address, psqlOpen, psqlClose, psqlDays, psqlDecals, newLot.Occupancy, newLot.Capacity, newLot.Notes, newLot.Verified)
		if err != nil {
			return err
		}
	}

	return nil
}

func downNameColumnLotTable2(ctx context.Context, tx *sql.Tx) error {
	// This code is executed when the migration is rolled back.
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	lots, err := data.GetAllLots(&prodDB)
	if err != nil {
		return err
	}

	query := "DROP TABLE lots"
	_, err = tx.Exec(query)
	if err != nil {
		return err
	}

	query = `CREATE TABLE LOTS (
    lotid uuid,
    latitude numeric(8,6),
    longitude numeric(9,6),
    address character varying(100),
    open time,
    close time,
    days character varying(1)[],
    decals character varying[],
    occupancy integer,
    capacity integer,
    notes character varying(100),
    verified boolean
)`
	_, err = tx.Exec(query)
	if err != nil {
		return err
	}

	for _, lot := range lots {
		newLot := lot.ConvertToInternalLot()
		psqlOpen := newLot.Open.FormatAsPSQLTime()
		psqlClose := newLot.Close.FormatAsPSQLTime()
		psqlDays := newLot.Days.ValueAsPSQLArray()
		psqlDecals := newLot.Decals.ValueAsPSQLArray()
		query = `INSERT INTO lots (lotid, latitude, longitude, address, open, close, days, decals, occupancy, capacity, notes, verified) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)`
		_, err = tx.Exec(query, newLot.LotID, newLot.Latitude, newLot.Longitude, newLot.Address, psqlOpen, psqlClose, psqlDays, psqlDecals, newLot.Occupancy, newLot.Capacity, newLot.Notes, newLot.Verified)
		if err != nil {
			return err
		}
	}

	return nil
}
