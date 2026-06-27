package com.locationshare

import android.app.*
import android.content.Intent
import android.location.*
import android.os.*
import androidx.core.app.NotificationCompat

class LocationService : Service() {

    private lateinit var locationManager: LocationManager
    private var webViewRef: android.webkit.WebView? = null
    private val CHANNEL_ID = "location_channel"
    private val NOTIF_ID = 1

    companion object {
        var instance: LocationService? = null
        var onLocationUpdate: ((Double, Double) -> Unit)? = null
    }

    override fun onCreate() {
        super.onCreate()
        instance = this
        createNotificationChannel()
        startForeground(NOTIF_ID, buildNotification())
        startLocationUpdates()
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
                    }
                    override fun onStatusChanged(p: String?, s: Int, e: Bundle?) {}
                    override fun onProviderEnabled(p: String) {}
                    override fun onProviderDisabled(p: String) {}
                }
            )
        } catch (e: SecurityException) { e.printStackTrace() }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        instance = null
        locationManager.removeUpdates {}
    }
}
