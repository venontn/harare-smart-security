# HSUSMS Citizen Mobile App (Flutter)

Citizen-facing mobile app for the Harare Smart Urban Security System.

## Features

- **Emergency panic button** — high-priority alert to command center
- **Incident reporting** — crime, theft, traffic, vandalism
- **Public alerts** — view active city safety notifications
- **GPS location** — auto-attaches coordinates to reports

## Prerequisites

1. [Flutter SDK](https://docs.flutter.dev/get-started/install) installed
2. HSUSMS backend running (`..\..\run.ps1`)

## Configure API URL

Edit `lib/services/api_service.dart`:

| Environment | baseUrl |
|---------------|---------|
| Windows / iOS Simulator | `http://127.0.0.1:8000/api` |
| Android Emulator | `http://10.0.2.2:8000/api` |
| Physical phone | `http://<YOUR_PC_IP>:8000/api` |

## Run

```powershell
cd mobile\hsusms_citizen
flutter pub get
flutter run
```

## Android permissions

Location permission is requested at runtime for GPS reports. Add to `android/app/src/main/AndroidManifest.xml` if building release:

```xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
<uses-permission android:name="android.permission.INTERNET"/>
```

## iOS

Add to `ios/Runner/Info.plist`:

```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>Location is used to send accurate incident reports to Harare security services.</string>
```

Run `flutter create .` once if platform folders are missing.
