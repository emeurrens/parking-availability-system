package lot

import (
	"github.com/google/uuid"
)

type Lot struct {
	lotID     uuid.UUID `db:"lotid"`
	Latitude  float64   `db:"latitude"`
	Longitude float64   `db:"longitude"`
	Address   string    `db:"address"`
}

func New(_uuid uuid.UUID, _lon float64, _lat float64, _address string) *Lot {
	return &Lot{
		lotID:     _uuid,
		Latitude:  _lat,
		Longitude: _lon,
		Address:   _address,
	}
}

func (l *Lot) GetID() uuid.UUID {
	return l.lotID
}
