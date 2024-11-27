package data

import (
	"testing"
	"time"

	"backpacktech.com/LPD/data/car"
	"backpacktech.com/LPD/data/lot"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

var testCarUUID uuid.UUID = uuid.Must(uuid.Parse("24028284-8201-4c49-87b1-6b81d54b18c5"))
var testLotUUID uuid.UUID = uuid.Must(uuid.Parse("f24dacb0-9513-45d9-90f8-b07e5dee5271"))

func TestSaveCar(t *testing.T) {
	db := setupTestDB()
	defer db.DB.Close()

	newUUID := uuid.New()
	vehicle := car.New(newUUID, "ABC123", "Red", testLotUUID)
	err := SaveCar(vehicle, db)
	assert.NoError(t, err)

	savedCar, err := GetCar(newUUID, db)
	assert.NoError(t, err)
	assert.Equal(t, newUUID, savedCar.GetID())
	assert.Equal(t, vehicle.License_plate, savedCar.License_plate)
	assert.Equal(t, vehicle.Color.String, savedCar.Color.String)
	assert.Equal(t, testLotUUID, savedCar.GetLotID())

	defer func() {
		err = DeleteCar(newUUID, db)
		assert.NoError(t, err)
	}()
}

func TestGetCar(t *testing.T) {
	db := setupTestDB()
	defer db.DB.Close()

	savedCar, err := GetCar(testCarUUID, db)
	assert.NoError(t, err)
	assert.Equal(t, testCarUUID, savedCar.GetID())
	assert.Equal(t, "TEST-CAR", savedCar.License_plate)
	assert.Equal(t, "TEST-COLOR", savedCar.Color.String)
	assert.Equal(t, testLotUUID, savedCar.GetLotID())
}

func TestGetAllCars(t *testing.T) {
	db := setupTestDB()
	defer db.DB.Close()

	vehicles, err := GetAllCars(testLotUUID, db)
	assert.NoError(t, err)
	assert.NotEmpty(t, vehicles)
}

func TestDeleteCar(t *testing.T) {
	db := setupTestDB()
	defer db.DB.Close()

	err := DeleteCar(testCarUUID, db)
	assert.NoError(t, err)

	savedCar, err := GetCar(testCarUUID, db)
	assert.Error(t, err)
	assert.Nil(t, savedCar)

	defer func() {
		vehicle := car.New(testCarUUID, "TEST-CAR", "TEST-COLOR", testLotUUID)
		err = SaveCar(vehicle, db)
		assert.NoError(t, err)
	}()
}

func TestUpdateCar(t *testing.T) {
	db := setupTestDB()
	defer db.DB.Close()

	vehicle := car.New(testCarUUID, "XYZ789", "Blue", uuid.Nil)
	err := UpdateCar(vehicle, db)
	assert.NoError(t, err)

	updatedCar, err := GetCar(testCarUUID, db)
	assert.NoError(t, err)
	assert.Equal(t, "XYZ789", updatedCar.License_plate)
	assert.Equal(t, "Blue", updatedCar.Color.String)

	defer func() {
		vehicle := car.New(testCarUUID, "TEST-CAR", "TEST-COLOR", uuid.Nil)
		err = UpdateCar(vehicle, db)
		assert.NoError(t, err)
	}()
}

func TestSaveLot(t *testing.T) {
	db := setupTestDB()
	defer db.DB.Close()

	newUUID := uuid.New()
	currentLot := lot.New(newUUID, 40.7128, -74.0060, "Lot 1", "123 Main St", time.Now(), time.Now(), []string{"M", "T"}, []string{"A", "B"}, 50, 100, "Notes", true, time.Now())
	err := SaveLot(currentLot, db)
	assert.NoError(t, err)

	savedLot, err := GetLot(newUUID, db)
	assert.NoError(t, err)
	assert.Equal(t, newUUID, savedLot.GetID())
	assert.Equal(t, currentLot.Name, savedLot.Name)
	assert.Equal(t, currentLot.Address, savedLot.Address)

	defer func() {
		err = DeleteLot(newUUID, db)
		assert.NoError(t, err)
	}()
}

func TestGetLot(t *testing.T) {
	db := setupTestDB()
	defer db.DB.Close()

	savedLot, err := GetLot(testLotUUID, db)
	assert.NoError(t, err)
	assert.Equal(t, testLotUUID, savedLot.GetID())
	assert.Equal(t, "Test Lot", savedLot.Name)
	assert.Equal(t, "123 Test St", savedLot.Address)
	assert.Equal(t, 50, savedLot.Occupancy)
	assert.Equal(t, 100, savedLot.Capacity)
	assert.Equal(t, "Test Notes", savedLot.Notes)
	assert.Equal(t, true, savedLot.EvCharging)
	assert.Equal(t, "Red", savedLot.Decals[0])
	assert.Equal(t, "T", savedLot.Days[1])
}

func TestGetAllLots(t *testing.T) {
	db := setupTestDB()
	defer db.DB.Close()

	allLots, err := GetAllLots(db)
	assert.NoError(t, err)
	assert.NotEmpty(t, allLots)
}

func TestDeleteLot(t *testing.T) {
	db := setupTestDB()
	defer db.DB.Close()

	err := DeleteLot(testLotUUID, db)
	assert.NoError(t, err)

	savedLot, err := GetLot(testLotUUID, db)
	assert.Error(t, err)
	assert.Nil(t, savedLot)

	defer func() {
		currentLot := lot.New(
			testLotUUID,
			40.7128,
			-74.0060,
			"Test Lot",
			"123 Test St",
			time.Now(),
			time.Now(),
			[]string{"M", "T"},
			[]string{"Red", "Green"},
			50,
			100,
			"Test Notes",
			true,
			time.Now(),
		)
		err = SaveLot(currentLot, db)
		assert.NoError(t, err)
	}()
}

func TestUpdateLot(t *testing.T) {
	db := setupTestDB()
	defer db.DB.Close()

	parking := lot.New(
		testLotUUID,
		12.7742,
		-11.0126,
		"Updated Lot",
		"456 Elm St",
		time.Now(),
		time.Now(),
		[]string{"W", "F"},
		[]string{"C", "D"},
		100,
		200,
		"Test Updated Notes",
		false,
		time.Now(),
	)
	err := UpdateLot(parking, db)
	assert.NoError(t, err)

	updatedLot, err := GetLot(testLotUUID, db)
	assert.NoError(t, err)
	assert.Equal(t, "Updated Lot", updatedLot.Name)
	assert.Equal(t, "456 Elm St", updatedLot.Address)
	assert.Equal(t, 100, updatedLot.Occupancy)
	assert.Equal(t, 200, updatedLot.Capacity)
	assert.Equal(t, "Test Updated Notes", updatedLot.Notes)
	assert.Equal(t, false, updatedLot.EvCharging)
	assert.Equal(t, "C", updatedLot.Decals[0])
	assert.Equal(t, "F", updatedLot.Days[1])

	defer func() {
		currentLot := lot.New(
			testLotUUID,
			40.7128,
			-74.0060,
			"Test Lot",
			"123 Test St",
			time.Now(),
			time.Now(),
			[]string{"M", "T"},
			[]string{"Red", "Green"},
			50,
			100,
			"Test Notes",
			true,
			time.Now(),
		)
		err = UpdateLot(currentLot, db)
		assert.NoError(t, err)
	}()
}

func setupTestDB() *Database {
	var prodDB Database = Database{
		DB:   GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	return &prodDB
}
