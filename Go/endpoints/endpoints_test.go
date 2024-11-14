package endpoints

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"backpacktech.com/LPD/data"
	"backpacktech.com/LPD/data/car"
	"backpacktech.com/LPD/data/lot"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

var testCarUUID uuid.UUID = uuid.Must(uuid.Parse("24028284-8201-4c49-87b1-6b81d54b18c5"))
var testLotUUID uuid.UUID = uuid.Must(uuid.Parse("f24dacb0-9513-45d9-90f8-b07e5dee5271"))

func TestGetCar(t *testing.T) {
	router := gin.Default()
	router.GET("/getCar", GetCar)

	reqCar := car.InternalCar{CarID: testCarUUID}
	jsonValue, _ := json.Marshal(reqCar)
	req, _ := http.NewRequest("GET", "/getCar", bytes.NewBuffer(jsonValue))
	req.Header.Set("Content-Type", "application/json")

	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var returnCar car.InternalCar
	json.Unmarshal(w.Body.Bytes(), &returnCar)
	assert.Equal(t, "TEST-CAR", returnCar.License_plate)
	assert.Equal(t, "TEST-COLOR", returnCar.Color.String)
	assert.Equal(t, testLotUUID, returnCar.LotID)
}

func TestSaveCar(t *testing.T) {
	router := gin.Default()
	router.POST("/saveCar", SaveCar)

	reqCar := car.New(
		uuid.New(),
		"ABC123",
		"Red",
		testLotUUID,
	)
	jsonValue, _ := json.Marshal(reqCar)
	req, _ := http.NewRequest("POST", "/saveCar", bytes.NewBuffer(jsonValue))
	req.Header.Set("Content-Type", "application/json")

	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	response := w.Body.String()
	assert.Contains(t, response, "CAR_SAVED_SUCCESS")

	defer func() {
		if w.Code == http.StatusOK {
			db := data.Database{
				DB:   data.GetDB("", "", "", "", "", "", 0),
				Name: "prod",
			}
			defer db.DB.Close()

			var returnCar car.InternalCar
			err := json.Unmarshal(w.Body.Bytes(), &returnCar)
			if err != nil {
				panic(err)
			}
			data.DeleteCar(returnCar.CarID, &db)
		}
	}()
}

func TestDeleteCar(t *testing.T) {
	router := gin.Default()
	router.DELETE("/deleteCar", DeleteCar)

	reqCar := car.InternalCar{CarID: testCarUUID}
	jsonValue, _ := json.Marshal(reqCar)
	req, _ := http.NewRequest("DELETE", "/deleteCar", bytes.NewBuffer(jsonValue))
	req.Header.Set("Content-Type", "application/json")

	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	response := w.Body.String()
	assert.Contains(t, response, "CAR_DELETE_SUCCESS")

	defer func() {
		if w.Code == http.StatusOK {
			db := data.Database{
				DB:   data.GetDB("", "", "", "", "", "", 0),
				Name: "prod",
			}
			defer db.DB.Close()

			undoDeleteCar := car.New(testCarUUID, "TEST-CAR", "TEST-COLOR", testLotUUID)
			data.SaveCar(undoDeleteCar, &db)
		}
	}()
}

func TestGetAllCars(t *testing.T) {
	router := gin.Default()
	router.GET("/getAllCars", GetAllCars)

	req, _ := http.NewRequest("GET", "/getAllCars", nil)

	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	response := w.Body.Bytes()
	assert.NotEmpty(t, response)
}

func TestUpdateCar(t *testing.T) {
	router := gin.Default()
	router.PUT("/updateCar", UpdateCar)

	reqCar := car.InternalCar{
		CarID:         testCarUUID,
		License_plate: "XYZ789",
		Color: sql.NullString{
			String: "Blue",
			Valid:  true,
		},
		LotID: uuid.Nil,
	}
	jsonValue, _ := json.Marshal(reqCar)
	req, _ := http.NewRequest("PUT", "/updateCar", bytes.NewBuffer(jsonValue))
	req.Header.Set("Content-Type", "application/json")

	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	response := w.Body.String()
	assert.Contains(t, response, "CAR_UPDATE_SUCCESS")

	defer func() {
		if w.Code == http.StatusOK {
			db := data.Database{
				DB:   data.GetDB("", "", "", "", "", "", 0),
				Name: "prod",
			}
			defer db.DB.Close()

			carUpdate := car.New(
				testCarUUID,
				"TEST-CAR",
				"TEST-COLOR",
				uuid.Nil,
			)
			data.UpdateCar(carUpdate, &db)
		}
	}()
}

func TestGetLot(t *testing.T) {
	router := gin.Default()
	router.GET("/getLot", GetLot)

	// This is all useless filler info needed to parse the request into a JSON form
	beforeConvLot := lot.New(
		testLotUUID,
		0,
		0,
		"",
		"",
		time.Now(),
		time.Now(),
		[]string{},
		[]string{},
		0,
		0,
		"",
		false,
		time.Now(),
	)
	reqLot := beforeConvLot.ConvertToInternalLot()
	jsonValue, _ := json.Marshal(reqLot)
	req, _ := http.NewRequest("GET", "/getLot", bytes.NewBuffer(jsonValue))
	req.Header.Set("Content-Type", "application/json")

	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var returnLot lot.InternalLot
	json.Unmarshal(w.Body.Bytes(), &returnLot)
	assert.Equal(t, "Test Lot", returnLot.Name)
	assert.Equal(t, "123 Test St", returnLot.Address)
	assert.Equal(t, 50, returnLot.Occupancy)
	assert.Equal(t, 100, returnLot.Capacity)
	assert.Equal(t, "Test Notes", returnLot.Notes)
	assert.Equal(t, true, returnLot.EvCharging)
	assert.Equal(t, "Red", returnLot.Decals[0])
	assert.Equal(t, "T", returnLot.Days[1])
}

func TestSaveLot(t *testing.T) {
	router := gin.Default()
	router.POST("/saveLot", SaveLot)

	reqUUID := uuid.New()
	reqLot := lot.New(
		reqUUID,
		40.7128,
		-74.0060,
		"Test Lot",
		"123 Test St",
		time.Now(),
		time.Now(),
		[]string{"M", "T"},
		[]string{"A", "B"},
		50,
		100,
		"Test Notes",
		true,
		time.Now(),
	)

	jsonValue, _ := json.Marshal(reqLot)
	req, _ := http.NewRequest("POST", "/saveLot", bytes.NewBuffer(jsonValue))
	req.Header.Set("Content-Type", "application/json")

	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	response := w.Body.String()
	assert.Contains(t, response, "LOT_SAVED_SUCCESS")

	defer func() {
		if w.Code == http.StatusOK {
			db := data.Database{
				DB:   data.GetDB("", "", "", "", "", "", 0),
				Name: "prod",
			}
			defer db.DB.Close()

			var returnLot lot.InternalLot
			err := json.Unmarshal(w.Body.Bytes(), &returnLot)
			if err != nil {
				panic(err)
			}
			data.DeleteLot(returnLot.LotID, &db)
		}
	}()
}

func TestDeleteLot(t *testing.T) {
	router := gin.Default()
	router.DELETE("/deleteLot", DeleteLot)

	// This is all useless filler info needed to parse the request into a JSON form
	beforeConvLot := lot.New(
		testLotUUID,
		0,
		0,
		"",
		"",
		time.Now(),
		time.Now(),
		[]string{},
		[]string{},
		0,
		0,
		"",
		false,
		time.Now(),
	)
	reqLot := beforeConvLot.ConvertToInternalLot()
	jsonValue, _ := json.Marshal(reqLot)
	req, _ := http.NewRequest("DELETE", "/deleteLot", bytes.NewBuffer(jsonValue))
	req.Header.Set("Content-Type", "application/json")

	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	response := w.Body.String()
	assert.Contains(t, response, "LOT_DELETE_SUCCESS")

	defer func() {
		if w.Code == http.StatusOK {
			db := data.Database{
				DB:   data.GetDB("", "", "", "", "", "", 0),
				Name: "prod",
			}
			defer db.DB.Close()

			undoDeleteLot := lot.New(
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
			data.SaveLot(undoDeleteLot, &db)
		}
	}()
}

func TestGetAllLots(t *testing.T) {
	router := gin.Default()
	router.GET("/getAllLots", GetAllLots)

	req, _ := http.NewRequest("GET", "/getAllLots", nil)

	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	response := w.Body.Bytes()
	assert.NotEmpty(t, response)
}

func TestUpdateLot(t *testing.T) {
	router := gin.Default()
	router.PUT("/updateLot", UpdateLot)

	reqLot := lot.New(
		testLotUUID,
		70.7158,
		-25.0199,
		"Updated Lot",
		"456 Updated St",
		time.Now(),
		time.Now(),
		[]string{"W", "R"},
		[]string{"C", "D"},
		75,
		150,
		"Updated Notes",
		false,
		time.Now(),
	)
	internalReqLot := reqLot.ConvertToInternalLot()

	jsonValue, _ := json.Marshal(internalReqLot)
	req, _ := http.NewRequest("PUT", "/updateLot", bytes.NewBuffer(jsonValue))
	req.Header.Set("Content-Type", "application/json")

	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	response := w.Body.String()
	assert.Contains(t, response, "LOT_UPDATE_SUCCESS")

	defer func() {
		if w.Code == http.StatusOK {
			db := data.Database{
				DB:   data.GetDB("", "", "", "", "", "", 0),
				Name: "prod",
			}
			defer db.DB.Close()

			lotUpdate := lot.New(
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

			data.UpdateLot(lotUpdate, &db)
		}
	}()
}
