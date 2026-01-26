import threading
import webbrowser
from time import sleep
from waitress import serve
from kivy.utils import platform as kivy_platform
from app import app as flask_app


# Desktop mode
if kivy_platform != "android":
    def start_flask():
        serve(flask_app, host="127.0.0.1", port=8080)

    threading.Thread(target=start_flask, daemon=True).start()

    webbrowser.open("http://127.0.0.1:8080")

    while True:
        sleep(1)

# Android mode
else:
    import requests
    from kivy.app import App
    from kivy.uix.label import Label
    from kivy.clock import Clock
    from jnius import autoclass, PythonJavaClass, java_method, cast
    from android.permissions import request_permissions, Permission
    from android import activity
    from app import app as flask_app


    # Permissions
    request_permissions([
        Permission.CAMERA,
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE,
        "android.permission.READ_MEDIA_IMAGES"
    ])


    # Java classes
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    WebView = autoclass("android.webkit.WebView")
    WebViewClient = autoclass("android.webkit.WebViewClient")
    WebChromeClient = autoclass("android.webkit.WebChromeClient")
    Intent = autoclass("android.content.Intent")
    LayoutParams = autoclass("android.view.ViewGroup$LayoutParams")
    Uri = autoclass('android.net.Uri')
    ArrayList = autoclass("java.util.ArrayList")


    # Globals    
    FILE_PICKER_CODE = 1001
    PORT = 5000
    chrome = None
    webview_instance = None
    back_key_listener = None


    # Start flask server
    def start_flask():
        serve(flask_app, host="127.0.0.1", port=PORT)

    threading.Thread(target=start_flask, daemon=True).start()


    # Custom WebChromeClient
    LeafLogChromeClient = autoclass("org.test.leaflog.LeafLogChromeClient")


    # Handle activity result
    def on_activity_result(request_code, result_code, intent):
        global webview_instance
        
        if webview_instance is None:
            return
        
        chrome_base = webview_instance.getWebChromeClient()
        chrome = cast("org.test.leaflog.LeafLogChromeClient", chrome_base)

        if chrome is None:
            return

        if request_code != FILE_PICKER_CODE:
            return

        if LeafLogChromeClient.fileCallback is None:
            return

        if result_code != -1 or intent is None:
            LeafLogChromeClient.fileCallback.onReceiveValue(None)
            LeafLogChromeClient.fileCallback = None
            return

        uris = []
        has_clip = intent.getClipData() is not None
        has_data = intent.getData() is not None
        camera_uri = chrome.getCameraImageUri()
        
        if has_clip:
            clip = intent.getClipData()
            if clip:
                for i in range(clip.getItemCount()):
                    uris.append(clip.getItemAt(i).getUri())
        elif has_data:
            uris.append(intent.getData())
        elif camera_uri is not None:
            java_list = ArrayList()
            java_list.add(cast("android.net.Uri", camera_uri))
            chrome.sendUrisToCallback(java_list)

            LeafLogChromeClient.fileCallback = None
            LeafLogChromeClient.cameraImageUri = None
            return

        if not uris:
            LeafLogChromeClient.fileCallback.onReceiveValue(None)
            LeafLogChromeClient.fileCallback = None
            return

        java_list = ArrayList()
        for uri in uris:
            java_list.add(cast("android.net.Uri", uri))

        chrome.sendUrisToCallback(java_list)
        LeafLogChromeClient.fileCallback = None


    # Bind the activity result handler
    activity.bind(on_activity_result=on_activity_result)
 

    # Listen for back presses
    class BackPressListener(PythonJavaClass):
        __javainterfaces__ = ["android/view/View$OnKeyListener"]
        __javacontext__ = "app"

        @java_method("(Landroid/view/View;ILandroid/view/KeyEvent;)Z")
        def onKey(self, view, keyCode, event):
            KEYCODE_BACK = 4
            ACTION_UP = 1

            if event is None:
                return False

            if keyCode == KEYCODE_BACK and event.getAction() == ACTION_UP:
                if webview_instance and webview_instance.canGoBack():
                    webview_instance.goBack()
                    return True

            return False


    # Create WebView
    class WebViewRunnable(PythonJavaClass):
        __javainterfaces__ = ["java/lang/Runnable"]

        def __init__(self, callback):
            super().__init__()
            self.callback = callback

        @java_method("()V")
        def run(self):
            self.callback()


    def create_webview():
        global chrome
        global webview_instance
        activity = PythonActivity.mActivity
        webview = WebView(activity)
        webview_instance = webview

        settings = webview.getSettings()
        settings.setJavaScriptEnabled(True)
        settings.setDomStorageEnabled(True)
        settings.setAllowFileAccess(True)
        settings.setAllowContentAccess(True)
        settings.setAllowUniversalAccessFromFileURLs(True)

        webview.setWebViewClient(WebViewClient())
        chrome = LeafLogChromeClient(PythonActivity.mActivity)
        webview.setWebChromeClient(chrome)

        webview_instance.setOnKeyListener(BackPressListener())

        webview.setFocusableInTouchMode(True)
        webview.requestFocus()

        activity.addContentView(webview, LayoutParams(-1, -1))

        webview.loadUrl(f"http://127.0.0.1:{PORT}")
        webview.requestFocus()
        


    # Wait for Flask then launch WebView
    def poll_flask(callback):
        def check(dt):
            try:
                r = requests.get(f"http://127.0.0.1:{PORT}", timeout=1)
                if r.status_code in (200, 302):
                    callback()
                    return False
            except:
                pass
            return True

        Clock.schedule_interval(check, 0.5)


    # Kivy app wrapper
    class LeafLogApp(App):
        def build(self):
            return Label(text="Starting LeafLog...")

        def on_start(self):
            poll_flask(self.launch_webview)

        def launch_webview(self):
            runnable = WebViewRunnable(create_webview)
            PythonActivity.mActivity.runOnUiThread(runnable)


    # Run this thing
    LeafLogApp().run()
    