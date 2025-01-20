import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

enum DecalType {
  gold,
  silver,
  official,
  orange,
  disabledEmployee,
  disabledStudent,
  blue,
  green,
  medResident,
  shandsYellow,
  staffCommuter,
  carpool,
  motorcycleScooter,
  parkAndRide,
  red1,
  red3,
  brown2,
  brown3,
  visitor;

  @override
  String toString() {
    return name;
  }
}

enum VehicleType { any, car, scooter }

const Map<DecalType, Set<DecalType>> allApplicableZones = {
  DecalType.gold: <DecalType>{
    DecalType.gold,
    DecalType.orange,
    DecalType.blue,
    DecalType.green,
    DecalType.red1,
    DecalType.red3,
    DecalType.brown2,
    DecalType.brown3,
    DecalType.parkAndRide,
    DecalType.visitor
  },
  DecalType.silver: <DecalType>{
    DecalType.silver,
    DecalType.visitor
  },
  DecalType.official: <DecalType>{
    DecalType.official,
    DecalType.orange,
    DecalType.blue,
    DecalType.green,
    DecalType.red1,
    DecalType.red3,
    DecalType.brown3,
    DecalType.brown2,
    DecalType.parkAndRide,
    DecalType.visitor
  },
  DecalType.orange: <DecalType>{
    DecalType.orange,
    DecalType.green,
    DecalType.parkAndRide,
    DecalType.visitor
  },
  DecalType.disabledEmployee: <DecalType>{
    DecalType.disabledEmployee,
    DecalType.disabledStudent,
    DecalType.parkAndRide,
    DecalType.visitor
  },
  DecalType.disabledStudent: <DecalType>{
    DecalType.disabledStudent,
    DecalType.disabledEmployee,
    DecalType.parkAndRide,
    DecalType.visitor
  },
  DecalType.blue: <DecalType>{
    DecalType.blue,
    DecalType.green,
    DecalType.parkAndRide,
    DecalType.visitor
  },
  DecalType.green: <DecalType>{
    DecalType.green,
    DecalType.parkAndRide,
    DecalType.visitor
  },
  DecalType.medResident: <DecalType>{
    DecalType.medResident,
    DecalType.orange,
    DecalType.green,
    DecalType.red1,
    DecalType.red3,
    DecalType.brown2,
    DecalType.brown3,
    DecalType.parkAndRide,
    DecalType.visitor
  },
  DecalType.shandsYellow: <DecalType>{
    DecalType.shandsYellow,
    DecalType.visitor
  },
  DecalType.staffCommuter: <DecalType>{
    DecalType.staffCommuter,
    DecalType.green,
    DecalType.visitor
  },
  DecalType.carpool: <DecalType>{
    DecalType.carpool,
    DecalType.orange,
    DecalType.blue,
    DecalType.green,
    DecalType.parkAndRide,
    DecalType.visitor
  },
  DecalType.motorcycleScooter: <DecalType>{DecalType.motorcycleScooter},
  DecalType.parkAndRide: <DecalType>{
    DecalType.parkAndRide,
    DecalType.visitor
  },
  DecalType.red1: <DecalType>{
    DecalType.red1,
    DecalType.red3,
    DecalType.parkAndRide,
    DecalType.visitor
  },
  DecalType.red3: <DecalType>{
    DecalType.red3,
    DecalType.parkAndRide,
    DecalType.visitor
  },
  DecalType.brown2: <DecalType>{
    DecalType.brown2,
    DecalType.parkAndRide,
    DecalType.visitor
  },
  DecalType.brown3: <DecalType>{
    DecalType.brown3,
    DecalType.parkAndRide,
    DecalType.visitor
  },
  DecalType.visitor: <DecalType>{
    DecalType.visitor,
  }
};

enum DayRestrictions { weekends, weekdays, all, none }

enum LotSize { large, medium, small }

/// Standard: 7:30-3:30pm
/// Mid: 7:30am-4:30pm
/// Extended: 7:30am-5:30pm
/// All Day: 12am-11:59pm
enum TimeRestrictions { standard, mid, extended, allDay, none }

//Corresponds to weekday number from DateTime.weekday
enum Day {
  monday(1, 'M'),
  tuesday(2, 'T'),
  wednesday(3, 'W'),
  thursday(4, 'R'),
  friday(5, 'F'),
  saturday(6, 'S'),
  sunday(7, 'U');

  const Day(this.num, this.abbr);
  final int num;
  final String abbr;
}

const Set<int> weekdays = <int>{
  1, //monday
  2, //tuesday
  3, //wednesday
  4, //thursday
  5 //friday
};

const Set<int> weekends = <int>{
  6, //saturday
  7 //sunday
};

class ParkingLocation {
  late String lotID;                  // lot database ID
  late String name;
  late LatLng location;
  late TimeOfDay restrictionStart;
  late TimeOfDay restrictionEnd;
  late Set<int> restrictedDays;
  late Set<DecalType> requiredDecals;
  late int currentOccupancy = -1;     // -1 if PAS not available (IMPORTANT)
  late bool evCharging = false;
  late String specialNotes;
  late bool isVerified = false;       
  late DateTime dateVerified = DateTime(1901,1,1);
  late LotSize sizeOfLot;

  ParkingLocation(this.name, this.location, this.restrictionStart,
      this.restrictionEnd, this.restrictedDays, this.requiredDecals);

  ParkingLocation.usingEnums(
      String locName,
      LatLng loc,
      TimeRestrictions timeRestrictions,
      DayRestrictions dayRestrictions,
      Set<DecalType> reqDecals,
      LotSize lotSize,
      {bool evCharge = false,
      String notes = "",
      bool verified = false,
      DateTime? dateVerified}) {
    name = locName;
    location = loc;
    requiredDecals = reqDecals;
    sizeOfLot = lotSize;
    evCharging = evCharge;
    specialNotes = notes;
    isVerified = verified;

    if (timeRestrictions == TimeRestrictions.allDay) {
      restrictionStart = const TimeOfDay(hour: 0, minute: 0);
      restrictionEnd = const TimeOfDay(hour: 23, minute: 59);
    } else if (timeRestrictions == TimeRestrictions.extended) {
      restrictionStart = const TimeOfDay(hour: 7, minute: 30);
      restrictionEnd = const TimeOfDay(hour: 17, minute: 30);
    } else if (timeRestrictions == TimeRestrictions.mid) {
      restrictionStart = const TimeOfDay(hour: 7, minute: 30);
      restrictionEnd = const TimeOfDay(hour: 16, minute: 30);
    } else if (timeRestrictions == TimeRestrictions.none) {
      restrictionStart = const TimeOfDay(hour: 0, minute: 0);
      restrictionEnd = const TimeOfDay(hour: 0, minute: 0);
    } else {
      restrictionStart = const TimeOfDay(hour: 8, minute: 30);
      restrictionEnd = const TimeOfDay(hour: 15, minute: 30);
    }

    if (dayRestrictions == DayRestrictions.all) {
      restrictedDays = weekdays.union(weekends);
    } else if (dayRestrictions == DayRestrictions.weekends) {
      restrictedDays = weekends;
    } else if (dayRestrictions == DayRestrictions.weekdays) {
      restrictedDays = weekdays;
    } else {
      restrictedDays = <int>{};
    }
  }

  ParkingLocation.fromJson(Map<String, dynamic> json) :
      lotID = json['LotID'] ?? "NO_ID",
      name = json['name'],
      location = LatLng(json['latitude'], json['longitude']),
      restrictionStart = TimeOfDay(hour: int.parse(json['open'].split(':')[0]),
                                    minute: int.parse(json['open'].split(':')[1])),
      restrictionEnd = TimeOfDay(hour: int.parse(json['close'].split(':')[0]),
                                  minute: int.parse(json['close'].split(':')[1])),
      restrictedDays = json['days'].map((abbr) =>
                  Day.values.firstWhere((day) => day.abbr == abbr).num).toSet().cast<int>(),
      requiredDecals = json['decals'].map((name) =>
                  DecalType.values.firstWhere((type) => type.name == name)).toSet().cast<DecalType>(),
      currentOccupancy = json['occupancy'],
      evCharging = json['evCharging'],
      specialNotes = json['notes'],
      isVerified = json['verified'] == "1901-01-01" ? false : true,
      dateVerified = DateTime.parse(json['verified']),
      sizeOfLot = json['capacity'] >= 500 ? LotSize.large :
                  json['capacity'] >= 100 ? LotSize.medium :
                  LotSize.small;

  Map<String, dynamic> toJson() => {
    'latitude':   location.latitude,
    'longitude':  location.longitude,
    'name':       name,
    'address':    "",        // Seriously could get rid of this address column
    'open':       "${restrictionStart.hour}:${restrictionStart.minute}:00",
    'close':      "${restrictionEnd.hour}:${restrictionEnd.minute}:00",
    'days':       restrictedDays.map((i) => Day.values[i-1].abbr).toList(),
    'decals':     requiredDecals.map((type) => type.toString()).toList(),
    'occupancy':  currentOccupancy,
    'capacity':   sizeOfLot == LotSize.large ? 500 :
                    sizeOfLot == LotSize.medium ? 100 :
                    20,
    'evCharging': evCharging,
    'notes':      specialNotes,
    'verified':   "${dateVerified.year}-"
                  "${dateVerified.month.toString().padLeft(2,'0')}-"
                  "${dateVerified.day.toString().padLeft(2,'0')}"
  };

  String formatNotes() {
    String retVal = "";

    if (evCharging) {
      retVal += "EV Charging available\n";
    }

    retVal += specialNotes;

    if (retVal.isEmpty) {
      return "No special restrictions";
    }

    return retVal;
  }

  String decalsToString() {
    if (requiredDecals.isEmpty) {
      return "None";
    }

    String decalString = "";

    int decalCount = requiredDecals.length;

    for (var element in requiredDecals) {
      String elementName = element.toString().split('.').last;
      elementName = elementName[0].toUpperCase() + elementName.substring(1);
      decalString += elementName;
      decalCount -= 1;
      if (decalCount > 0) {
        decalString += ", ";
      }
    }

    return decalString;
  }

  String restrictedDaysToString() {
    if (restrictedDays.isEmpty) {
      return "None";
    }
    List orderedDays = [...restrictedDays];
    orderedDays.sort();

    Map<int, String> dayNameMap = {
      1: "Mon",
      2: "Tue",
      3: "Wed",
      4: "Thur",
      5: "Fri",
      6: "Sat",
      7: "Sun"
    };

    String output = "";

    int dayCount = restrictedDays.length;
    if (dayCount == 7) {
      return "Every day";
    }

    for (var dayNum in orderedDays) {
      output += dayNameMap[dayNum]!;
      dayCount -= 1;
      if (dayCount > 0) {
        output += ", ";
      }
    }

    return output;
  }

  String restrictedTimesToString() {
    if (restrictionStart == const TimeOfDay(hour: 0, minute: 0) &&
        restrictionEnd == const TimeOfDay(hour: 23, minute: 59)) {
      return "All day";
    }
    if (restrictionStart == const TimeOfDay(hour: 0, minute: 0) &&
        restrictionEnd == const TimeOfDay(hour: 0, minute: 0)) {
      return "No restricted times";
    }

    String ampmStart = (restrictionStart.hour / 12 >= 1 ? "pm" : "am");
    String ampmEnd = (restrictionEnd.hour / 12 >= 1 ? "pm" : "am");

    return (restrictionStart.hour % 12).toString() +
        ":" +
        restrictionStart.minute.toString() +
        ampmStart +
        " - " +
        (restrictionEnd.hour % 12).toString() +
        ":" +
        restrictionEnd.minute.toString() +
        ampmEnd;
  }

  String lotSizeToString() {
    if (sizeOfLot == LotSize.large) {
      return "Large";
    } else if (sizeOfLot == LotSize.medium) {
      return "Medium";
    } else {
      return "Small";
    }
  }

  bool validDecal(DecalType decalType) {
    Set<DecalType> possibleMatches = allApplicableZones[decalType]!;

    for (var decal in possibleMatches) {
      if (requiredDecals.contains(decal)) {
        return true;
      }
    }
    return false;
  }

  bool validVehicleType(VehicleType vehicleTypeQuery) {
    if (vehicleTypeQuery == VehicleType.car &&
        requiredDecals.contains(DecalType.motorcycleScooter) &&
        requiredDecals.length == 1) {
      return false;
    }

    if (vehicleTypeQuery == VehicleType.scooter &&
        !requiredDecals.contains(DecalType.motorcycleScooter)) {
      return false;
    }

    return true;
  }
}
