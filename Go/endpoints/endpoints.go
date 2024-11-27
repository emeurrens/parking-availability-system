package endpoints

import (
	"time"

	"backpacktech.com/LPD/data"
	"backpacktech.com/LPD/data/car"
	"backpacktech.com/LPD/data/lot"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

func GetCar(c *gin.Context) {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	var reqCar car.InternalCar

	err := c.BindJSON(&reqCar)

	if err != nil {
		c.JSON(400, gin.H{"error": "Invalid Car ID"})
		return
	}

	retCar, err := data.GetCar(reqCar.CarID, &prodDB)
	if err != nil {
		c.JSON(404, gin.H{"error": "Unable to Get Car", "error_message": err.Error()})
		return
	}
	c.IndentedJSON(200, retCar)
}

func SaveCar(c *gin.Context) {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	var reqCar car.Car
	uuid := uuid.New()

	err := c.BindJSON(&reqCar)

	if err != nil {
		c.JSON(400, gin.H{"error": "Invalid Car request"})
		return
	}

	var saveCar *car.Car = car.New(
		uuid,
		reqCar.License_plate,
		reqCar.Color.String,
		reqCar.GetLotID(),
	)

	err = data.SaveCar(saveCar, &prodDB)
	if err != nil {
		c.JSON(500, gin.H{"error": "Unable to Create Car", "error_message": err.Error()})
		return
	}
	c.IndentedJSON(200, gin.H{"CarID": uuid.String(), "message": "CAR_SAVED_SUCCESS"})
}

func DeleteCar(c *gin.Context) {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	var reqCar car.InternalCar

	err := c.BindJSON(&reqCar)

	if err != nil {
		c.JSON(400, gin.H{"error": "Invalid Car ID"})
		return
	}

	_, err = data.GetCar(reqCar.CarID, &prodDB)
	if err != nil {
		c.JSON(404, gin.H{"error": "Car does not exist", "error_message": err.Error()})
		return
	}

	err = data.DeleteCar(reqCar.CarID, &prodDB)
	if err != nil {
		c.JSON(404, gin.H{"error": "Unable to Delete Car", "error_message": err.Error()})
		return
	}
	c.IndentedJSON(200, gin.H{"message": "CAR_DELETE_SUCCESS"})
}

func GetAllCars(c *gin.Context) {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	var reqCar car.InternalCar

	err := c.BindJSON(&reqCar)
	if err != nil {
		c.JSON(400, gin.H{"error": "Invalid Lot ID"})
		return
	}

	cars, err := data.GetAllCars(reqCar.LotID, &prodDB)

	reqCars := make([]car.InternalCar, len(cars))
	for i, car := range cars {
		reqCars[i] = *car.ConvertToInternalCar()
	}

	if err != nil {
		c.JSON(404, gin.H{"error": "Unable to Get All Cars", "error_message": err.Error()})
		return
	}
	c.IndentedJSON(200, reqCars)
}

func GetAllCars_dev(c *gin.Context) {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	cars, err := data.GetAllCars_dev(&prodDB)

	reqCars := make([]car.InternalCar, len(cars))
	for i, car := range cars {
		reqCars[i] = *car.ConvertToInternalCar()
	}

	if err != nil {
		c.JSON(404, gin.H{"error": "Unable to Get All Cars", "error_message": err.Error()})
		return
	}
	c.IndentedJSON(200, reqCars)
}

func UpdateCar(c *gin.Context) {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	var reqCar car.InternalCar

	err := c.BindJSON(&reqCar)

	if err != nil {
		c.JSON(400, gin.H{"error": "Invalid Car request"})
		return
	}

	_, err = data.GetCar(reqCar.CarID, &prodDB)
	if err != nil {
		c.JSON(404, gin.H{"error": "Car does not exist", "error_message": err.Error()})
		return
	}

	updateCar := car.New(
		reqCar.CarID,
		reqCar.License_plate,
		reqCar.Color.String,
		reqCar.LotID,
	)
	err = data.UpdateCar(updateCar, &prodDB)
	if err != nil {
		c.JSON(500, gin.H{"error": "Unable to Update Car", "error_message": err.Error()})
		return
	}
	c.IndentedJSON(200, gin.H{"message": "CAR_UPDATE_SUCCESS"})
}

func GetLot(c *gin.Context) {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	var reqLot lot.InternalLot

	err := c.BindJSON(&reqLot)

	if err != nil {
		c.JSON(400, gin.H{"error": "Invalid Lot ID"})
		return
	}

	retLot, err := data.GetLot(reqLot.LotID, &prodDB)
	if err != nil {
		c.JSON(404, gin.H{"error": "Unable to Get Lot", "error_message": err.Error()})
		return
	}
	c.IndentedJSON(200, retLot)
}

func SaveLot(c *gin.Context) {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	var reqLot lot.Lot
	uuid := uuid.New()

	err := c.BindJSON(&reqLot)

	if err != nil {
		c.JSON(400, gin.H{"error": "Invalid Lot request"})
		return
	}

	var saveLot *lot.Lot = lot.New(
		uuid,
		reqLot.Latitude,
		reqLot.Longitude,
		reqLot.Name,
		reqLot.Address,
		time.Time(reqLot.Open),
		time.Time(reqLot.Close),
		reqLot.Days,
		reqLot.Decals,
		reqLot.Occupancy,
		reqLot.Capacity,
		reqLot.Notes,
		reqLot.EvCharging,
		time.Time(reqLot.Verified),
	)

	err = data.SaveLot(saveLot, &prodDB)
	if err != nil {
		c.JSON(500, gin.H{"error": "Unable to Create Lot", "error_message": err.Error()})
		return
	}
	c.IndentedJSON(200, gin.H{"LotID": uuid.String(), "message": "LOT_SAVED_SUCCESS"})
}

func DeleteLot(c *gin.Context) {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	var reqLot lot.InternalLot

	err := c.BindJSON(&reqLot)

	if err != nil {
		c.JSON(400, gin.H{"error": "Invalid Lot ID"})
		return
	}

	_, err = data.GetLot(reqLot.LotID, &prodDB)
	if err != nil {
		c.JSON(404, gin.H{"error": "Lot does not exist", "error_message": err.Error()})
		return
	}

	err = data.DeleteLot(reqLot.LotID, &prodDB)
	if err != nil {
		c.JSON(404, gin.H{"error": "Unable to Delete Lot", "error_message": err.Error()})
		return
	}
	c.IndentedJSON(200, gin.H{"message": "LOT_DELETE_SUCCESS"})
}

func GetAllLots(c *gin.Context) {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	lots, err := data.GetAllLots(&prodDB)

	reqLots := make([]lot.InternalLot, len(lots))
	for i, lot := range lots {
		reqLots[i] = *lot.ConvertToInternalLot()
	}

	if err != nil {
		c.JSON(404, gin.H{"error": "Unable to Get All Lots", "error_message": err.Error()})
		return
	}
	c.IndentedJSON(200, reqLots)
}

func UpdateLot(c *gin.Context) {
	var prodDB data.Database = data.Database{
		DB:   data.GetDB("", "", "", "", "", "", 0),
		Name: "prod",
	}
	defer prodDB.DB.Close()

	var reqLot lot.InternalLot

	err := c.BindJSON(&reqLot)

	if err != nil {
		c.JSON(400, gin.H{"error": "Invalid Lot request"})
		return
	}

	_, err = data.GetLot(reqLot.LotID, &prodDB)
	if err != nil {
		c.JSON(404, gin.H{"error": "Lot does not exist", "error_message": err.Error()})
		return
	}

	updateLot := lot.New(
		reqLot.LotID,
		reqLot.Latitude,
		reqLot.Longitude,
		reqLot.Name,
		reqLot.Address,
		time.Time(reqLot.Open),
		time.Time(reqLot.Close),
		reqLot.Days,
		reqLot.Decals,
		reqLot.Occupancy,
		reqLot.Capacity,
		reqLot.Notes,
		reqLot.EvCharging,
		time.Time(reqLot.Verified),
	)
	err = data.UpdateLot(updateLot, &prodDB)
	if err != nil {
		c.JSON(500, gin.H{"error": "Unable to Update Lot", "error_message": err.Error()})
		return
	}
	c.IndentedJSON(200, gin.H{"message": "LOT_UPDATE_SUCCESS"})
}
