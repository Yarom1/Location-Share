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
import kotlin.random.Random

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
    private val CHAT_CHANNEL_ID = "chat_messages_channel"
    private var lastMessageCheckTime: String? = null
    private val chatCheckHandler = Handler(Looper.getMainLooper())
    private val chatCheckIntervalMs = 15_000L
    private val chatCheckRunnable = object : Runnable {
        override fun run() {
            checkForNewChatMessages()
            chatCheckHandler.postDelayed(this, chatCheckIntervalMs)
        }
    }
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
        chatCheckHandler.postDelayed(chatCheckRunnable, chatCheckIntervalMs)
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
        val listener = object : LocationListener {
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
        try {
            if (locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
                locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 10000L, 5f, listener)
            }
        } catch (e: SecurityException) { e.printStackTrace() }
        try {
            if (locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)) {
                locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 10000L, 5f, listener)
            }
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
        val refreshToken = prefs.getString("refresh_token", null)
        if (refreshToken == null) { updateNotificationText("אין refresh token שמור - פתח את האפליקציה"); return null }
        val apiKey = prefs.getString("api_key", null)
        if (apiKey == null) { updateNotificationText("אין api key שמור - פתח את האפליקציה"); return null }

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
                    lastWriteTimeMillis = System.currentTimeMillis()
                    val now = SimpleDateFormat("HH:mm:ss", Locale.US).format(Date())
                    updateNotificationText("משתף מיקום ברקע · עודכן ב-$now")
                }
                conn.disconnect()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()
    }

    private fun checkForNewChatMessages() {
        Thread {
            try {
                val prefs = getSharedPreferences("location_share_prefs", MODE_PRIVATE)
                val lastJsActive = prefs.getLong("last_js_active_time", 0L)
                if (System.currentTimeMillis() - lastJsActive < 10_000L) {
                    // JS is alive and already handling notifications itself - avoid duplicates
                    return@Thread
                }
                val uid = prefs.getString("uid", null) ?: return@Thread
                val groupId = prefs.getString("active_group_id", null)
                if (groupId.isNullOrEmpty()) return@Thread
                val idToken = getFreshIdToken() ?: return@Thread

                val mutedUrl = URL("https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents/groups/$groupId/members/$uid")
                val mutedConn = mutedUrl.openConnection() as HttpURLConnection
                mutedConn.requestMethod = "GET"
                mutedConn.setRequestProperty("Authorization", "Bearer $idToken")
                var isMuted = false
                if (mutedConn.responseCode == 200) {
                    val body = mutedConn.inputStream.bufferedReader().use { it.readText() }
                    val fields = JSONObject(body).optJSONObject("fields")
                    if (fields != null && fields.has("muted")) {
                        isMuted = fields.getJSONObject("muted").optBoolean("booleanValue", false)
                    }
                }
                mutedConn.disconnect()
                if (isMuted) { lastMessageCheckTime = null; return@Thread }

                val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.US)
                sdf.timeZone = TimeZone.getTimeZone("UTC")
                val checkFrom = lastMessageCheckTime ?: sdf.format(Date())
                val nowStr = sdf.format(Date())

                val queryBody = JSONObject().apply {
                    put("structuredQuery", JSONObject().apply {
                        put("from", org.json.JSONArray().put(JSONObject().put("collectionId", "groupChat")))
                        put("where", JSONObject().apply {
                            put("fieldFilter", JSONObject().apply {
                                put("field", JSONObject().put("fieldPath", "ts"))
                                put("op", "GREATER_THAN")
                                put("value", JSONObject().put("timestampValue", checkFrom))
                            })
                        })
                        put("orderBy", org.json.JSONArray().put(JSONObject().apply {
                            put("field", JSONObject().put("fieldPath", "ts"))
                            put("direction", "ASCENDING")
                        }))
                    })
                }

                val queryUrl = URL("https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents/groups/$groupId:runQuery")
                val conn = queryUrl.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json")
                conn.setRequestProperty("Authorization", "Bearer $idToken")
                conn.doOutput = true
                conn.outputStream.use { it.write(queryBody.toString().toByteArray()) }

                if (conn.responseCode == 200) {
                    val respText = conn.inputStream.bufferedReader().use { it.readText() }
                    val arr = org.json.JSONArray(respText)
                    for (i in 0 until arr.length()) {
                        val item = arr.optJSONObject(i) ?: continue
                        val doc = item.optJSONObject("document") ?: continue
                        val fields = doc.optJSONObject("fields") ?: continue
                        val senderUid = fields.optJSONObject("uid")?.optString("stringValue")
                        if (senderUid == uid) continue
                        val senderName = fields.optJSONObject("name")?.optString("stringValue") ?: "מישהו"
                        val text = fields.optJSONObject("text")?.optString("stringValue") ?: ""
                        showChatNotification(senderName, text)
                    }
                }
                conn.disconnect()
                lastMessageCheckTime = nowStr
            } catch (e: Exception) { e.printStackTrace() }
        }.start()
    }

    private fun showChatNotification(senderName: String, text: String) {
        try {
            val nm = getSystemService(NotificationManager::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                val channel = NotificationChannel(CHAT_CHANNEL_ID, "הודעות צ'אט", NotificationManager.IMPORTANCE_HIGH)
                nm.createNotificationChannel(channel)
            }
            val intent = Intent(this, MainActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
            intent.putExtra("deep_link", "chat")
            val pi = PendingIntent.getActivity(this, Random.nextInt(), intent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
            val notification = NotificationCompat.Builder(this, CHAT_CHANNEL_ID)
                .setContentTitle(senderName)
                .setContentText(text)
                .setSmallIcon(android.R.drawable.ic_dialog_email)
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setAutoCancel(true)
                .setContentIntent(pi)
                .build()
            nm.notify(Random.nextInt(), notification)
        } catch (e: Exception) { e.printStackTrace() }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        instance = null
        locationManager.removeUpdates {}
        heartbeatHandler.removeCallbacks(heartbeatRunnable)
        chatCheckHandler.removeCallbacks(chatCheckRunnable)
        try { if (wakeLock?.isHeld == true) wakeLock?.release() } catch (e: Exception) { e.printStackTrace() }
    }
}
