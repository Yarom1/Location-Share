package com.locationshare

import android.Manifest
import android.annotation.SuppressLint
import android.content.Intent
import android.content.pm.PackageManager
import android.location.LocationManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.webkit.*
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private val LOCATION_PERMISSION_CODE = 1001
    private val BACKGROUND_LOCATION_CODE = 1002
    private val FILE_CHOOSER_CODE = 1003
    private var filePathCallback: ValueCallback<Array<Uri>>? = null
    private var cameraUri: Uri? = null
    private var waitingForLocationEnable = false

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)

        CookieManager.getInstance().apply {
            setAcceptCookie(true)
            setAcceptThirdPartyCookies(webView, true)
            flush()
        }

        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            allowFileAccess = true
            allowContentAccess = true
            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
            cacheMode = WebSettings.LOAD_DEFAULT
            javaScriptCanOpenWindowsAutomatically = true
            setSupportZoom(true)
            builtInZoomControls = false
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onGeolocationPermissionsShowPrompt(
                origin: String, callback: GeolocationPermissions.Callback
            ) { callback.invoke(origin, true, true) }

            override fun onPermissionRequest(request: PermissionRequest) {
                request.grant(request.resources)
            }

            override fun onShowFileChooser(
                webView: WebView?,
                filePath: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                filePathCallback?.onReceiveValue(null)
                filePathCallback = filePath

                // יצור קובץ זמני למצלמה
                val photoFile = File(cacheDir, "profile_photo_${System.currentTimeMillis()}.jpg")
                cameraUri = FileProvider.getUriForFile(
                    this@MainActivity,
                    "com.locationshare.fileprovider",
                    photoFile
                )

                // Intent למצלמה
                val cameraIntent = Intent(android.provider.MediaStore.ACTION_IMAGE_CAPTURE).apply {
                    putExtra(android.provider.MediaStore.EXTRA_OUTPUT, cameraUri)
                }

                // Intent לגלריה
                val galleryIntent = Intent(Intent.ACTION_PICK).apply {
                    type = "image/*"
                }

                // chooser
                val chooser = Intent.createChooser(galleryIntent, "בחר תמונה")
                chooser.putExtra(Intent.EXTRA_INITIAL_INTENTS, arrayOf(cameraIntent))

                startActivityForResult(chooser, FILE_CHOOSER_CODE)
                return true
            }

            override fun onConsoleMessage(msg: ConsoleMessage): Boolean {
                android.util.Log.d("WebView", "${msg.message()} [${msg.sourceId()}:${msg.lineNumber()}]")
                return true
            }
        }

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url = request?.url?.toString() ?: return false
                val isNavLink = url.startsWith("geo:") ||
                        url.startsWith("waze:") ||
                        url.contains("waze.com") ||
                        url.contains("maps.google.com") ||
                        url.contains("google.com/maps")
                if (isNavLink) {
                    try {
                        // השתמש ב-geo: URI כדי לקבל את תפריט הבחירה הטבעי של אנדרואיד
                        val geoUri = if (url.startsWith("geo:")) {
                            Uri.parse(url)
                        } else {
                            val regex = Regex("[-.0-9]+,[-.0-9]+")
                            val match = regex.find(url)
                            val coords = match?.value ?: ""
                            Uri.parse("geo:0,0?q=$coords")
                        }
                        val intent = Intent(Intent.ACTION_VIEW, geoUri)
                        val chooser = Intent.createChooser(intent, "נווט עם")
                        chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                        startActivity(chooser)
                    } catch (e: Exception) {
                        Toast.makeText(this@MainActivity, "לא נמצאה אפליקציית ניווט", Toast.LENGTH_SHORT).show()
                    }
                    return true
                }
                return false
            }
        }

        LocationService.onLocationUpdate = { lat, lng ->
            runOnUiThread {
                webView.evaluateJavascript(
                    "if(window.onBackgroundLocation)window.onBackgroundLocation($lat,$lng);", null
                )
            }
        }

        requestLocationPermissions()
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == FILE_CHOOSER_CODE) {
            if (resultCode == RESULT_OK) {
                val results = when {
                    data?.data != null -> arrayOf(data.data!!)
                    cameraUri != null -> arrayOf(cameraUri!!)
                    else -> null
                }
                filePathCallback?.onReceiveValue(results)
            } else {
                filePathCallback?.onReceiveValue(null)
            }
            filePathCallback = null
            cameraUri = null
        }
    }

    private fun requestLocationPermissions() {
        val permissions = mutableListOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.CAMERA
        )
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        val notGranted = permissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (notGranted.isEmpty()) requestBackgroundLocation()
        else ActivityCompat.requestPermissions(this, notGranted.toTypedArray(), LOCATION_PERMISSION_CODE)
    }

    private fun requestBackgroundLocation() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            if (ContextCompat.checkSelfPermission(this,
                    Manifest.permission.ACCESS_BACKGROUND_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                    arrayOf(Manifest.permission.ACCESS_BACKGROUND_LOCATION),
                    BACKGROUND_LOCATION_CODE)
                return
            }
        }
        checkLocationEnabledAndProceed()
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        when (requestCode) {
            LOCATION_PERMISSION_CODE -> requestBackgroundLocation()
            BACKGROUND_LOCATION_CODE -> checkLocationEnabledAndProceed()
        }
    }

    private fun isLocationEnabled(): Boolean {
        val lm = getSystemService(LOCATION_SERVICE) as LocationManager
        return lm.isProviderEnabled(LocationManager.GPS_PROVIDER) ||
                lm.isProviderEnabled(LocationManager.NETWORK_PROVIDER)
    }

    private fun checkLocationEnabledAndProceed() {
        if (isLocationEnabled()) {
            waitingForLocationEnable = false
            startLocationServiceAndLoad()
        } else {
            waitingForLocationEnable = true
            AlertDialog.Builder(this)
                .setTitle("שירותי מיקום כבויים")
                .setMessage("כדי להשתמש באפליקציה יש להפעיל את שירותי המיקום (GPS) במכשיר.")
                .setCancelable(false)
                .setPositiveButton("פתח הגדרות") { _, _ ->
                    startActivity(Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS))
                }
                .show()
        }
    }

    private fun startLocationServiceAndLoad() {
        val serviceIntent = Intent(this, LocationService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent)
        } else {
            startService(serviceIntent)
        }
        loadApp()
    }

    private fun loadApp() {
        webView.loadUrl("file:///android_asset/index.html")
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }

    override fun onResume() {
        super.onResume()
        webView.onResume()
        if (waitingForLocationEnable && isLocationEnabled()) {
            waitingForLocationEnable = false
            startLocationServiceAndLoad()
        }
    }
    override fun onPause() { super.onPause(); webView.onPause() }
}
