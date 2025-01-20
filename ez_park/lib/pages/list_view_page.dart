/// TODO: Add refresh (getAllCars from database API)

import 'package:ez_park/classes/filtered_parking_locations.dart';
import 'package:flutter/material.dart';

class ListViewPage extends StatefulWidget {
  const ListViewPage({Key? key}) : super(key: key);

  @override
  _ListViewPageState createState() => _ListViewPageState();
}

class _ListViewPageState extends State<ListViewPage> {
  List<String> parkingLocationList = [];

  @override
  void initState() {
    super.initState();
    _updateList();
  }

  void _updateList() {
    setState(() {
      parkingLocationList =
      [...currentParkingLocations.filteredParkingLocations.keys];
    });
  }

  void _onTileTapped(int index) {
    setState(() {
      currentParkingLocations.selectedParkingLocation = currentParkingLocations.filteredParkingLocations[parkingLocationList[index]]!;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: ListView.builder(
        itemCount: parkingLocationList.length,
        itemBuilder: (BuildContext context, int index) {
          return Card(
            child: ListTile(
              title: Text(
                parkingLocationList[index],
                textAlign: TextAlign.center,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              tileColor: currentParkingLocations.selectedParkingLocation.name == parkingLocationList[index] ? Colors.greenAccent : Colors.lightBlueAccent,
              onTap: () => _onTileTapped(index),
            ),
          );
        },

      ),
    );
  }
}
