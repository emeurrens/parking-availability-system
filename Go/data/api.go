package data

import (
	"fmt"

	"backpacktech.com/LPD/data/car"
	"backpacktech.com/LPD/data/lot"
	"github.com/google/uuid"
)

// Todo set up DB migrations

func generateSQLCar(queryType string, vehicle *car.Car, uuid *string) string {
	switch queryType {
	case "save":
		return fmt.Sprintf("INSERT INTO cars(carid, plate, color) VALUES('%s', '%s', '%s')", vehicle.GetID(), vehicle.License_plate, vehicle.Color.String)
	case "get":
		return fmt.Sprintf("SELECT * FROM cars WHERE carid = '%s'", *uuid)
	case "getAll":
		return "SELECT * FROM cars"
	case "delete":
		return fmt.Sprintf("DELETE FROM cars WHERE carid = '%s'", *uuid)
	case "update":
		return fmt.Sprintf("UPDATE cars SET plate = '%s', color = '%s' WHERE carid = '%s'", vehicle.License_plate, vehicle.Color.String, vehicle.GetID())
	default:
		return ""
	}
}

func generateSQLLot(queryType string, lot *lot.Lot, uuid *string) string {
	switch queryType {
	case "save":
		return fmt.Sprintf("INSERT INTO lots(lotid, latitude, longitude, address) VALUES('%s', '%f', '%f', '%s')", lot.GetID().String(), lot.Longitude, lot.Longitude, lot.Address)
	case "get":
		return fmt.Sprintf("SELECT * FROM lots WHERE lotid = '%s'", *uuid)
	case "getAll":
		return "SELECT * FROM lots"
	case "delete":
		return fmt.Sprintf("DELETE FROM lots WHERE lotid = '%s'", *uuid)
	case "update":
		return fmt.Sprintf("UPDATE lots SET latitude = '%f', longitude = '%f', address = '%s' WHERE lotid = '%s'", lot.Longitude, lot.Longitude, lot.Address, lot.GetID().String())
	default:
		return ""
	}
}

func SaveCar(vehicle *car.Car, db *Database) (err error) {
	sql := generateSQLCar("save", vehicle, nil)

	_, err = db.DB.Exec(sql)
	if err != nil {
		panic(err)
	}
	return err
}

func GetCar(_uuid uuid.UUID, db *Database) (vehicle *car.Car, err error) {
	uuidStr := _uuid.String()
	sql := generateSQLCar("get", nil, &uuidStr)

	var carId uuid.UUID
	var license_plate, color string

	row := db.DB.QueryRow(sql)
	err = row.Scan(&carId, &license_plate, &color)
	if err != nil {
		return nil, err
	}

	vehicle = car.New(carId, license_plate, color)
	return vehicle, err
}

func GetAllCars(db *Database) (vehicles []*car.Car, err error) {
	sql := generateSQLCar("getAll", nil, nil)

	rows, err := db.DB.Query(sql)
	if err != nil {
		panic(err)
	}
	defer rows.Close()

	for rows.Next() {
		var carId uuid.UUID
		var license_plate, color string

		err = rows.Scan(&carId, &license_plate, &color)
		if err != nil {
			panic(err)
		}

		vehicle := car.New(carId, license_plate, color)
		vehicles = append(vehicles, vehicle)
	}
	return vehicles, err
}

func DeleteCar(uuid uuid.UUID, db *Database) (err error) {
	uuidStr := uuid.String()
	sql := generateSQLCar("delete", nil, &uuidStr)

	_, err = db.DB.Exec(sql)
	if err != nil {
		panic(err)
	}
	return err
}

func UpdateCar(vehicle *car.Car, db *Database) (err error) {
	sql := generateSQLCar("update", vehicle, nil)

	_, err = db.DB.Exec(sql)
	if err != nil {
		panic(err)
	}
	return err
}

func SaveLot(current_lot *lot.Lot, db *Database) (err error) {
	sql := generateSQLLot("save", current_lot, nil)

	_, err = db.DB.Exec(sql)
	if err != nil {
		panic(err)
	}
	return err
}

func GetLot(_uuid uuid.UUID, db *Database) (current_lot *lot.Lot, err error) {
	uuidStr := _uuid.String()
	sql := generateSQLLot("get", nil, &uuidStr)

	var lotID uuid.UUID
	var latitude, longitude float64
	var address string

	row := db.DB.QueryRow(sql)
	err = row.Scan(&lotID, &latitude, &longitude, &address)
	if err != nil {
		panic(err)
	}

	current_lot = lot.New(lotID, latitude, longitude, address)
	return current_lot, err
}

func GetAllLots(db *Database) (all_lots []*lot.Lot, err error) {
	sql := generateSQLLot("getAll", nil, nil)

	rows, err := db.DB.Query(sql)
	if err != nil {
		panic(err)
	}
	defer rows.Close()

	for rows.Next() {
		var lotID uuid.UUID
		var latitude, longitude float64
		var address string

		err = rows.Scan(&lotID, &latitude, &longitude, &address)
		if err != nil {
			panic(err)
		}

		lot := lot.New(lotID, latitude, longitude, address)
		all_lots = append(all_lots, lot)
	}
	return all_lots, err
}

func DeleteLot(uuid uuid.UUID, db *Database) (err error) {
	uuidStr := uuid.String()
	sql := generateSQLLot("delete", nil, &uuidStr)

	_, err = db.DB.Exec(sql)
	if err != nil {
		panic(err)
	}
	return err
}

func UpdateLot(current_lot *lot.Lot, db *Database) (err error) {
	sql := generateSQLLot("update", current_lot, nil)

	_, err = db.DB.Exec(sql)
	if err != nil {
		panic(err)
	}
	return err
}
