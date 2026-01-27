# LeafLog
LeafLog is a locally-run web-based plant growth journal for Android and Desktop. This app is written in Python with Flask and Kivy.

# How it works
When you run LeafLog, it will launch a Flask server at 127.0.0.1 (port 8080 on desktop, port 5000 on mobile). The app will then connect to the server through webview if on mobile, or through your default browser on desktop.

From there, it's a basic journaling app. Open the side menu, add a plant, and get growing!

This app runs 100% locally on your Android device or PC. That means no data is collected or sent to anyone or anywhere.

# How to run it
Android - just download the APK from [Releases](https://github.com/AphelionWasTaken/LeafLog/releases/latest). Since this is an unsigned debug APK, you will need to enable sideloading apps on your device.

Desktop - Run main.py with python. You'll need the following modules: kivy, Flask, Flask-SQLAlchemy, and waitress.

# How to build it
I hope I haven't forgotten anything...

To build the APK, you'll need to use a Linux system or WSL. I'd recommend setting up a Python 3.9 venv (feel free to try to get it to work with whatever version you'd like).

- `python3.9 -m venv {your venv name here}`
- `source {your venv name here}/bin/activate`

In that environment, you'll need to install the following modules with pip: setuptools, wheel, cython=0.29.36, buildozer, appdirs, packaging, and python-for-android.

I believe you'll also need the following: openjdk-17-jdk, zlib1g-dev, libncurses5-dev, libncursesw5-dev (I apparently ran `sudo apt install -y git unzip openjdk-17-jdk zlib1g-dev libncurses5-dev libncursesw5-dev python3-pip wget`).

Run `buildozer android clean` to generate the necessary buildozer files.

Navigate to .buildozer\android\platform\python-for-android\pythonforandroid\bootstraps\sdl2\build\templates and edit AndroidManifest.tmpl.xml (feel free to try to get XML injection working via buildozer.spec instead).

Inside of the `<application>` tag, paste `android:usesCleartextTraffic="true"`

Also inside of `<application>`, paste the following block of XML:
```XML
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="org.test.leaflog.fileprovider"
    android:exported="false"
    android:grantUriPermissions="true">
    <meta-data
        android:name="android.support.FILE_PROVIDER_PATHS"
        android:resource="@xml/provider_paths"/>
</provider>
```
it should look like the following screenshot:

<img width="611" height="619" alt="image" src="https://github.com/user-attachments/assets/4583f6d0-106a-4c0c-a3e1-8e32f9037b31" />

Save the file and run `buildozer android debug` to build the APK.

# Screenshots
All screenshots are from Android Studio, as I ironically do not own an Android device yet!

<img width="236" height="532" alt="image" src="https://github.com/user-attachments/assets/057aaecb-38d3-4956-89cf-0f712f41b5c1" />
<img width="236" height="532" alt="image" src="https://github.com/user-attachments/assets/c5247462-9d33-4494-b236-e07a0f3e5ca4" />
<img width="236" height="532" alt="image" src="https://github.com/user-attachments/assets/615159ff-5acc-491e-8727-3b7bf57db230" />

