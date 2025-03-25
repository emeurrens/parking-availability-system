import 'package:ez_park/classes/parking_location.dart';
import 'package:ez_park/classes/filtered_parking_locations.dart';

import '../data/all_parking_locations.dart';

import 'dart:async';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

class MapSample extends StatefulWidget {
  const MapSample({Key? key}) : super(key: key);

  @override
  State<MapSample> createState() => MapSampleState();
}

class MapSampleState extends State<MapSample> {
  final Completer<GoogleMapController> _controller = Completer();

  Map<MarkerId, Marker> mapMarkers = <MarkerId, Marker>{};
  MarkerId? selectedMarker;

  static LatLng _userPosition =
      currentParkingLocations.selectedParkingLocation.location;
  static LatLng _targetPosition =
      currentParkingLocations.selectedParkingLocation.location;

  static CameraPosition _kUserPosition = CameraPosition(
    target: _userPosition,
    zoom: 18,
  );

  static CameraPosition _kTargetPosition = CameraPosition(
    target: _targetPosition,
    zoom: 18,
  );

  @override
  void initState() {
    super.initState();
    _targetPosition = currentParkingLocations.selectedParkingLocation.location;
    _kTargetPosition = CameraPosition(
      target: _targetPosition,
      zoom: 18,
    );
    _getUserLocation();
    _setSelectedMarker(mapMarkers[
        MarkerId(currentParkingLocations.selectedParkingLocation.name)]);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: GoogleMap(
          mapType: MapType.hybrid,
          initialCameraPosition: _kTargetPosition,
          onMapCreated: (GoogleMapController controller) {
            _controller.complete(controller);
            _addMarkers();
            _setSelectedMarker(mapMarkers[MarkerId(
                currentParkingLocations.selectedParkingLocation.name)]);
          },
          myLocationEnabled: true,
          markers: Set<Marker>.of(mapMarkers.values)),
      floatingActionButton: Align(
        alignment: Alignment.bottomCenter,
        child: FloatingActionButton.extended(
          onPressed: _findClosestParking,
          label: const Text('Find nearest parking!'),
          icon: const Icon(Icons.location_pin),
        ),
      ),
    );
  }

  BitmapDescriptor _getAppropriateMarkerColor(String locationName) {
    if (locationName == currentParkingLocations.selectedParkingLocation.name) {
      return BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueCyan);
    }

    ParkingLocation location = allParkingLocations[locationName]!;

    if (location.requiredDecals.contains(DecalType.parkAndRide)) {
      return BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueYellow);
    }

    if (location.requiredDecals.contains(DecalType.red3) ||
        location.requiredDecals.contains(DecalType.red1)) {
      return BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueRed);
    }

    if (location.requiredDecals.contains(DecalType.brown2) ||
        location.requiredDecals.contains(DecalType.brown3)) {
      return BitmapDescriptor.defaultMarkerWithHue(45.0);
    }

    if (location.requiredDecals.contains(DecalType.green)) {
      return BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen);
    }

    if (location.requiredDecals.contains(DecalType.orange)) {
      return BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueOrange);
    }

    if (location.requiredDecals.contains(DecalType.blue)) {
      return BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueBlue);
    }

    if (location.requiredDecals.contains(DecalType.motorcycleScooter)) {
      return BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueAzure);
    }

    return BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueMagenta);
  }

  void _onMarkerTapped(MarkerId markerId) {
    final Marker? tappedMarker = mapMarkers[markerId];
    _setSelectedMarker(tappedMarker);
  }

  void _setSelectedMarker(Marker? tappedMarker) {
    if (tappedMarker != null) {
      setState(() {
        final MarkerId? previousMarkerId = selectedMarker;
        _targetPosition = currentParkingLocations
            .selectParkingLocation(tappedMarker.markerId.value)
            .location;

        if (previousMarkerId != null &&
            mapMarkers.containsKey(previousMarkerId)) {
          final Marker resetOld = mapMarkers[previousMarkerId]!.copyWith(
              iconParam: _getAppropriateMarkerColor(previousMarkerId.value));
          mapMarkers[previousMarkerId] = resetOld;
        }
        selectedMarker = tappedMarker.markerId;
        final Marker newMarker = tappedMarker.copyWith(
            iconParam: _getAppropriateMarkerColor(tappedMarker.markerId.value));
        mapMarkers[tappedMarker.markerId] = newMarker;
      });
    }
  }

  void _addMarkers() {
    setState(() {
      currentParkingLocations.filteredParkingLocations
          .forEach((name, parkingLocation) {
        MarkerId markerId = MarkerId(name);
        String markerSnippet =
            "Applicable Decals: " + parkingLocation.decalsToString();
        Marker marker = Marker(
          markerId: markerId,
          position: parkingLocation.location,
          icon: _getAppropriateMarkerColor(parkingLocation.name),
          infoWindow: InfoWindow(
              title: name + (parkingLocation.isVerified ? " ✓" : ""),
              snippet: markerSnippet),
          onTap: () {
            _onMarkerTapped(markerId);
          },
        );
        mapMarkers[markerId] = marker;
      });
    });
  }

  Future<void> _goToTargetLocation() async {
    final GoogleMapController controller = await _controller.future;
    controller.animateCamera(CameraUpdate.newCameraPosition(_kTargetPosition));
  }

  Future<void> _findClosestParking() async {
    final GoogleMapController controller = await _controller.future;
    await _getUserLocation().then((value) => setState(() {
          int minDistance = 0x7fffffffffffffff; //int max
          ParkingLocation closestLocation = defaultParkingLocation;
          currentParkingLocations.filteredParkingLocations
              .forEach((name, parkingLocation) {
            int distanceFromUser =
                haversineDistance(_userPosition, parkingLocation.location);
            if (distanceFromUser < minDistance) {
              minDistance = distanceFromUser;
              closestLocation = parkingLocation;
            }
          });
          _setTargetLocation(closestLocation.location);
          _setSelectedMarker(mapMarkers[MarkerId(closestLocation.name)]);
          _goToTargetLocation();
        }));

    controller.animateCamera(CameraUpdate.newCameraPosition(_kUserPosition));
  }

  Future<void> _getUserLocation() async {
    Position position = await Geolocator.getCurrentPosition();
    setState(() {
      _userPosition = LatLng(position.latitude, position.longitude);
      _kUserPosition = CameraPosition(
        target: _userPosition,
        zoom: 19,
      );
    });
  }

  void _setTargetLocation(LatLng latLng) async {
    setState(() {
      _targetPosition = latLng;
      _kTargetPosition = CameraPosition(
        target: _targetPosition,
        zoom: 18,
      );
    });
  }

  //https://en.wikipedia.org/wiki/Haversine_formula
  int haversineDistance(LatLng point1, LatLng point2) {
    double phi1 = point1.latitude;
    double phi2 = point2.latitude;
    double lam1 = point1.longitude;
    double lam2 = point2.longitude;
    int R = 6371000; //earth's radius

    return (2 *
            R *
            asin(sqrt(pow(sin((phi2 - phi1) / 2), 2) +
                cos(phi1) * cos(phi2) * pow(sin((lam2 - lam1) / 2), 2))))
        .toInt();
  }
}
