package com.example.eduflowsmsgateway

import android.content.Context
import android.content.SharedPreferences
import java.util.UUID

class SessionManager(context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences("EduFlowPrefs", Context.MODE_PRIVATE)

    companion object {
        private const val KEY_ACCESS_TOKEN = "access_token"
        private const val KEY_DEVICE_UUID = "device_uuid"
    }

    fun saveAuthToken(token: String) {
        prefs.edit().putString(KEY_ACCESS_TOKEN, token).apply()
    }

    fun getAuthToken(): String? {
        return prefs.getString(KEY_ACCESS_TOKEN, null)
    }

    fun clearAuthToken() {
        prefs.edit().remove(KEY_ACCESS_TOKEN).apply()
    }

    fun getDeviceUuid(): String {
        var uuid = prefs.getString(KEY_DEVICE_UUID, null)
        if (uuid == null) {
            uuid = UUID.randomUUID().toString()
            prefs.edit().putString(KEY_DEVICE_UUID, uuid).apply()
        }
        return uuid
    }

    fun isPaired(): Boolean {
        return getAuthToken() != null
    }
}
