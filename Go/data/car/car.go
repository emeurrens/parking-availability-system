package car

import (
	"database/sql"
	"encoding/json"

	"github.com/google/uuid"
)

type InternalCar struct {
	CarID         uuid.UUID      `json:"CarID,omitempty"`
	License_plate string         `json:"license_plate,omitempty"`
	Color         sql.NullString `json:"color,omitempty"`
	LotID         uuid.UUID      `json:"LotID,omitempty"`
}

type Car struct {
	carID         uuid.UUID
	License_plate string         `json:"license_plate"`
	Color         sql.NullString `json:"color"`
	lotID         uuid.UUID
}

func New(
	_uuid uuid.UUID,
	_license_plate string,
	_color string,
	_lotid uuid.UUID,
) *Car {

	var validColor bool = false
	if _color != "" {
		validColor = true
	}
	colorNullString := sql.NullString{String: _color, Valid: validColor}

	return &Car{
		carID:         _uuid,
		License_plate: _license_plate,
		Color:         colorNullString,
		lotID:         _lotid,
	}
}

func (c *Car) GetID() uuid.UUID {
	return c.carID
}

func (c *Car) GetLotID() uuid.UUID {
	return c.lotID
}

func (c *Car) ConvertToInternalCar() *InternalCar {
	return &InternalCar{
		CarID:         c.GetID(),
		License_plate: c.License_plate,
		Color:         c.Color,
		LotID:         c.GetLotID(),
	}
}

// Custom JSON Marshal function to maintain the LotID value as read only
func (c *Car) MarshalJSON() ([]byte, error) {
	return json.Marshal(&struct {
		License_plate string         `json:"license_plate"`
		Color         sql.NullString `json:"color"`
		LotID         uuid.UUID      `json:"LotID"`
	}{
		License_plate: c.License_plate,
		Color:         c.Color,
		LotID:         c.lotID,
	})
}

// Custom JSON Unmarshal function to maintain the LotID value as read only
func (c *Car) UnmarshalJSON(data []byte) error {
	var temp struct {
		License_plate string         `json:"license_plate"`
		Color         sql.NullString `json:"color"`
		LotID         uuid.UUID      `json:"LotID"`
	}

	if err := json.Unmarshal(data, &temp); err != nil {
		return err
	}

	c.License_plate = temp.License_plate
	c.Color = temp.Color
	c.lotID = temp.LotID

	return nil
}
