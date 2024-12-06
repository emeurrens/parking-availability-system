import 'package:ez_park/classes/filtered_parking_locations.dart';
import 'package:ez_park/classes/parking_location.dart';
import 'package:ez_park/widgets/decal_dropdown_options.dart';
import 'package:flutter/material.dart';

class FilterPage extends StatefulWidget {
  const FilterPage({Key? key}) : super(key: key);

  @override
  State<FilterPage> createState() => FilterPageState();
}

class FilterPageState extends State<FilterPage> {
  final formKey = GlobalKey<FormState>();
  DecalType _decalType = currentParkingLocations.decalQuery;
  VehicleType _vehicleType = currentParkingLocations.vehicleTypeQuery;
  DateTime _selectedDate = currentParkingLocations.dateQuery;
  TimeOfDay _selectedTime = currentParkingLocations.timeQuery;
  String _searchValue = currentParkingLocations.searchQuery;
  bool _showAllLocations = currentParkingLocations.showAllLocationsQuery;

  bool _filtersChanged() {
    return currentParkingLocations.searchQuery != _searchValue ||
        currentParkingLocations.decalQuery != _decalType ||
        currentParkingLocations.vehicleTypeQuery != _vehicleType ||
        currentParkingLocations.timeQuery != _selectedTime ||
        currentParkingLocations.dateQuery != _selectedDate ||
        currentParkingLocations.showAllLocationsQuery != _showAllLocations;
  }

  void _applyFilters() {
    currentParkingLocations.searchQuery = _searchValue;
    currentParkingLocations.decalQuery = _decalType;
    currentParkingLocations.vehicleTypeQuery = _vehicleType;
    currentParkingLocations.timeQuery = _selectedTime;
    currentParkingLocations.dateQuery = _selectedDate;
    currentParkingLocations.showAllLocationsQuery = _showAllLocations;
    currentParkingLocations.applyFilters();
    _setFiltersFromQuery();
  }

  void _resetFilters() {
    currentParkingLocations.setDefaultFilters();
    currentParkingLocations.applyFilters();
    _setFiltersFromQuery();
  }

  void _setFiltersFromQuery() {
    setState(() {
      _decalType = currentParkingLocations.decalQuery;
      _vehicleType = currentParkingLocations.vehicleTypeQuery;
      _selectedDate = currentParkingLocations.dateQuery;
      _selectedTime = currentParkingLocations.timeQuery;
      _searchValue = currentParkingLocations.searchQuery;
      _showAllLocations = currentParkingLocations.showAllLocationsQuery;
    });
  }

  @override
  void initState() {
    super.initState();
    _setFiltersFromQuery();
  }

  _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
        context: context,
        initialDate: _selectedDate,
        firstDate: DateTime(2000),
        lastDate: DateTime(2025));
    if (picked != null && picked != _selectedDate) {
      setState(() {
        _selectedDate = picked;
      });
    }
  }

  Future<void> show() async {
    final TimeOfDay? result =
        await showTimePicker(context: context, initialTime: TimeOfDay.now());
    if (result != null) {
      setState(() {
        _selectedTime = result;
      });
    }
  }

  Color getColor(Set<WidgetState> states) {
    const Set<WidgetState> interactiveStates = <WidgetState>{
      WidgetState.pressed,
      WidgetState.hovered,
      WidgetState.focused,
    };
    if (states.any(interactiveStates.contains)) {
      return Colors.blue;
    }
    return Colors.red;
  }

  Widget showAllLocationsCheckbox() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        const Text(
          "Show ALL Parking Locations",
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
        Checkbox(
            checkColor: Colors.white,
            fillColor: WidgetStateProperty.resolveWith(getColor),
            value: _showAllLocations,
            onChanged: (bool? newValue) {
              setState(() {
                _showAllLocations = newValue!;
              });
            })
      ],
    );
  }

  Widget decalTypeDropdown() {
    return Column(
      children: <Widget>[
        const Text(
          "Your Decal",
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        Container(
            padding: const EdgeInsets.all(16),
            child: DropdownButton<DecalType>(
              value: _decalType,
              items: decalDropdownOptions,
              onChanged: (DecalType? value) {
                setState(() {
                  _decalType = value!;
                });
              },
            )),
      ],
    );
  }

  Widget vehicleTypeDropdown() {
    return Column(
      children: <Widget>[
        const Text(
          "Your Vehicle",
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        Container(
            padding: const EdgeInsets.all(16),
            child: DropdownButton<VehicleType>(
              value: _vehicleType,
              items: const <DropdownMenuItem<VehicleType>>[
                DropdownMenuItem<VehicleType>(
                    value: VehicleType.any, child: Text("Any")),
                DropdownMenuItem<VehicleType>(
                    value: VehicleType.car, child: Text("Car")),
                DropdownMenuItem<VehicleType>(
                    value: VehicleType.scooter,
                    child: Text("Scooter")),
              ],
              onChanged: (VehicleType? value) {
                setState(() {
                  _vehicleType = value!;
                });
              },
            )),
      ],
    );
  }

  Widget searchBarLocationNames() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        const SizedBox(
          height: 10.0,
        ),
        TextField(
          onChanged: (String value) {
            _searchValue = value;
          },
          decoration: const InputDecoration(
              prefixIcon: Icon(Icons.search),
              border: OutlineInputBorder(),
              labelText: "Search by Name"),
        ),
        const SizedBox(
          height: 10.0,
        ),
      ],
    );
  }

  Widget dateSelectionWidget() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        Container(
          padding: const EdgeInsets.all(8),
          child: Text(
            "${_selectedDate.toLocal()}".split(' ')[0],
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
        ),
        ElevatedButton(
          onPressed: () => _selectDate(context),
          child: const Text(
            "Select Date",
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
        )
      ],
    );
  }

  Widget timeSelectionWidget() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          child: Text(
            _selectedTime.format(context),
            style: const TextStyle(
                color: Colors.black, fontSize: 24, fontWeight: FontWeight.bold),
          ),
        ),
        ElevatedButton(
          onPressed: show,
          child: const Text("Select Time",
              style: TextStyle(fontWeight: FontWeight.bold)),
        ),
      ],
    );
  }

  Widget timeAndDateSelection() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        dateSelectionWidget(),
        const SizedBox(width: 30),
        timeSelectionWidget()
      ],
    );
  }

  Widget showWidget(Widget w) {
    if (_showAllLocations) {
      return const Text("Filters disabled, will show all UF parking locations.",
          style: TextStyle(fontStyle: FontStyle.italic));
    } else {
      return w;
    }
  }

  Widget statusText() {
    return Text(
        _filtersChanged()
            ? "Filters changed. Make sure to apply them!"
            : "Filters applied. Check out the Map or List view!",
        style: TextStyle(
            fontStyle: FontStyle.italic,
            color: _filtersChanged() ? Colors.red : Colors.green));
  }

  @override
  Widget build(BuildContext context) => Scaffold(
      appBar: AppBar(
        title: const Text("Filters"),
      ),
      backgroundColor: Colors.grey[300],
      body: Center(
          child: Form(
              key: formKey,
              child: SingleChildScrollView(
                  child: Column(
                mainAxisAlignment: MainAxisAlignment.start,
                children: <Widget>[
                  showAllLocationsCheckbox(),
                  showWidget(Column(
                    children: <Widget>[
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: <Widget>[
                          decalTypeDropdown(),
                          vehicleTypeDropdown(),

                        ],
                      ),
                      searchBarLocationNames(),
                      timeAndDateSelection(),
                    ],
                  )),
                  const SizedBox(height: 25),
                  Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: <Widget>[
                        ElevatedButton(
                          child: const Text("Apply Filters"),
                          onPressed: _applyFilters,
                          style:
                              ElevatedButton.styleFrom(foregroundColor: Colors.green),
                        ),
                        ElevatedButton(
                          child: const Text("Reset Filters"),
                          onPressed: _resetFilters,
                          style: ElevatedButton.styleFrom(
                              foregroundColor: Colors.redAccent),
                        )
                      ]),
                  statusText(),
                ],
              )))));
}
