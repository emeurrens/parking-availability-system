import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter/material.dart';
import 'widgets/navbar_widgets.dart';
import 'pages/map_view_page.dart';
import 'pages/filter_page.dart';
import 'pages/list_view_page.dart';
import 'pages/location_detail_page.dart';
import 'data/lot_database_client.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: ".env");

  // Run app
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      title: 'EZPark UF',
      home: MainPage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class MainPage extends StatefulWidget {
  const MainPage({Key? key}) : super(key: key);

  @override
  State<MainPage> createState() => _MainPageState();
}

class _MainPageState extends State<MainPage> {
  final Future<int> _dbLoadStatus = LotDatabaseClient.pollLotsFromDB();

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
      body: FutureBuilder(
        // Attempt to load data from database
          future: _dbLoadStatus,
          builder: (BuildContext context, AsyncSnapshot<int> snapshot) {
            if (snapshot.hasData || snapshot.hasError) {
              return screens[_selectedIndex];
            }
            else {
              return Center(
                child: CircularProgressIndicator(color: Colors.blue),
              );
            }
          }
      ),
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
