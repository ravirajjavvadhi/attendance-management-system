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
import android.telephony.SubscriptionManager
import android.util.Log
import androidx.core.app.NotificationCompat
import com.example.eduflowsmsgateway.api.ApiClient
import com.example.eduflowsmsgateway.api.SmsStatusUpdateRequest
import com.example.eduflowsmsgateway.data.SmsDao
import com.example.eduflowsmsgateway.data.SmsEntity
import kotlinx.coroutines.*

class SmsPollingService : Service() {

    private val job = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.IO + job)

    private lateinit var sessionManager: SessionManager
    private lateinit var smsDao: SmsDao

    override fun onCreate() {
        super.onCreate()
        sessionManager = ServiceLocator.provideSessionManager(this)
        smsDao = ServiceLocator.provideSmsDao(this)
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
                    pollBackendForNewSms()
                    processLocalQueue()
                }
                delay(15000) // Poll every 15 seconds
            }
        }
    }

    private suspend fun pollBackendForNewSms() {
        try {
            val token = "Bearer ${sessionManager.getAuthToken()}"
            val deviceUuid = sessionManager.getDeviceUuid()

            val response = ApiClient.apiService.getPendingSms(token, deviceUuid)
            if (response.isSuccessful) {
                val pendingList = response.body() ?: emptyList()
                if (pendingList.isNotEmpty()) {
                    val entities = pendingList.map { 
                        SmsEntity(id = it.id, recipientPhone = it.recipientPhone, message = it.message, status = "PENDING") 
                    }
                    smsDao.insertAll(entities)
                    Log.d("SmsPolling", "Saved ${entities.size} SMS to Room DB")
                }
            }
        } catch (e: Exception) {
            Log.e("SmsPolling", "Error polling backend (offline?)", e)
        }
    }

    private suspend fun processLocalQueue() {
        val pendingSms = smsDao.getPendingSms()
        val token = "Bearer ${sessionManager.getAuthToken()}"
        val deviceUuid = sessionManager.getDeviceUuid()

        for (sms in pendingSms) {
            sendSms(sms, token, deviceUuid)
            delay(2000) // Delay between sending SMS to avoid carrier spam filters
        }
    }

    private suspend fun sendSms(sms: SmsEntity, token: String, deviceUuid: String) {
        var status = "FAILED"
        var errorMessage: String? = null

        try {
            // Enterprise enhancement: Dual SIM support & Multipart Unicode
            val smsManager: SmsManager = getSmsManager()

            val parts = smsManager.divideMessage(sms.message)
            smsManager.sendMultipartTextMessage(sms.recipientPhone, null, parts, null, null)
            status = "SENT"
        } catch (e: Exception) {
            Log.e("SmsPolling", "Error sending SMS", e)
            errorMessage = e.localizedMessage
        }

        // Update local Room database
        smsDao.updateStatus(sms.id, status)

        // Try to sync with backend
        try {
            ApiClient.apiService.updateSmsStatus(
                token,
                SmsStatusUpdateRequest(
                    deviceUuid = deviceUuid,
                    smsId = sms.id,
                    status = status,
                    errorMessage = errorMessage
                )
            )
        } catch (e: Exception) {
            Log.e("SmsPolling", "Error syncing status to backend", e)
            // It's okay, it remains updated in the local DB. We can build a sync worker later.
        }
    }

    private fun getSmsManager(): SmsManager {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val subscriptionManager = applicationContext.getSystemService(SubscriptionManager::class.java)
            val activeSubscriptionInfoList = subscriptionManager.activeSubscriptionInfoList
            
            if (!activeSubscriptionInfoList.isNullOrEmpty()) {
                // If dual SIM, default to SIM 1 (index 0). Can be configured via UI in future.
                val subscriptionId = activeSubscriptionInfoList[0].subscriptionId
                return applicationContext.getSystemService(SmsManager::class.java).createForSubscriptionId(subscriptionId)
            }
            return applicationContext.getSystemService(SmsManager::class.java)
        } else {
            @Suppress("DEPRECATION")
            return SmsManager.getDefault()
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
