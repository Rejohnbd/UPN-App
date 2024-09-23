import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import '../main.dart';

class NotificationHelper {
  static Future<void> initialize(
      FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin) async {
    var androidInitialize =
        const AndroidInitializationSettings('@mipmap/ic_launcher');
    var initializationsSettings =
        InitializationSettings(android: androidInitialize);
    flutterLocalNotificationsPlugin.initialize(initializationsSettings);
  }

  static initializeNotification() {
    //todo foreground state
    FirebaseMessaging.instance.getInitialMessage();
    FirebaseMessaging.onMessage.listen((RemoteMessage message) async {
      RemoteNotification? notification = message.notification;
      if (notification != null) {
        flutterLocalNotificationsPlugin.show(
            notification.hashCode,
            notification.title,
            notification.body,
            const NotificationDetails(
                android: AndroidNotificationDetails(
                    'channel-Id-N2', 'channel-Name-N2',
                    channelDescription: 'Channel - description',
                    importance: Importance.max,
                    playSound: true,
                    priority: Priority.max,
                    visibility: NotificationVisibility.public,
                    ticker: 'ticker')));
      }
    });

    // todo App is open but not terminated
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      if (message.notification != null) {}
    });

    //todo when the app is terminated
    FirebaseMessaging.instance.getInitialMessage().then((message) {
      if (message != null) {}
    });
  }
}
