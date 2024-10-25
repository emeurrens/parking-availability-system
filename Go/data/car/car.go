package car

import (
	"database/sql"

	"github.com/google/uuid"
)

type InternalCar struct {
	CarID         uuid.UUID      `json:"CarID"`
	License_plate string         `json:"license_plate"`
	Color         sql.NullString `json:"color"`
}

type Car struct {
	carID         uuid.UUID
	License_plate string         `json:"plate"`
	Color         sql.NullString `json:"color"`
}

func New(_uuid uuid.UUID, _license_plate string, _color string) *Car {

	var validColor bool = false
	if _color != "" {
		validColor = true
	}
	colorNullString := sql.NullString{String: _color, Valid: validColor}

	return &Car{
		carID:         _uuid,
		License_plate: _license_plate,
		Color:         colorNullString,
	}
}

func (c *Car) GetID() uuid.UUID {
	return c.carID
}

func (c *Car) ConvertToInternalCar() *InternalCar {
	return &InternalCar{
		CarID:         c.GetID(),
		License_plate: c.License_plate,
		Color:         c.Color,
	}
}
