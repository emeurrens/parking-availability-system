import 'package:ez_park/classes/parking_location.dart';
import 'package:flutter/material.dart';

const List<DropdownMenuItem<DecalType>> decalDropdownOptions = [
  DropdownMenuItem<DecalType>(
      value: DecalType.visitor, child: Text("Visitor (None)")),
  DropdownMenuItem<DecalType>(value: DecalType.blue, child: Text("Blue")),
  DropdownMenuItem<DecalType>(value: DecalType.brown2, child: Text("Brown 2")),
  DropdownMenuItem<DecalType>(value: DecalType.brown3, child: Text("Brown 3")),
  DropdownMenuItem<DecalType>(value: DecalType.gold, child: Text("Gold")),
  DropdownMenuItem<DecalType>(value: DecalType.green, child: Text("Green")),
  DropdownMenuItem<DecalType>(
      value: DecalType.medResident, child: Text("Medical Resident")),
  DropdownMenuItem<DecalType>(
      value: DecalType.motorcycleScooter, child: Text("Scooter")),
  DropdownMenuItem<DecalType>(value: DecalType.orange, child: Text("Orange")),
  DropdownMenuItem<DecalType>(
      value: DecalType.parkAndRide, child: Text("Park & Ride")),
  DropdownMenuItem<DecalType>(value: DecalType.red1, child: Text("Red 1")),
  DropdownMenuItem<DecalType>(value: DecalType.red3, child: Text("Red 3")),
  DropdownMenuItem<DecalType>(
      value: DecalType.shandsYellow, child: Text("Shands Yellow")),
  DropdownMenuItem<DecalType>(value: DecalType.silver, child: Text("Silver")),
  DropdownMenuItem<DecalType>(
      value: DecalType.staffCommuter, child: Text("Commuter")),
  DropdownMenuItem<DecalType>(
      value: DecalType.disabledEmployee, child: Text("Disabled Employee")),
  DropdownMenuItem<DecalType>(
      value: DecalType.disabledStudent, child: Text("Disabled Student")),
];
