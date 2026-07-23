package com.locationshare

import android.app.*
import android.content.Intent
import android.location.*
import android.os.*
import androidx.core.app.NotificationCompat
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.*

class LocationService : Service() {

    private lateinit var locationManager: LocationManager
    private var webViewRef: android.webkit.WebView? = null
    private var wakeLock: PowerManager.WakeLock? = null
    private val CHANNEL_ID = "location_channel"
    private val NOTIF_ID = 1
    private val PROJECT_ID = "locationshare-38792"
    private var cachedIdToken: String? = null
    private var idTokenExpiryMillis: Long = 0L
    private var lastWriteTimeMillis: Long = 0L
    private var lastKnownLat: Double? = null
    private var lastKnownLng: Double? = null
    private val heartbeatHandler = Handler(Looper.getMainLooper())
    private val heartbeatIntervalMs = 60_000L
    private val heartbeatRunnable = object : Runnable {
        override fun run() {
            val lat = lastKnownLat
            val lng = lastKnownLng
            if (lat != null && lng != null) {
                writeLocationToFirestore(lat, lng)
            }
            heartbeatHandler.postDelayed(this, heartbeatIntervalMs)
        }
    }

    companion object {
        var instance: LocationService? = null
        var onLocationUpdate: ((Double, Double) -> Unit)? = null
    }

    override fun onCreate() {
        super.onCreate()
        instance = this
        createNotificationChannel()
        startForeground(NOTIF_ID, buildNotification())
        acquireWakeLock()
        startLocationUpdates()
        heartbeatHandler.postDelayed(heartbeatRunnable, heartbeatIntervalMs)
    }

    private fun acquireWakeLock() {
        try {
            val pm = getSystemService(POWER_SERVICE) as PowerManager
            wakeLock = pm.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK,
                "LocationShare::LocationWakeLock"
            ).apply {
                setReferenceCounted(false)
                acquire(12 * 60 * 60 * 1000L) // safety timeout: 12h, renewed by service restarts
            }
        } catch (e: Exception) { e.printStackTrace() }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID, "Location Sharing",
                NotificationManager.IMPORTANCE_LOW
            ).apply { description = "Sharing your location" }
            getSystemService(NotificationManager::class.java)
                .createNotificationChannel(channel)
        }
    }

    private fun buildNotification(): Notification {
        val intent = Intent(this, MainActivity::class.java)
        val pi = PendingIntent.getActivity(this, 0, intent,
            PendingIntent.FLAG_IMMUTABLE)
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Location Share")
            .setContentText("משתף מיקום ברקע")
            .setSmallIcon(android.R.drawable.ic_menu_mylocation)
            .setContentIntent(pi)
            .setOngoing(true)
            .build()
    }

    private fun startLocationUpdates() {
        locationManager = getSystemService(LOCATION_SERVICE) as LocationManager
        try {
            locationManager.requestLocationUpdates(
                LocationManager.GPS_PROVIDER, 10000L, 5f,
                object : LocationListener {
                    override fun onLocationChanged(loc: Location) {
                        lastKnownLat = loc.latitude
                        lastKnownLng = loc.longitude
                        onLocationUpdate?.invoke(loc.latitude, loc.longitude)
                        writeLocationToFirestore(loc.latitude, loc.longitude)
                    }
                    override fun onStatusChanged(p: String?, s: Int, e: Bundle?) {}
                    override fun onProviderEnabled(p: String) {}
                    override fun onProviderDisabled(p: String) {}
                }
            )
        } catch (e: SecurityException) { e.printStackTrace() }
    }

    private fun updateNotificationText(text: String) {
        try {
            val notification = NotificationCompat.Builder(this, CHANNEL_ID)
                .setContentTitle("Location Share")
                .setContentText(text)
                .setSmallIcon(android.R.drawable.ic_menu_mylocation)
                .setOngoing(true)
                .build()
            getSystemService(NotificationManager::class.java).notify(NOTIF_ID, notification)
        } catch (e: Exception) { e.printStackTrace() }
    }

    private fun getFreshIdToken(): String? {
        val now = System.currentTimeMillis()
        if (cachedIdToken != null && now < idTokenExpiryMillis) return cachedIdToken

        val prefs = getSharedPreferences("location_share_prefs", MODE_PRIVATE)
        val refreshToken = prefs.getString("refresh_token", null) ?: return null
        val apiKey = prefs.getString("api_key", null) ?: return null

        return try {
            val url = URL("https://securetoken.googleapis.com/v1/token?key=$apiKey")
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded")
            conn.doOutput = true
            val body = "grant_type=refresh_token&refresh_token=$refreshToken"
            conn.outputStream.use { it.write(body.toByteArray()) }
            if (conn.responseCode == 200) {
                val response = conn.inputStream.bufferedReader().use { it.readText() }
                val json = JSONObject(response)
                val idToken = json.getString("id_token")
                val expiresIn = json.getString("expires_in").toLong()
                cachedIdToken = idToken
                idTokenExpiryMillis = now + (expiresIn - 60) * 1000L
                conn.disconnect()
                idToken
            } else {
                val err = conn.errorStream?.bufferedReader()?.use { it.readText() }
                updateNotificationText("⚠️ שגיאת טוקן (${conn.responseCode}): ${err ?: ""}")
                conn.disconnect()
                null
            }
        } catch (e: Exception) {
            updateNotificationText("⚠️ שגיאת רננון טוקן: ${e.message}")
            null
        }
    }

    private fun writeLocationToFirestore(lat: Double, lng: Double) {
        Thread {
            try {
                val prefs = getSharedPreferences("location_share_prefs", MODE_PRIVATE)
                val uid = prefs.getString("uid", null)
                if (uid == null) { updateNotificationText("⚠️ אין UID שמור - פתח את האפליקציה"); return@Thread }
                val groupId = prefs.getString("active_group_id", null)
                if (groupId.isNullOrEmpty()) { updateNotificationText("ללא קבוצה פעילה - אין מה לעדכן"); return@Thread }

                val idToken = getFreshIdToken()
                if (idToken == null) { return@Thread }

                val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.US)
                sdf.timeZone = TimeZone.getTimeZone("UTC")
                val timestamp = sdf.format(Date())

                val docPath = "projects/$PROJECT_ID/databases/(default)/documents/groups/$groupId/locations/$uid"

                val fields = JSONObject().apply {
                    put("lat", JSONObject().put("doubleValue", lat))
                    put("lng", JSONObject().put("doubleValue", lng))
                    put("online", JSONObject().put("booleanValue", true))
                    put("lastSeen", JSONObject().put("timestampValue", timestamp))
                }

                val write = JSONObject().apply {
                    put("update", JSONObject().apply {
                        put("name", docPath)
                        put("fields", fields)
                    })
                    put("updateMask", JSONObject().apply {
                        put("fieldPaths", org.json.JSONArray(listOf("lat", "lng", "online", "lastSeen")))
                    })
                }

                val bodyJson = JSONObject().apply {
                    put("writes", org.json.JSONArray().put(write))
                }

                val urlStr = "https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents:commit"
                val url = URL(urlStr)
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json")
                conn.setRequestProperty("Authorization", "Bearer $idToken")
                conn.doOutput = true
                conn.outputStream.use { it.write(bodyJson.toString().toByteArray()) }
                val code = conn.responseCode
                if (code !in 200..299) {
                    val err = conn.errorStream?.bufferedReader()?.use { it.readText() }
                    updateNotificationText("⚠️ כשלון כתיבה ($code): ${err?.take(80) ?: ""}")
                } else {
                    val nowMillis = System.currentTimeMillis()
                    val gapText = if (lastWriteTimeMillis == 0L) " | אתחול מחדש" else {
                        val gapSec = (nowMillis - lastWriteTimeMillis) / 1000
                        " | מרווח מעודכון קודם: ${gapSec}ש'"
                    }
                    lastWriteTimeMillis = nowMillis
                    val now = SimpleDateFormat("HH:mm:ss", Locale.US).format(Date())
                    updateNotificationText("✅ עודכן ב-$now$gapText")
                }
                conn.disconnect()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        instance = null
        locationManager.removeUpdates {}
        heartbeatHandler.removeCallbacks(heartbeatRunnable)
        try { if (wakeLock?.isHeld == true) wakeLock?.release() } catch (e: Exception) { e.printStackTrace() }
    }
}
