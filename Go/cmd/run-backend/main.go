package main

import (
	"backpacktech.com/LPD/endpoints"
	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()
	gin.SetMode(gin.ReleaseMode)

	router.GET("/getCar", endpoints.GetCar)
	router.GET("/getAllCars", endpoints.GetAllCars)
	router.GET("/getAllCars_dev", endpoints.GetAllCars_dev)
	router.POST("/saveCar", endpoints.SaveCar)
	router.DELETE("/deleteCar", endpoints.DeleteCar)
	router.PUT("/updateCar", endpoints.UpdateCar)

	router.GET("/getLot", endpoints.GetLot)
	router.GET("/getAllLots", endpoints.GetAllLots)
	router.POST("/saveLot", endpoints.SaveLot)
	router.DELETE("/deleteLot", endpoints.DeleteLot)
	router.PUT("/updateLot", endpoints.UpdateLot)

	router.Run(":8080")
}
