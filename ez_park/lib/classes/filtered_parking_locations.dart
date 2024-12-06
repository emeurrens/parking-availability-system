import 'package:ez_park/classes/parking_location.dart';
import 'package:ez_park/data/all_parking_locations.dart';
import 'package:flutter/material.dart';

class FilteredParkingLocations {
  late String searchQuery;
  late TimeOfDay timeQuery;
  late DateTime dateQuery;
  DecalType decalQuery = DecalType.visitor;
  late VehicleType vehicleTypeQuery;
  bool showAllLocationsQuery = false;

  late Map<String, ParkingLocation> filteredParkingLocations;
  late ParkingLocation selectedParkingLocation;

  FilteredParkingLocations(this.searchQuery,
      this.timeQuery,
      this.dateQuery,
      this.decalQuery,
      this.vehicleTypeQuery,
      this.filteredParkingLocations);

  FilteredParkingLocations.defaultFilters(){
    setDefaultFilters();
    applyFilters();
  }

  void setDefaultFilters() {
    searchQuery = "";
    timeQuery = TimeOfDay.now();
    dateQuery = DateTime.now();
    decalQuery = DecalType.visitor;
    vehicleTypeQuery = VehicleType.any;
    showAllLocationsQuery = false;
  }

  bool _dateTimeQueryIsRestricted(ParkingLocation parkingLocation) {
    TimeOfDay startTime = parkingLocation.restrictionStart;
    TimeOfDay endTime = parkingLocation.restrictionEnd;
    Set<int> restrictedDays = parkingLocation.restrictedDays;

    double start = startTime.hour + (startTime.minute / 60.0);
    double end = endTime.hour + (endTime.minute / 60.0);
    double query = timeQuery.hour + (timeQuery.minute / 60.0);

    return query >= start && query <= end && restrictedDays.contains(dateQuery.weekday);
  }

  void applyFilters(){
    Map<String, ParkingLocation> newMap = {};

    allParkingLocations.forEach((name, parkingLocation) {
      bool meetsCriteria = true;
      if (!name.contains(RegExp(searchQuery, caseSensitive: false))) {
        meetsCriteria = false;
      }

      if (_dateTimeQueryIsRestricted(parkingLocation) && !parkingLocation.validDecal(decalQuery)) {
        meetsCriteria = false;
      }

      if(!parkingLocation.validVehicleType(vehicleTypeQuery)) {
        meetsCriteria = false;
      }

      if (meetsCriteria || showAllLocationsQuery) {
        newMap[name] = parkingLocation;
      }
    });

    filteredParkingLocations = newMap;

    if(filteredParkingLocations.isEmpty) {
      filteredParkingLocations[defaultParkingLocation.name] = defaultParkingLocation;
      selectedParkingLocation = defaultParkingLocation;
    } else {
      selectedParkingLocation = defaultParkingLocation;
    }
  }

  ParkingLocation selectParkingLocation(String name) {
    selectedParkingLocation = filteredParkingLocations[name]!;
    return selectedParkingLocation;
  }

}

FilteredParkingLocations currentParkingLocations = FilteredParkingLocations.defaultFilters();
