package com.example.eduflowsmsgateway.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "sms_queue")
data class SmsEntity(
    @PrimaryKey val id: Int, // The backend SMS ID
    val recipientPhone: String,
    val message: String,
    val status: String // "PENDING", "SENT", "FAILED"
)
