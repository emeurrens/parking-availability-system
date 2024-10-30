// package main

// import (
// 	"math/rand"
// 	"time"

// 	"backpacktech.com/LPD/data"
// 	"backpacktech.com/LPD/data/lot"
// 	"github.com/google/uuid"
// )

// func main() {
// 	var prodDB data.Database = data.Database{
// 		DB:   data.GetDB("", "", "", "", "", "", 0),
// 		Name: "prod",
// 	}
// 	defer prodDB.DB.Close()

// 	// Create new car with color red
// 	var testCar *car.Car = car.New(uuid.New(), "123456", "red")
// 	println(testCar.GetID().String())

// 	data.SaveCar(testCar, &prodDB)

// 	// Update car color to blue
// 	testCar.Color.String = "blue"
// 	data.UpdateCar(testCar, &prodDB)

// 	// Check if car color is blue
// 	checkCar, _ := data.GetCar(testCar.GetID(), &prodDB)
// 	println(checkCar.Color.String)

// 	// Delete car
// 	data.DeleteCar(testCar.GetID(), &prodDB)

// 	// Create 10 cars
// 	for i := 0; i < 10; i++ {
// 		var testCar *car.Car = car.New(uuid.New(), strconv.Itoa(rand.Intn(2000)), "red")
// 		data.SaveCar(testCar, &prodDB)
// 	}

// 	// Get all cars
// 	cars, _ := data.GetAllCars(&prodDB)
// 	for _, car := range cars {
// 		println(car.GetID().String())
// 		data.DeleteCar(car.GetID(), &prodDB)
// 	}

// 	openTime := time.Now()
// 	closeTime := time.Now()

// 	// Create new lot
// 	var testLot *lot.Lot = lot.New(uuid.New(), rand.Float64(), rand.Float64(), "1234 Main St", openTime, closeTime, []string{"M", "T"}, []string{"Red", "Green"}, 0, 100, "test note", true)
// 	println(testLot.GetID().String())

// 	data.SaveLot(testLot, &prodDB)

// 	// Update lot address
// 	testLot.Address = "5678 Elm St"
// 	data.UpdateLot(testLot, &prodDB)

// 	// Check if lot address is 5678 Elm St
// 	checkLot, _ := data.GetLot(testLot.GetID(), &prodDB)
// 	println(checkLot.Address)

// 	// Delete lot
// 	data.DeleteLot(testLot.GetID(), &prodDB)

// 	// Create 10 lots
// 	for i := 0; i < 10; i++ {
// 		var testLot *lot.Lot = lot.New(uuid.New(), rand.Float64(), rand.Float64(), "1234 Main St", openTime, closeTime, []string{"M", "T"}, []string{"Red", "Green"}, 0, 100, "test note", true)
// 		data.SaveLot(testLot, &prodDB)
// 	}

// 	// Get all lots
// 	lots, _ := data.GetAllLots(&prodDB)
// 	for _, lot := range lots {
// 		println(lot.GetID().String())
// 		data.DeleteLot(lot.GetID(), &prodDB)
// 	}
// }

package main

import (
	"backpacktech.com/LPD/endpoints"
	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()
	router.GET("/getCar", endpoints.GetCar)
	router.GET("/getAllCars", endpoints.GetAllCars)
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
