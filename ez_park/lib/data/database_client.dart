import "dart:convert";

import "package:ez_park/data/all_parking_locations.dart";

import "./psql_api_wrapper.dart";
import "../classes/parking_location.dart";

/// TO DO - DOCUMENT ME
class DatabaseClient {
  /// TO DO - DOCUMENT ME
  static Future<void> pollGetLots([int timeOutMs = 5000]) async {
    // Create new lot list
    List<dynamic> updatedList = List.empty(growable: true);

    //
    // Try to read from database successfully
    //
    final stopwatch = Stopwatch();    // stopwatch to track timeout

    // Begin timing and poll until either timeout is reached or data is read successfully
    stopwatch.start();
    while (stopwatch.elapsedMilliseconds < timeOutMs) {
      // Read input from getAllLots
      dynamic dataIn = await getAllLots();
      // if function does not return an int error code, it must've been successful right?
      if (int.tryParse(dataIn) == null) {
        updatedList = jsonDecode(dataIn as String);
        break;
      }
      else {
        print(dataIn);
      }
    }
    stopwatch.stop();

    // Based off of result, assign new data to corresponding lot entry
    // in allParkingLocations data structure
    for (final lot in updatedList) {
      print(lot);
      allParkingLocations.update(lot['name'],
                                (value) => ParkingLocation.fromJson(lot),
                                ifAbsent: () => ParkingLocation.fromJson(lot)
      );
    }

    // Done :)
    return;
  }
}
