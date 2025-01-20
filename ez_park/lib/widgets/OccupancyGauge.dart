import 'dart:async';
import 'dart:convert';

import 'package:ez_park/data/psql_api_wrapper.dart';
import 'package:flutter/widgets.dart';
import '../classes/parking_location.dart';
import '../data/all_parking_locations.dart';

class OccupancyGauge extends StatefulWidget {
  const OccupancyGauge({
    super.key,
    required this.lotName,
  });

  final String lotName;

  @override
  State<OccupancyGauge> createState() => _OccupancyGaugeState();
}

class _OccupancyGaugeState extends State<OccupancyGauge> {
  int capacity = 0;
  Color color = const Color(0xFF00007F);
  Timer? timer;

  @override
  void initState() {
    super.initState();
    timer = Timer.periodic(const Duration(seconds: 10), (timer) => checkOccupancy());
    checkOccupancy();
  }

  void checkOccupancy() async {
    // Update parking location according to database information
    print(widget.lotName + " " + allParkingLocations[widget.lotName]!.lotID);
    Map<String, dynamic> jsonInput = jsonDecode(await getLot(allParkingLocations[widget.lotName]!.lotID) as String);
    jsonInput.putIfAbsent("LotID", () => allParkingLocations[widget.lotName]!.lotID);  // Need to add lotID since lotID is not returned with getLot
    print(jsonInput);

    allParkingLocations[widget.lotName] =
        ParkingLocation.fromJson(
            jsonInput,
        );
    print(allParkingLocations[widget.lotName]!.toJson());

    setState(() {
      // Update occupancy information
      capacity = allParkingLocations[widget.lotName]!.currentOccupancy;
      /// TODO: Update color according to occupancy percentage
    });
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) =>
      Center(
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 10),
          child: Text(
            "Occupancy: $capacity",
            style: TextStyle(
                fontSize: 30,
                fontWeight: FontWeight.bold,
                color: color
            ),
            textAlign: TextAlign.center,
          ),
        ),
      );
}