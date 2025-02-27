package lot

import (
	"database/sql/driver"
	"encoding/json"
	"time"

	"github.com/google/uuid"
	"github.com/lib/pq"
)

type psqlStrArray []string
type psqlTime time.Time
type psqlDate time.Time

type InternalLot struct {
	LotID      uuid.UUID    `json:"LotID"`
	Latitude   float64      `json:"latitude"`
	Longitude  float64      `json:"longitude"`
	Name       string       `json:"name"`
	Address    string       `json:"address"`
	Open       psqlTime     `json:"open"`
	Close      psqlTime     `json:"close"`
	Days       psqlStrArray `json:"days"`
	Decals     psqlStrArray `json:"decals"`
	Occupancy  int          `json:"occupancy"`
	Capacity   int          `json:"capacity"`
	Notes      string       `json:"notes"`
	EvCharging bool         `json:"evCharging"`
	Verified   psqlDate     `json:"verified"`
}

type Lot struct {
	lotID      uuid.UUID
	Latitude   float64      `json:"latitude"`
	Longitude  float64      `json:"longitude"`
	Name       string       `json:"name"`
	Address    string       `json:"address"`
	Open       psqlTime     `json:"open"`
	Close      psqlTime     `json:"close"`
	Days       psqlStrArray `json:"days"`
	Decals     psqlStrArray `json:"decals"`
	Occupancy  int          `json:"occupancy"`
	Capacity   int          `json:"capacity"`
	Notes      string       `json:"notes"`
	EvCharging bool         `json:"evCharging"`
	Verified   psqlDate     `json:"verified"`
}

func New(
	_uuid uuid.UUID,
	_lat float64,
	_lon float64,
	_name string,
	_address string,
	_open time.Time,
	_close time.Time,
	_days []string,
	_decals []string,
	_occupancy int,
	_capacity int,
	_notes string,
	_evCharging bool,
	_verified time.Time,
) *Lot {
	return &Lot{
		lotID:      _uuid,
		Latitude:   _lat,
		Longitude:  _lon,
		Name:       _name,
		Address:    _address,
		Open:       psqlTime(_open),
		Close:      psqlTime(_close),
		Days:       _days,
		Decals:     _decals,
		Occupancy:  _occupancy,
		Capacity:   _capacity,
		Notes:      _notes,
		EvCharging: _evCharging,
		Verified:   psqlDate(_verified),
	}
}

func (l *Lot) GetID() uuid.UUID {
	return l.lotID
}

func (l *Lot) ConvertToInternalLot() *InternalLot {
	return &InternalLot{
		LotID:      l.GetID(),
		Latitude:   l.Latitude,
		Longitude:  l.Longitude,
		Name:       l.Name,
		Address:    l.Address,
		Open:       l.Open,
		Close:      l.Close,
		Days:       l.Days,
		Decals:     l.Decals,
		Occupancy:  l.Occupancy,
		Capacity:   l.Capacity,
		Notes:      l.Notes,
		EvCharging: l.EvCharging,
		Verified:   l.Verified,
	}
}

func (s *psqlStrArray) ValueAsPSQLArray() driver.Value {
	ret, err := pq.Array(*s).Value()
	if err != nil {
		panic(err)
	}
	return ret
}

func (t *psqlTime) FormatAsPSQLTime() string {
	return time.Time(*t).Format(time.TimeOnly)
}

func (t *psqlTime) MarshalJSON() ([]byte, error) {
	stringTime := time.Time(*t).Format(time.TimeOnly)
	return json.Marshal(stringTime)
}

func (t *psqlTime) UnmarshalJSON(b []byte) error {
	var stringTime string
	err := json.Unmarshal(b, &stringTime)
	if err != nil {
		return err
	}
	parsedTime, err := time.Parse(time.TimeOnly, stringTime)
	if err != nil {
		return err
	}
	*t = psqlTime(parsedTime)
	return nil
}

func (d *psqlDate) FormatAsPSQLDate() string {
	return time.Time(*d).Format(time.DateOnly)
}

func (d *psqlDate) MarshalJSON() ([]byte, error) {
	stringDate := time.Time(*d).Format(time.DateOnly)
	return json.Marshal(stringDate)
}

func (d *psqlDate) UnmarshalJSON(b []byte) error {
	var stringDate string
	err := json.Unmarshal(b, &stringDate)
	if err != nil {
		return err
	}
	parsedDate, err := time.Parse(time.DateOnly, stringDate)
	if err != nil {
		return err
	}
	*d = psqlDate(parsedDate)
	return nil
}
