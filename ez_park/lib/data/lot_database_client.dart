/// Import SDK libraries and packages
import "dart:convert";
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter/material.dart' show TimeOfDay;
import 'package:http/http.dart' as http;
import 'package:http/retry.dart';
/// Import local files
import "./all_parking_locations.dart";
import "../classes/parking_location.dart";

/// Class:
///     [LotDatabaseClient]
///
/// Description:
///     Singleton with functions and fields for handling PostgreSQL database
///     access for the backend lot table
///
class LotDatabaseClient {
  /// URL for connection to database
  static final String _psqlUrl = dotenv.env['PSQL_DB_URL']!;
  /// Most recent http response
  static late http.Response _response;
  /// Returns most recent http response
  static http.Response get lastResponse => _response;

  ///
  /// Function:
  ///         [pollGetAllLots]
  ///
  /// Description:
  ///       Polls the database periodically to retrieve all lot data from lot
  ///       database.
  ///
  /// Input:
  ///       int numRetries - Number of retries between requests
  ///       int retryIntervalMs - Millisecond count between retry intervals
  ///
  /// Affected:
  ///       [lastResponse]
  ///
  /// Output:
  ///       Returns future int http status code
  ///
  static Future<int> pollLotsFromDB({
    int numRetries = 5, int retryIntervalMs = 500
  }) async {

    // Create new lot list
    List<dynamic> updatedList = List.empty(growable: true);

    //
    // Attempt to read lot data from database successfully
    //
    final client = RetryClient(
      http.Client(),
      retries: numRetries,
      when: (response) => response.statusCode != 200,
      delay: (attempt) => Duration(milliseconds: retryIntervalMs),
    );

    try {
      _response = await client.get(Uri.http(_psqlUrl,'getAllLots'));
    } finally {
      client.close();
    }

    // If request was successful (response code == 200), update lot list
    if (_response.statusCode == 200) {
      // Add lots to updated list
      updatedList = jsonDecode(_response.body);

      // Based off of result, assign new data to corresponding lot entry
      // in allParkingLocations data structure. If there is a new lost, add to
      // allParkingLocations.
      for (final lot in updatedList) {
        allParkingLocations.update(lot['name'],
                (value) => ParkingLocation.fromJson(lot),
            ifAbsent: () => ParkingLocation.fromJson(lot)
        );
      }
    }

    // Return status code
    return _response.statusCode;

  }

  /// Function:
  ///         [getLot]
  ///
  /// Description:
  ///         Asynchronous function used to request data from PSQL database
  ///         lot table for lot entry identified by [lotID].
  ///
  /// Input:
  ///         [lotID] for the corresponding lot entry
  ///
  /// Affected:
  ///         [lastResponse]
  ///
  /// Output:
  ///         Future Map<String,dynamic> - JSON body response.
  ///         If successful, returns corresponding lot entry JSON body.
  ///         Otherwise, returns error JSON body.
  static Future<Map<String, dynamic>> getLot (final String lotID) async {

    // Endpoint Path
    const String path = "getLot";

    // Query parameters
    final Map<String, dynamic> params = {
      'id' : lotID,
    };

    // Prepare http request to get lot from lot ID
    http.Request request = http.Request('GET', Uri.http(_psqlUrl, path, params));

    // Send request and receive response
    _response = await http.Response.fromStream(await request.send());

    // Return JSON response
    return jsonDecode(_response.body);
  }

  /// Function:
  ///         [getAllLots]
  ///
  /// Description:
  ///         Asynchronous function used to request all data from LOT table
  ///         in database
  ///
  /// Input:
  ///         None
  ///
  /// Affected:
  ///       [lastResponse]
  ///
  /// Output:
  ///         Future Map<String,dynamic> - JSON body response.
  ///         If successful, returns JSON body with list of lot JSON objects.
  ///         Otherwise, returns error JSON body.
  static Future<List<dynamic>> getAllLots() async{
    // Endpoint path
    const String path = "getAllLots";

    // Prepare http request to get all lots
    http.Request request = http.Request('GET', Uri.http(_psqlUrl,path));

    // Send request
    _response = await http.Response.fromStream(await request.send());

    // Check response
    return jsonDecode(_response.body);
  }

  /// Function:
  ///       [updateLot]
  ///
  /// Description:
  ///       Asynchronous function used to update selected fields in the database for the lot with the
  ///       given [lotID]
  ///
  /// Input:
  ///         [lotID] - the unique ID of the particular lot entry being updated
  ///
  ///         The following optional named parameters:
  ///         double? latitude - latitude coordinate of lot,
  ///         double? longitude - longitude coordinate of lot,
  ///         String? name - the name of the lot,
  ///         String? address - any associated address of the lot,
  ///         TimeOfDay? restrictStart - start time of restrictions at lot,
  ///         TimeOfDay? restrictEnd - end time of restrictions at lot,
  ///         Set<int>? restrictDays - integer encoded set of days when restrictions are enforced
  ///                               1 = Monday, . . . , 7 = Sunday
  ///         Set<DecalType>? decals - set of decals enforced during restrictions at lot
  ///         int? capacity - approximate capacity of lot
  ///         int? occupancy - current, real-time occupancy of lot
  ///         bool? evCharging - if there is EV charging available at lot
  ///         String? notes - A string of notes for the specific lot
  ///         DateTime? creationDate - the date the lot was created
  ///
  /// Affected:
  ///         [lastResponse]
  ///
  /// Output:
  ///         Future int - response status code
  ///         Returns corresponding HTTP request status code
  ///
  static Future<int> updateLot(final String lotID,
      { double? latitude,
        double? longitude,
        String? name,
        String? address,
        TimeOfDay? restrictStart,
        TimeOfDay? restrictEnd,
        Set<int>? restrictDays, // e.g. 1 = Mon, ..., 7 = Sun
        Set<DecalType>? decals,
        int? occupancy,
        int? capacity,
        bool? evCharging,
        String? notes,
        DateTime? creationDate
      }) async {

    // Endpoint path
    const String path = "updateLot";

    // Get original data
    var jsonOld = await getLot(lotID);
    if (_response.statusCode != 200) {
      return _response.statusCode;                           // There was an error
    }

    // Prepare JSON string to be sent
    final String jsonNew = jsonEncode({
      'id': lotID,
      'latitude': latitude ?? jsonOld['latitude'],
      'longitude': longitude ?? jsonOld['longitude'],
      'name': name ?? jsonOld['name'],
      'address': address ?? jsonOld['address'],
      // This formatting is gonna cause something to break, I swear
      'open': restrictStart == null ? "${DateTime.parse(jsonOld['open']).hour}:${DateTime.parse(jsonOld['open']).hour}:00"
          :
      "${restrictStart.hour}:${restrictStart.minute}:00",
      'close': restrictEnd == null  ? "${DateTime.parse(jsonOld['close']).hour}:${DateTime.parse(jsonOld['close']).hour}:00"
          :
      "${restrictEnd.hour}:${restrictEnd.minute}:00",
      'days': restrictDays == null ? jsonOld['days'] :
      restrictDays.map((i) => Day.values[i-1].abbr).toList(),
      'decals': decals == null ? jsonOld['decals'] :
      decals.map((type) => type.toString()).toList(),
      'occupancy': occupancy ?? jsonOld['occupancy'],
      'capacity': capacity ?? jsonOld['capacity'],
      'ev_charging': evCharging ?? jsonOld['evCharging'],
      'notes': notes ?? jsonOld['notes'],
      'created_at': creationDate ?? jsonOld['created_at']
    });

    // Prepare http request to update lot entry
    var headers = {
      'Content-Type': 'application/json'
    };
    http.Request request = http.Request('PUT', Uri.http(_psqlUrl,path));
    request.headers.addAll(headers);
    request.body = jsonNew;

    // Send request and receive response
    _response = await http.Response.fromStream(await request.send());

    return _response.statusCode;
  }

  /// Function:
  ///         [saveLot]
  ///
  ///         Asynchronous function used to add new LOT entry into database
  ///         LOT table
  ///
  /// Input:
  ///         double latitude - latitude coordinate of lot,
  ///         double longitude - longitude coordinate of lot,
  ///         String name - the name of the lot,
  ///         TimeOfDay restrictStart - start time of restrictions at lot,
  ///         TimeOfDay restrictEnd - end time of restrictions at lot,
  ///         Set<int> restrictDays - integer encoded set of days when restrictions are enforced
  ///                               1 = Monday, . . . , 7 = Sunday
  ///         Set<DecalType> decals - set of decals enforced during restrictions at lot
  ///         int capacity - approximate capacity of lot
  ///         /*Optional named parameters*/
  ///         String address - any associated name of the lot
  ///         int occupancy - current, real-time occupancy of lot
  ///         bool evCharging - if there is EV charging at lot
  ///         String notes - A string of notes for the specific lot
  ///
  /// Affected:
  ///         [lastResponse]
  ///
  /// Output:
  ///         Future int - HTTP response status code
  ///         Returns corresponding HTTP request status code
  ///
  static Future<int> saveLot(
      double latitude, double longitude,
      String name,
      TimeOfDay restrictStart, TimeOfDay restrictEnd,
      Set<int> restrictDays,
      Set<DecalType> decals,
      int capacity, {int occupancy = -1,
        String address = "",
        bool evCharging = false,
        String notes = "",
      }) async {

    // Endpoint path
    const String path = "saveLot";

    // Set request headers
    var headers = {
      'Content-Type': 'application/json'
    };

    // Prepare JSON string body to be sent
    final String jsonNew = jsonEncode({
      'latitude': latitude,
      'longitude': longitude,
      'name': name,
      'address': address, // This column should be removed honestly
      'open': "${restrictStart.hour}:${restrictStart.minute}:00",
      'close': "${restrictEnd.hour}:${restrictEnd.minute}:00",
      'days': restrictDays.map((i) => Day.values[i - 1].abbr).toList(),
      'decals': decals.map((type) => type.toString()).toList(),
      'occupancy': occupancy,
      'capacity': capacity,
      'ev_charging': evCharging,
      'notes': notes
    });

    // Prepare http request to update lot entry
    http.Request request = http.Request('POST', Uri.http(_psqlUrl, path));
    request.headers.addAll(headers);
    request.body = jsonNew;

    // Send HTTP request and receive response
    _response = await http.Response.fromStream(await request.send());

    return _response.statusCode;
  }

  /// Function:
  ///         [saveLotFromJson]
  ///
  ///         Asynchronous function used to add new LOT entry into LOT table
  ///
  /// Input:
  ///         String jsonLot - JSON object String corresponding to the
  ///                          parameters and values of the LOT entry
  ///
  /// Affected:
  ///         [lastResponse]
  ///
  /// Output:
  ///         Future int - response status code
  ///         Returns corresponding HTTP request status code
  ///
  static Future<int> saveLotFromJson(String jsonLot) async{
    // Endpoint path
    const String path = "saveLot";

    // Prepare http request to add lot entry
    http.Request request = http.Request('POST', Uri.http(_psqlUrl,path));
    var headers = {
      'Content-Type': 'application/json'
    };
    request.body = jsonLot;
    request.headers.addAll(headers);

    // Send HTTP request and receive response
    _response = await http.Response.fromStream(await request.send());

    return _response.statusCode;
  }

  /// Function:
  ///         [deleteLot]
  ///
  ///         Asynchronous function used to request deletion of data from LOT
  ///           database
  ///
  /// Input:
  ///         String lotID - LotID for the corresponding LOT entry for deletion
  ///
  /// Affected:
  ///         [lastResponse]
  ///
  /// Output:
  ///         Future int - response status code
  ///         Returns corresponding HTTP request status code
  ///
  static Future<int> deleteLot(final String lotID) async {

    // Endpoint path
    const String path = "deleteLot";

    // Prepare http request to update lot entry
    http.Request request = http.Request('DELETE', Uri.http(_psqlUrl,path));
    var headers = {
      'Content-Type': 'application/json'
    };
    request.headers.addAll(headers);
    request.body = jsonEncode({
      'id' : lotID
    });

    // Send HTTP request and receive response
    _response = await http.Response.fromStream(await request.send());

    //Check response
    return _response.statusCode;

  }
}