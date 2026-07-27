import shutil

path = "app/src/main/java/com/locationshare/LocationService.kt"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def report(ok, label, extra=""):
    print(("✅ " if ok else "❌ ")+label+" "+extra)

old1 = "import java.net.URL\n"
if "import java.net.URLEncoder" in content:
    report(False, "import URLEncoder", "- כבר קיים, מדלג")
elif content.count(old1) != 1:
    report(False, "import URLEncoder", f"- עוגן נמצא {content.count(old1)} פעמים")
else:
    content = content.replace(old1, old1 + "import java.net.URLEncoder\n")
    report(True, "import URLEncoder", "- נוסף")

old2 = 'private val CHAT_CHANNEL_ID = "chat_messages_channel"\n'
if 'DM_CHANNEL_ID' in content:
    report(False, "קבוע DM_CHANNEL_ID", "- כבר קיים, מדלג")
elif content.count(old2) != 1:
    report(False, "קבוע DM_CHANNEL_ID", f"- עוגן נמצא {content.count(old2)} פעמים")
else:
    content = content.replace(old2, old2 + '    private val DM_CHANNEL_ID = "dm_chat"\n')
    report(True, "קבוע DM_CHANNEL_ID", "- נוסף")

old3 = "private var lastMessageCheckTime: String? = null\n"
if "dmLastCheckTimes" in content:
    report(False, "שדה dmLastCheckTimes", "- כבר קיים, מדלג")
elif content.count(old3) != 1:
    report(False, "שדה dmLastCheckTimes", f"- עוגן נמצא {content.count(old3)} פעמים")
else:
    content = content.replace(old3, old3 + "    private val dmLastCheckTimes = mutableMapOf<String, String>()\n")
    report(True, "שדה dmLastCheckTimes", "- נוסף")

old4 = "val idToken = getFreshIdToken() ?: return@Thread\n"
if "checkForNewDmMessages(uid, idToken, prefs)" in content:
    report(False, "קריאה ל-checkForNewDmMessages", "- כבר קיים, מדלג")
elif content.count(old4) != 1:
    report(False, "קריאה ל-checkForNewDmMessages", f"- עוגן נמצא {content.count(old4)} פעמים")
else:
    content = content.replace(old4, old4 + "                checkForNewDmMessages(uid, idToken, prefs)\n")
    report(True, "קריאה ל-checkForNewDmMessages", "- נוספה")

anchor5 = "override fun onBind(intent: Intent?): IBinder? = null"
if "private fun checkForNewDmMessages" in content:
    report(False, "פונקציות DM חדשות", "- כבר קיימות, מדלג")
elif content.count(anchor5) != 1:
    report(False, "פונקציות DM חדשות", f"- עוגן נמצא {content.count(anchor5)} פעמים")
else:
    new_funcs = '''private fun checkForNewDmMessages(uid: String, idToken: String, prefs: android.content.SharedPreferences) {
        val peers = prefs.getStringSet("dm_peer_uids", emptySet()) ?: emptySet()
        if (peers.isEmpty()) return
        val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.US)
        sdf.timeZone = TimeZone.getTimeZone("UTC")
        for (peerUid in peers) {
            try {
                val dmId = listOf(uid, peerUid).sorted().joinToString("_")
                val checkFrom = dmLastCheckTimes[peerUid] ?: sdf.format(Date())
                val nowStr = sdf.format(Date())

                val queryBody = JSONObject().apply {
                    put("structuredQuery", JSONObject().apply {
                        put("from", org.json.JSONArray().put(JSONObject().put("collectionId", "messages")))
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

                val queryUrl = URL("https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents/dms/$dmId:runQuery")
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
                        val senderAvatar = fields.optJSONObject("avatar")?.optString("stringValue") ?: ""
                        val text = fields.optJSONObject("text")?.optString("stringValue") ?: ""
                        showDmNotification(peerUid, senderName, senderAvatar, text)
                    }
                }
                conn.disconnect()
                dmLastCheckTimes[peerUid] = nowStr
            } catch (e: Exception) { e.printStackTrace() }
        }
    }

    private fun showDmNotification(peerUid: String, senderName: String, senderAvatar: String, text: String) {
        try {
            val nm = getSystemService(NotificationManager::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                val channel = NotificationChannel(DM_CHANNEL_ID, "הודעות פרטיות", NotificationManager.IMPORTANCE_HIGH)
                nm.createNotificationChannel(channel)
            }
            fun enc(s: String) = URLEncoder.encode(s, "UTF-8").replace("+", "%20")
            val deepLink = "dm:" + enc(peerUid) + ":" + enc(senderName) + ":" + enc(senderAvatar)
            val intent = Intent(this, MainActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
            intent.putExtra("deep_link", deepLink)
            val pi = PendingIntent.getActivity(this, Random.nextInt(), intent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
            val notification = NotificationCompat.Builder(this, DM_CHANNEL_ID)
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

    '''
    content = content.replace(anchor5, new_funcs + anchor5)
    report(True, "פונקציות DM חדשות", "- נוספו")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
