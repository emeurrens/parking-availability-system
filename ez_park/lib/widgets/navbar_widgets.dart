import 'package:flutter/material.dart';

BottomNavigationBarItem mapViewPage() {
  return const BottomNavigationBarItem(
    icon: Icon(Icons.map_outlined),
    label: 'Map View',
  );
}

BottomNavigationBarItem listViewPage() {
  return const BottomNavigationBarItem(
      icon: Icon(Icons.list),
      label: 'List View'
  );
}

BottomNavigationBarItem filterPage() {
  return const BottomNavigationBarItem(
    icon: Icon(Icons.filter_alt),
    label: 'Filters',
  );
}

BottomNavigationBarItem detailsPage() {
  return const BottomNavigationBarItem(
    icon: Icon(Icons.local_parking),
    label: 'Parking Details',
  );
}
