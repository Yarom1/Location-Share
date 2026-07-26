import shutil

path = "app/src/main/java/com/locationshare/LocationService.kt"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

start_anchor = "private fun startLocationUpdates() {"
end_anchor = "private fun updateNotificationText"

idx_start = content.find(start_anchor)
idx_end = content.find(end_anchor)

if idx_start == -1 or idx_end == -1 or idx_end < idx_start:
    print("❌ לא נמצאו עוגני התחלה/סוף")
elif "registerLocationUpdates" in content:
    print("⏭️ כבר קיים, מדלג")
else:
    old_block = content[idx_start:idx_end]

    new_block = '''private var isFastLocationMode = false
    private var locationListener: LocationListener? = null

    private fun startLocationUpdates() {
        locationManager = getSystemService(LOCATION_SERVICE) as LocationManager
        locationListener = object : LocationListener {
            override fun onLocationChanged(loc: Location) {
                lastKnownLat = loc.latitude
                lastKnownLng = loc.longitude
                onLocationUpdate?.invoke(loc.latitude, loc.longitude)
                writeLocationToFirestore(loc.latitude, loc.longitude)
                val speedKmh = loc.speed * 3.6f
                if (speedKmh >= 3.5f && !isFastLocationMode) {
                    isFastLocationMode = true
                    registerLocationUpdates(2000L, 3f)
                } else if (speedKmh < 3.5f && isFastLocationMode) {
                    isFastLocationMode = false
                    registerLocationUpdates(10000L, 5f)
                }
            }
            override fun onStatusChanged(p: String?, s: Int, e: Bundle?) {}
            override fun onProviderEnabled(p: String) {}
            override fun onProviderDisabled(p: String) {}
        }
        registerLocationUpdates(10000L, 5f)
    }

    private fun registerLocationUpdates(minTimeMs: Long, minDistM: Float) {
        val listener = locationListener ?: return
        try {
            locationManager.removeUpdates(listener)
        } catch (e: Exception) { e.printStackTrace() }
        try {
            if (locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
                locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, minTimeMs, minDistM, listener)
            }
        } catch (e: SecurityException) { e.printStackTrace() }
        try {
            if (locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)) {
                locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, minTimeMs, minDistM, listener)
            }
        } catch (e: SecurityException) { e.printStackTrace() }
    }

    '''

    new_content = content[:idx_start] + new_block + content[idx_end:]
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ הוחלף: {len(old_block)} תווים -> {len(new_block)} תווים")
