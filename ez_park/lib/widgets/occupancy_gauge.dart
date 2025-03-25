import 'dart:async';

import 'package:percent_indicator/percent_indicator.dart';
import 'package:flutter/material.dart';

import '../classes/parking_location.dart';
import '../data/all_parking_locations.dart';
import '../data/lot_database_client.dart';

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
  // database polling timer
  late Timer timer;

  // gauge variables
  late int occupancy;
  late int capacity;
  late double fillRatio;
  late Color color;

  @override
  void initState() {
    super.initState();

    // Set polling timer to check for changes
    timer = Timer.periodic(const Duration(seconds: 5), (timer) => updateOccupancy());

    // Check for changes
    updateOccupancy();
  }

  Future<void> _updateLotInfo() async {
    // Update local parking location data according to database information
    print("${widget.lotName} ${allParkingLocations[widget.lotName]!.lotID}");
    Map<String,dynamic> jsonUpdated = await LotDatabaseClient.getLot(allParkingLocations[widget.lotName]!.lotID);
    print(jsonUpdated);
    allParkingLocations[widget.lotName] = ParkingLocation.fromJson(jsonUpdated);
    print(allParkingLocations[widget.lotName]!.toJson());
  }

  void updateOccupancy() {
    _updateLotInfo();

    setState(() {
      // Update occupancy information for gauge
      occupancy = allParkingLocations[widget.lotName]!.occupancy;
      capacity = allParkingLocations[widget.lotName]!.capacity;
      fillRatio = occupancy.toDouble() / capacity.toDouble();

      // Update color according to occupancy percentage
      // If occupancy-capacity ratio is [0-0.4), make color green
      if (fillRatio < 0.4) {
        color = const Color(0xFF00BF00);
      }
      // If occupancy-capacity ratio is 0.4-0.8, make color yellow
      else if (fillRatio < 0.8) {
        color = const Color(0xFFFFCF00);
      }
      // If occupancy-capacity ratio is 0.8-1.0, make color red
      else {
        color = const Color(0xFFEF0000);
      }
    });
  }

  @override
  void dispose() {
    timer.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) =>
      Center(
        child: CircularPercentIndicator(
          // Until radius reaches a certain maximum (120 in this case),
          // grow proportionally to screen
          radius: MediaQuery.sizeOf(context).width / 4.5 > 120.0 ? 120.0
              : MediaQuery.sizeOf(context).width / 4.5,
          // Width of line
          lineWidth: 18.0,
          // Percent of gauge filled
          percent: fillRatio,
          progressColor: color,
          circularStrokeCap: CircularStrokeCap.butt,
          startAngle: 0.0,
          animation: true,
          animateFromLastPercent: true,
          animateToInitialPercent: false,
          center: Text.rich(
              TextSpan(
                children: <TextSpan>[
                  TextSpan(
                    text: "${capacity - occupancy}",
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 36),
                  ),
                  const TextSpan(
                    text: "\nspaces\n available",
                    style: TextStyle(fontWeight: FontWeight.normal, fontSize: 18, height: 1.0),
                  ),
                ],
              ),
              textAlign: TextAlign.center,
          ),
        ),
      );
}

