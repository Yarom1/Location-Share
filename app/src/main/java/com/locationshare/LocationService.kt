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
                conn.disconnect()
                null
            }
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    private fun writeLocationToFirestore(lat: Double, lng: Double) {
        Thread {
            try {
                val prefs = getSharedPreferences("location_share_prefs", MODE_PRIVATE)
                val uid = prefs.getString("uid", null) ?: return@Thread
                val groupId = prefs.getString("active_group_id", null)
                if (groupId.isNullOrEmpty()) return@Thread

                val idToken = getFreshIdToken() ?: return@Thread

                val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.US)
                sdf.timeZone = TimeZone.getTimeZone("UTC")
                val timestamp = sdf.format(Date())

                val bodyJson = JSONObject().apply {
                    put("fields", JSONObject().apply {
                        put("lat", JSONObject().put("doubleValue", lat))
                        put("lng", JSONObject().put("doubleValue", lng))
                        put("online", JSONObject().put("booleanValue", true))
                        put("lastSeen", JSONObject().put("timestampValue", timestamp))
                    })
                }

                val urlStr = "https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents/groups/$groupId/locations/$uid" +
                        "?updateMask.fieldPaths=lat&updateMask.fieldPaths=lng&updateMask.fieldPaths=online&updateMask.fieldPaths=lastSeen"

                val url = URL(urlStr)
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("X-HTTP-Method-Override", "PATCH")
                conn.setRequestProperty("Content-Type", "application/json")
                conn.setRequestProperty("Authorization", "Bearer ${'$'}idToken")
                conn.doOutput = true
                conn.outputStream.use { it.write(bodyJson.toString().toByteArray()) }
                conn.responseCode
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
        try { if (wakeLock?.isHeld == true) wakeLock?.release() } catch (e: Exception) { e.printStackTrace() }
    }
}
