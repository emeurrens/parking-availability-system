/*
    Class designed to control the state of MyApp in main.dart
 */
import 'package:flutter/material.dart';
import 'package:uf_parking_map/services/database_service.dart';
import 'login_page.dart';
import 'map_transfer.dart';


class CurrentPage extends StatefulWidget {
  const CurrentPage({Key? key}) : super(key: key);

  @override
  State<CurrentPage> createState() => _CurrentPageState();
}

class _CurrentPageState extends State<CurrentPage> {
  Widget currentState = LoginPage(notifyParent: () {});

  static Future<bool> pollDatabaseState() async {
    while (DatabaseService.databaseConnection.isClosed){}
    return true;
  }

  @override
  void initState() {
    super.initState();
    currentState = LoginPage(notifyParent: userLoggedIn);

    /* Attempt to connect to Postgres SQL database */
    debugPrint("Attempting to connect to database");
    DatabaseService.initDatabaseConnection();
  }
  /*
      Callback function designed to detect when user is logged in
      before changing app state
   */
  void userLoggedIn() {

    setState(() {
      currentState = MapTransfer();
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'UF Parking',
      theme: ThemeData(
        primarySwatch: Colors.lightBlue,
      ),
      home: currentState,
    );
  }
}
