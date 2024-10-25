package endpoints

import (
	"backpacktech.com/LPD/data"
	"backpacktech.com/LPD/data/car"
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

	var saveCar *car.Car = car.New(uuid, reqCar.License_plate, reqCar.Color.String)

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

	cars, err := data.GetAllCars(&prodDB)

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

	updateCar := car.New(reqCar.CarID, reqCar.License_plate, reqCar.Color.String)
	err = data.UpdateCar(updateCar, &prodDB)
	if err != nil {
		c.JSON(500, gin.H{"error": "Unable to Update Car", "error_message": err.Error()})
		return
	}
	c.IndentedJSON(200, gin.H{"message": "CAR_UPDATE_SUCCESS"})
}
