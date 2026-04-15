# CureBay Flutter App — Conversion Guide

## Overview

Converting CureBay from a FastAPI web backend to a Flutter mobile app (Android APK).
The problem statement recommends **Option A: Android APK** as the primary deliverable.

---

## Architecture Decision

### Current: Web Backend + Browser UI
```
Browser ──── HTTP ──── FastAPI (Python) ──── MedGemma GGUF
                              ├── ChromaDB (RAG)
                              ├── SQLite (DB)
                              └── EfficientNet (Images)
```

### Flutter Target: Two Deployment Options

**Option A — Flutter + Embedded Python (Recommended for Hackathon)**
```
Flutter App (Dart/UI)
  ├── REST calls to → FastAPI backend (running on same device via Chaquopy / background service)
  └── OR calls to → Remote backend (if WiFi available)
```

**Option B — Flutter with Tflite/ONNX (Fully Embedded)**
```
Flutter App (Dart)
  ├── TFLite / ONNX model (for inference)
  ├── SQLite via sqflite package
  └── Audio via flutter_sound
```

---

## Major Changes Required

### 1. Flutter Project Structure
```
curebay_flutter/
├── android/
├── ios/                    # Optional
├── lib/
│   ├── main.dart
│   ├── models/
│   │   ├── patient.dart
│   │   ├── assessment.dart
│   │   └── user.dart
│   ├── services/
│   │   ├── api_service.dart      # HTTP client (http package)
│   │   ├── auth_service.dart     # JWT storage (flutter_secure_storage)
│   │   ├── db_service.dart       # Local SQLite (sqflite)
│   │   └── audio_service.dart    # Voice recording (flutter_sound)
│   ├── screens/
│   │   ├── login_screen.dart
│   │   ├── dashboard_screen.dart
│   │   ├── patients_screen.dart
│   │   ├── assessment_screen.dart
│   │   └── history_screen.dart
│   └── widgets/
│       ├── risk_badge.dart
│       ├── condition_card.dart
│       └── vitals_input.dart
├── pubspec.yaml
└── assets/
    └── models/             # TFLite models if embedded
```

### 2. Key Flutter Packages

```yaml
# pubspec.yaml dependencies
dependencies:
  flutter:
    sdk: flutter

  # HTTP & API
  http: ^1.2.0
  dio: ^5.4.0              # Better HTTP with interceptors

  # State Management
  provider: ^6.1.0         # Or riverpod / bloc

  # Local Database (replaces SQLite + ChromaDB)
  sqflite: ^2.3.3
  path_provider: ^2.1.2

  # Auth
  flutter_secure_storage: ^9.0.0   # JWT token storage

  # Voice Input (replaces Sarvam + IndicConformer)
  speech_to_text: ^6.6.0           # Device STT (offline, 20+ Indian languages on Android)
  flutter_sound: ^9.2.13           # Audio recording for server-side STT

  # Image
  image_picker: ^1.0.7             # Camera + gallery
  camera: ^0.11.0                  # Live camera for rPPG

  # ML Models (replaces llama-cpp-python + torchvision)
  tflite_flutter: ^0.10.4          # TFLite for image classification
  # NOTE: LLM runs on backend; TFLite handles image preprocessing only

  # UI
  google_fonts: ^6.1.0
  flutter_animate: ^4.5.0
  lottie: ^3.1.0

  # Utils
  intl: ^0.19.0
  shared_preferences: ^2.2.3
  permission_handler: ^11.3.0
  connectivity_plus: ^6.0.3        # Offline detection
```

### 3. Backend Strategy for Flutter

**For Hackathon Demo (Quickest Path):**
Run the existing FastAPI backend on a laptop/server, point Flutter to it.

```dart
// lib/services/api_service.dart
class ApiService {
  // In demo: point to your laptop's IP
  static const String baseUrl = 'http://192.168.1.x:8000';
  // In production: embedded Python via localhost
  // static const String baseUrl = 'http://localhost:8000';
  
  static String? _token;
  
  static Future<Map> assess(Map payload) async {
    final r = await http.post(
      Uri.parse('$baseUrl/assessment/text'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $_token',
      },
      body: jsonEncode(payload),
    );
    return jsonDecode(r.body);
  }
}
```

**For Production (Offline APK):**
Use [Chaquopy](https://chaquo.com/chaquopy/) to embed Python in Android:

```groovy
// android/build.gradle
plugins {
    id 'com.chaquo.python' version '15.0.1' apply false
}

// android/app/build.gradle
android {
    python {
        pip { install "fastapi", "uvicorn", "llama-cpp-python", ... }
        pyc { src false }
    }
}
```

Then start the backend on app launch:
```dart
// lib/services/python_service.dart
import 'package:chaquopy/chaquopy.dart';

class PythonService {
  static Future<void> startBackend() async {
    await Chaquopy.getInstance().executeCode('''
      import subprocess, threading
      def run():
          subprocess.run(["uvicorn", "main:app", "--port", "8765"])
      threading.Thread(target=run, daemon=True).start()
    ''');
  }
}
```

### 4. Voice Input in Flutter

The `speech_to_text` package supports Android's offline STT with 20+ Indian languages:

```dart
// lib/services/voice_service.dart
import 'package:speech_to_text/speech_to_text.dart';

class VoiceService {
  final _speech = SpeechToText();
  String transcript = '';
  
  Future<bool> initialize() async {
    return await _speech.initialize(
      onError: (e) => print('STT error: $e'),
    );
  }
  
  Future<void> listen(String languageCode) async {
    if (!await initialize()) return;
    
    // languageCode: 'hi-IN', 'or-IN', 'ta-IN', 'te-IN', etc.
    await _speech.listen(
      onResult: (result) => transcript = result.recognizedWords,
      localeId: languageCode,
    );
  }
  
  Future<void> stop() async => await _speech.stop();
}
```

### 5. Image Assessment in Flutter

```dart
// lib/screens/assessment_screen.dart (image mode)
import 'package:image_picker/image_picker.dart';

Future<void> pickAndAssessImage() async {
  final picker = ImagePicker();
  final XFile? image = await picker.pickImage(
    source: ImageSource.camera,  // or ImageSource.gallery
    maxWidth: 1024,
    imageQuality: 85,
  );
  
  if (image == null) return;
  
  // Send to backend
  final request = http.MultipartRequest(
    'POST', Uri.parse('${ApiService.baseUrl}/assessment/image'),
  );
  request.files.add(await http.MultipartFile.fromPath('image_file', image.path));
  request.fields['patient_id'] = selectedPatientId;
  request.headers['Authorization'] = 'Bearer ${ApiService.token}';
  
  final response = await request.send();
  final body = await response.stream.bytesToString();
  final result = jsonDecode(body);
  // Show results...
}
```

### 6. Offline Database in Flutter

Replace SQLite+ChromaDB with sqflite:

```dart
// lib/services/db_service.dart
import 'package:sqflite/sqflite.dart';

class DbService {
  static Database? _db;
  
  static Future<Database> get db async {
    _db ??= await openDatabase(
      join(await getDatabasesPath(), 'curebay.db'),
      version: 1,
      onCreate: (db, v) async {
        await db.execute('''
          CREATE TABLE patients (
            id TEXT PRIMARY KEY, name TEXT, age INTEGER,
            gender TEXT, phone TEXT, village TEXT,
            district TEXT, known_conditions TEXT
          )
        ''');
        await db.execute('''
          CREATE TABLE assessments (
            id TEXT PRIMARY KEY, patient_id TEXT,
            symptoms_text TEXT, risk_level TEXT,
            risk_reason TEXT, possible_conditions TEXT,
            next_steps TEXT, confidence REAL, created_at TEXT
          )
        ''');
      },
    );
    return _db!;
  }
  
  // Sync with backend when online
  static Future<void> syncWithBackend() async {
    final isOnline = await ConnectivityService.isConnected();
    if (!isOnline) return;
    // Pull latest from backend...
  }
}
```

### 7. Offline-First Strategy

```dart
// lib/services/connectivity_service.dart
import 'package:connectivity_plus/connectivity_plus.dart';

class ConnectivityService {
  static Future<bool> isConnected() async {
    final result = await Connectivity().checkConnectivity();
    return result != ConnectivityResult.none;
  }
  
  static Stream<bool> get onConnectivityChanged =>
    Connectivity().onConnectivityChanged
      .map((r) => r != ConnectivityResult.none);
}

// In assessment_service.dart:
Future<Map> runAssessment(Map payload) async {
  if (await ConnectivityService.isConnected()) {
    // Use backend (full LLM)
    return await ApiService.assess(payload);
  } else {
    // Use embedded lightweight model
    return await LocalInferenceService.assess(payload);
  }
}
```

---

## Recommended Build Steps

### Step 1: Create Flutter project
```bash
flutter create curebay_app
cd curebay_app
```

### Step 2: Add dependencies to pubspec.yaml
Copy the dependencies listed above.

### Step 3: Build UI screens
Port the HTML/CSS UI to Flutter widgets. The design system maps cleanly:
- Cards → `Card` widget
- Buttons → `ElevatedButton` / `OutlinedButton`
- Forms → `TextFormField`
- Color scheme → `ThemeData`

### Step 4: Wire up API calls
Point `ApiService.baseUrl` to the running FastAPI server.

### Step 5: Add voice support
Initialize `speech_to_text` with Indian language locales.

### Step 6: Build APK
```bash
flutter build apk --release
# Output: build/app/outputs/flutter-apk/app-release.apk
```

---

## Timeline Estimate (Hackathon)

| Task | Time |
|------|------|
| Flutter project setup + dependencies | 1h |
| Auth screens (login/register) | 2h |
| Patient CRUD screens | 2h |
| Assessment screen (text + voice) | 3h |
| Results rendering | 2h |
| Image assessment | 1h |
| History + offline caching | 2h |
| APK build + testing | 1h |
| **Total** | **~14h** |

---

## Quick Start (Demo without full Flutter)

For the hackathon demo, the **fastest path** is:
1. Run FastAPI backend on a laptop
2. Open `http://LAPTOP_IP:8000` on an Android phone browser
3. The web UI works on mobile browsers too
4. For APK: wrap in WebView Flutter app (1-2 hours):

```dart
// lib/main.dart (WebView approach - fastest APK)
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

void main() => runApp(const CureBayApp());

class CureBayApp extends StatelessWidget {
  const CureBayApp({super.key});
  
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CureBay',
      home: Scaffold(
        body: WebViewWidget(
          controller: WebViewController()
            ..loadRequest(Uri.parse('http://YOUR_SERVER_IP:8000')),
        ),
      ),
    );
  }
}
```

This gets you a working APK in 30 minutes while building the full native app.
