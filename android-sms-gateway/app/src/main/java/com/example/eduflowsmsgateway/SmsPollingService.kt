package com.example.eduflowsmsgateway

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.telephony.SmsManager
import android.util.Log
import androidx.core.app.NotificationCompat
import com.example.eduflowsmsgateway.api.ApiClient
import com.example.eduflowsmsgateway.api.SmsStatusUpdateRequest
import kotlinx.coroutines.*

class SmsPollingService : Service() {

    private val job = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.IO + job)
    private lateinit var sessionManager: SessionManager

    override fun onCreate() {
        super.onCreate()
        sessionManager = SessionManager(this)
        createNotificationChannel()
        startForeground(1, buildNotification())
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startPolling()
        return START_STICKY
    }

    private fun startPolling() {
        scope.launch {
            while (isActive) {
                if (sessionManager.isPaired()) {
                    pollAndSend()
                }
                delay(15000) // Poll every 15 seconds
            }
        }
    }

    private suspend fun pollAndSend() {
        try {
            val token = "Bearer ${sessionManager.getAuthToken()}"
            val deviceUuid = sessionManager.getDeviceUuid()

            val response = ApiClient.apiService.getPendingSms(token, deviceUuid)
            if (response.isSuccessful) {
                val pendingList = response.body() ?: emptyList()
                for (sms in pendingList) {
                    sendSms(sms.id, sms.recipientPhone, sms.message, token, deviceUuid)
                    delay(2000) // Delay between sending SMS to avoid carrier spam filters
                }
            }
        } catch (e: Exception) {
            Log.e("SmsPolling", "Error polling", e)
        }
    }

    private suspend fun sendSms(smsId: Int, phone: String, message: String, token: String, deviceUuid: String) {
        var status = "FAILED"
        var errorMessage: String? = null

        try {
            val smsManager: SmsManager = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                applicationContext.getSystemService(SmsManager::class.java)
            } else {
                @Suppress("DEPRECATION")
                SmsManager.getDefault()
            }

            val parts = smsManager.divideMessage(message)
            smsManager.sendMultipartTextMessage(phone, null, parts, null, null)
            status = "SENT"
        } catch (e: Exception) {
            Log.e("SmsPolling", "Error sending SMS", e)
            errorMessage = e.localizedMessage
        }

        try {
            ApiClient.apiService.updateSmsStatus(
                token,
                SmsStatusUpdateRequest(
                    deviceUuid = deviceUuid,
                    smsId = smsId,
                    status = status,
                    errorMessage = errorMessage
                )
            )
        } catch (e: Exception) {
            Log.e("SmsPolling", "Error updating status", e)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        job.cancel()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                "SMS_GATEWAY",
                "SMS Gateway Service",
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    private fun buildNotification(): Notification {
        return NotificationCompat.Builder(this, "SMS_GATEWAY")
            .setContentTitle("EduFlow SMS Gateway")
            .setContentText("Active and polling for messages")
            .setSmallIcon(R.mipmap.ic_launcher)
            .build()
    }
}
