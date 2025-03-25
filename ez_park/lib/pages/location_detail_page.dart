import 'package:ez_park/classes/filtered_parking_locations.dart';
import 'package:ez_park/widgets/occupancy_gauge.dart';
import 'package:flutter/material.dart';
import 'package:map_launcher/map_launcher.dart';

class LocationDetailPage extends StatefulWidget {
  const LocationDetailPage({Key? key}) : super(key: key);

  @override
  _LocationDetailPageState createState() => _LocationDetailPageState();
}

class _LocationDetailPageState extends State<LocationDetailPage> {
  late List<AvailableMap> availableMaps;

  @override
  void initState() {
    super.initState();
    _loadMapLauncher();
  }

  void _loadMapLauncher() async {
    availableMaps = await MapLauncher.installedMaps;
  }

  void _launchMapsUrl() async {
    double lat =
        currentParkingLocations.selectedParkingLocation.location.latitude;
    double lng =
        currentParkingLocations.selectedParkingLocation.location.longitude;

    await availableMaps.first.showDirections(
      destination: Coords(lat, lng),
      directionsMode: DirectionsMode.driving,
      destinationTitle: currentParkingLocations.selectedParkingLocation.name
    );
  }

  @override
  Widget build(BuildContext context) => Scaffold(
      appBar: AppBar(
        title: const Text("Parking Details"),
      ),
      backgroundColor: Colors.grey[300],
      body: LayoutBuilder(
          builder: (context, constraints) => ListView(children: [
                Container(
                    constraints: BoxConstraints(
                      minHeight: constraints.maxHeight,
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        if(currentParkingLocations.selectedParkingLocation.occupancy != -1)
                          OccupancyGauge(
                            lotName: currentParkingLocations.selectedParkingLocation.name,
                          )
                        else
                          const Image(
                          height: 150,
                          image: NetworkImage(
                              'https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Florida_Gators_wordmark.png/640px-Florida_Gators_wordmark.png'),
                        ),
                        Text(
                          currentParkingLocations.selectedParkingLocation.name,
                          style: const TextStyle(
                              fontSize: 30,
                              fontWeight: FontWeight.bold,
                              decoration: TextDecoration.underline),
                          textAlign: TextAlign.center,
                        ),
                        Text(
                          currentParkingLocations.selectedParkingLocation
                              .formatNotes(),
                          style: const TextStyle(
                              fontSize: 16, fontStyle: FontStyle.italic),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 20),
                        const Text(
                          "Applicable Decals",
                          style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              decoration: TextDecoration.underline),
                          textAlign: TextAlign.center,
                        ),
                        Text(
                          currentParkingLocations.selectedParkingLocation
                              .decalsToString(),
                          style: const TextStyle(
                              fontSize: 24, fontWeight: FontWeight.normal),
                          textAlign: TextAlign.center,
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Text(
                              "Restricted Times",
                              style: TextStyle(
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                  decoration: TextDecoration.underline),
                              textAlign: TextAlign.center,
                            ),
                            currentParkingLocations
                                    .selectedParkingLocation.isVerified
                                ? (const Tooltip(
                                    message: 'Verified',
                                    child: Icon(Icons.check_circle,
                                        color: Colors.green, size: 24)))
                                : const Tooltip(
                                    message: 'Not yet verified',
                                    child: Icon(Icons.cancel_outlined,
                                        color: Colors.redAccent, size: 24)),
                          ],
                        ),
                        Text(
                          currentParkingLocations.selectedParkingLocation
                              .restrictedDaysToString(),
                          style: const TextStyle(
                              fontSize: 24, fontWeight: FontWeight.normal),
                          textAlign: TextAlign.center,
                        ),
                        Text(
                          currentParkingLocations.selectedParkingLocation
                              .restrictedTimesToString(),
                          style: const TextStyle(
                              fontSize: 24, fontWeight: FontWeight.normal),
                          textAlign: TextAlign.center,
                        ),
                        Row (
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Text(
                              "Lot Size",
                              style: TextStyle(
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                  decoration: TextDecoration.underline),
                            ),
                            Text(
                              ": " + currentParkingLocations.selectedParkingLocation
                                  .lotSizeToString(),
                              style: const TextStyle(
                                  fontSize: 24, fontWeight: FontWeight.normal),
                            ),
                          ],
                        ),
                        Container(
                            padding: const EdgeInsets.all(8),
                            child: ElevatedButton(
                              child: const Text("Open in Maps app"),
                              onPressed: _launchMapsUrl,
                            ))
                      ]
                    ))
              ])));
}
