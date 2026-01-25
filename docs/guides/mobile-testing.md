# 📱 Mobile Automated Testing Guide

This guide explains how to run headless E2E tests on an Android Emulator using **Maestro**.

## 🛠 Prerequisites

Ensure you have the following installed via `mise` and system packages:

- **Java 17**: `mise use java@17`
- **Android SDK**: `mise use android-sdk@latest`
- **Maestro CLI**: `curl -Ls "https://get.maestro.mobile.dev" | bash`
- **System dependencies**: `go-yq` (AUR) for the `android-sdk` mise plugin.

---

## 🚀 Step 1: Start the Emulator

In a dedicated terminal, start the emulator. The first launch after a `-wipe-data` will take ~2 minutes.

### Headless (for CI/Scripts)
```bash
emulator -avd Kitchen_Emulator -no-window -no-audio -no-boot-anim -no-snapshot -wipe-data -gpu swiftshader_indirect
```

### With Window (for Debugging)
```bash
emulator -avd Kitchen_Emulator -no-boot-anim -no-snapshot -wipe-data -gpu swiftshader_indirect
```

---

## 🏗 Step 2: Build & Install the App

Once the emulator is running, open a **new terminal** to build the debug APK.

### Build the APK
```bash
cd src/mobile/android
./gradlew assembleDebug
cd ../../../
```

### Verify Emulator Connection
```bash
adb devices -l
```
*If empty, run: `adb kill-server && adb start-server`.*

### Install to Emulator
```bash
adb -s emulator-5554 install src/mobile/android/app/build/outputs/apk/debug/app-debug.apk
```

---

## 🧪 Step 3: Run Maestro Tests

Run the smoke test flow defined in `tests/mobile/flows/smoke.yaml`.

```bash
export PATH="$PATH:$HOME/.maestro/bin"
maestro test tests/mobile/flows/smoke.yaml --device emulator-5554
```

---

## 🔍 Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **`adb devices` is empty** | Run `adb connect localhost:5555`. |
| **Gradle fails: "node not found"** | Ensure you are in a shell where `node` is in the PATH (run `mise reshim`). |
| **Maestro: "0 devices connected"** | Ensure `adb devices` shows `emulator-5554` as `device` (not `offline` or `unauthorized`). |
| **Emulator hangs on boot** | Kill it (`pkill -9 emulator`) and restart with `-wipe-data`. |

## 📝 Test Flows
Test flows are located in `tests/mobile/flows/*.yaml`. 
To add a new test, follow the [Maestro Documentation](https://maestro.mobile.dev/reference/commands).
