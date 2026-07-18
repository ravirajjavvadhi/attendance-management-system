package com.example.eduflowsmsgateway.worker

import android.content.Context
import android.telephony.SmsManager
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class SmsSyncWorker(context: Context, workerParams: WorkerParameters) : CoroutineWorker(context, workerParams) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        try {
            // In a real implementation, this would fetch from a DataRepository which polls the FastAPI backend.
            // For now, we mock the flow.
            
            val smsManager = SmsManager.getDefault()
            val pendingMessages = listOf(
                mapOf("id" to "1", "phone" to "+1234567890", "message" to "EduFlow: Your ward is absent today.")
            )

            for (msg in pendingMessages) {
                val phone = msg["phone"] as String
                val text = msg["message"] as String
                
                // Dispatch SMS
                smsManager.sendTextMessage(phone, null, text, null, null)
                
                // Here we would normally mark as DELIVERED in the local Room DB 
                // and HTTP POST an ACK back to the FastAPI Backend.
                println("Dispatched SMS to $phone")
            }

            Result.success()
        } catch (e: Exception) {
            e.printStackTrace()
            Result.retry()
        }
    }
}
