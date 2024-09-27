import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:notify_app/notification_helper.dart';

var initializationSettingsAndroid =
const AndroidInitializationSettings('@mipmap/ic_launcher');
var initializationSettings =
InitializationSettings(android: initializationSettingsAndroid);

final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
FlutterLocalNotificationsPlugin();

@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();

  FirebaseMessaging messaging = FirebaseMessaging.instance;
  NotificationSettings settings = await messaging.requestPermission(
    alert: true,
    badge: true,
    sound: true,
  );
  await NotificationHelper.initialize(flutterLocalNotificationsPlugin);
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  await FirebaseMessaging.instance.subscribeToTopic("face_detection");

  flutterLocalNotificationsPlugin.initialize(initializationSettings);
  await flutterLocalNotificationsPlugin.initialize(
    initializationSettings,
    onDidReceiveNotificationResponse:
        (NotificationResponse notificationResponse) async {},
  );

  await NotificationHelper.initializeNotification();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Notify App',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      debugShowCheckedModeBanner: false,
      home: const MyHomePage(title: 'Notify App'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.pinkAccent, // Set background color to pinkAccent
        title: Text(
          widget.title,
          style: const TextStyle(color: Colors.white), // Set text color to white
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications, color: Colors.white), // Set icon color to white
            onPressed: () {
              // Navigate to All Notifications page
              Navigator.push(
                context,
                MaterialPageRoute(
                    builder: (context) => const NotificationsPage()),
              );
            },
          ),
        ],
      ),
      drawer: _buildDrawer(context),
      body: const Center(
        child: Text(
          'Notify App',
          style: TextStyle(fontSize: 24),
        ),
      ),
    );
  }

  Drawer _buildDrawer(BuildContext context) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: <Widget>[
          _buildDrawerHeader(context),
          ListTile(
            leading: const Icon(Icons.notifications, color: Colors.pinkAccent), // Set icon color to pinkAccent
            title: const Text('All Notifications'),
            onTap: () {
              Navigator.pop(context); // Close the drawer
              Navigator.push(
                context,
                MaterialPageRoute(
                    builder: (context) => const NotificationsPage()),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.settings, color: Colors.pinkAccent), // Set icon color to pinkAccent
            title: const Text('Notification Settings'),
            onTap: () {
              Navigator.pop(context); // Close the drawer
              Navigator.push(
                context,
                MaterialPageRoute(
                    builder: (context) => const NotificationSettingsPage()),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.account_balance_wallet_outlined, color: Colors.pinkAccent), // Set icon color to pinkAccent
            title: const Text('Live Streaming'),
            onTap: () {
              Navigator.pop(context); // Close the drawer
            },
          ),
        ],
      ),
    );
  }

  Widget _buildDrawerHeader(BuildContext context) {
    return Container(
      height: 80,
      decoration: const BoxDecoration(
        color: Colors.pinkAccent, // Set the drawer header background to pinkAccent
      ),
      child: const Center(
        child: Text(
          'Menu',
          style: TextStyle(
            color: Colors.white,
            fontSize: 24,
          ),
        ),
      ),
    );
  }
}

class NotificationsPage extends StatelessWidget {
  const NotificationsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.pinkAccent, // Set background color to pinkAccent
        title: const Text(
          'All Notifications',
          style: TextStyle(color: Colors.white), // Set text color to white
        ),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(8.0),
        itemCount: 5, // Define the number of cards
        itemBuilder: (context, index) {
          return Card(
            elevation: 4,
            margin: const EdgeInsets.symmetric(vertical: 10, horizontal: 15),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
            child: ListTile(
              leading: const Icon(Icons.account_circle_outlined,
                  color: Colors.pinkAccent),
              title: const Text(
                'Caution Unknown Face',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.pinkAccent,
                ),
              ),
              subtitle: Text.rich(
                TextSpan(
                  text: 'Detected at ',
                  style: const TextStyle(color: Colors.black),
                  children: <TextSpan>[
                    TextSpan(
                      text: '2024-09-30 10:00AM',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
              trailing: const Icon(Icons.arrow_forward_ios, color: Colors.grey),
              onTap: () {
                // Define your onTap action here
              },
            ),
          );
        },
      ),
    );
  }
}

class NotificationSettingsPage extends StatefulWidget {
  const NotificationSettingsPage({super.key});

  @override
  State<NotificationSettingsPage> createState() =>
      _NotificationSettingsPageState();
}

class _NotificationSettingsPageState extends State<NotificationSettingsPage> {
  final TextEditingController _notificationFrequencyController =
  TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.pinkAccent, // Set background color to pinkAccent
        title: const Text(
          'Notification Settings',
          style: TextStyle(color: Colors.white), // Set text color to white
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Set Notification Interval',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _notificationFrequencyController,
              decoration: const InputDecoration(
                labelText: 'Notification Interval (in minutes)',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _submitNotificationSettings,
              child: const Text('Submit'),
            ),
          ],
        ),
      ),
    );
  }

  void _submitNotificationSettings() {
    String frequency = _notificationFrequencyController.text;
    // Handle the logic for updating notification frequency
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Frequency set to $frequency minutes')),
    );
  }

  @override
  void dispose() {
    _notificationFrequencyController.dispose();
    super.dispose();
  }
}
