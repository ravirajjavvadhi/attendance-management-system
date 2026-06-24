package com.example.eduflowsmsgateway

import android.content.Context
import android.os.BatteryManager
import android.telephony.TelephonyManager
import android.util.Log
import androidx.hilt.work.HiltWorker
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.example.eduflowsmsgateway.api.ApiClient
import com.example.eduflowsmsgateway.api.HeartbeatRequest
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject

@HiltWorker
class HeartbeatWorker @AssistedInject constructor(
    @Assisted appContext: Context,
    @Assisted workerParams: WorkerParameters,
    private val sessionManager: SessionManager
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {

        if (!sessionManager.isPaired()) {
            return Result.success()
        }

        try {
            val token = "Bearer ${sessionManager.getAuthToken()}"
            val deviceUuid = sessionManager.getDeviceUuid()

            // Get Battery Percentage
            val bm = applicationContext.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
            val batteryLevel = bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)

            // Get Network Operator
            val tm = applicationContext.getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager
            val operatorName = tm.networkOperatorName

            // Signal strength is complex to read in background on modern Android,
            // so we send a default 100% or implement proper PhoneStateListener if strictly needed.
            val signalStrength = 100

            val request = HeartbeatRequest(
                deviceUuid = deviceUuid,
                batteryPercentage = batteryLevel,
                signalStrength = signalStrength,
                simOperator = if (operatorName.isNotEmpty()) operatorName else "Unknown Network"
            )

            val response = ApiClient.apiService.sendHeartbeat(token, request)
            if (response.isSuccessful) {
                Log.d("HeartbeatWorker", "Heartbeat sent successfully")
            } else {
                Log.e("HeartbeatWorker", "Heartbeat failed: ${response.code()}")
            }

        } catch (e: Exception) {
            Log.e("HeartbeatWorker", "Error sending heartbeat", e)
            return Result.retry()
        }

        return Result.success()
    }
}
