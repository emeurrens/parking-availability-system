/// To Do: Fix bug where all locations don't load

import 'package:ez_park/pages/location_detail_page.dart';

import 'widgets/navbar_widgets.dart';
import 'pages/map_view_page.dart';
import 'pages/filter_page.dart';
import 'pages/list_view_page.dart';
import 'package:flutter/material.dart';
import 'data/database_client.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  /// To-Do: move to load during app
  // Get data from database
  DatabaseClient.pollGetLots();

  // Run app
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      title: 'EZ Park',
      home: MainPage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class MainPage extends StatefulWidget {
  const MainPage({Key? key}) : super(key: key);

  @override
  State<MainPage> createState() => MainPageState();
}

class MainPageState extends State<MainPage> {
  int _selectedIndex = 0;
  final List<Widget> screens = [
    const MapSample(),
    const ListViewPage(),
    const FilterPage(),
    const LocationDetailPage()
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: screens[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        backgroundColor: Colors.grey[300],
        items: <BottomNavigationBarItem>[
          mapViewPage(),
          listViewPage(),
          filterPage(),
          detailsPage(),
        ],
        currentIndex: _selectedIndex,
        unselectedItemColor: Colors.blue,
        selectedItemColor: Colors.deepOrange,
        onTap: _onItemTapped,
      ),
    );
  }
}
