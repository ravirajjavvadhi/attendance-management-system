package com.example.eduflowsmsgateway.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "sms_queue")
data class SmsMessage(
    @PrimaryKey val messageUuid: String,
    val phoneNumber: String,
    val messageBody: String,
    val priority: String,
    var status: String = "PENDING" // PENDING, DELIVERED, FAILED
)
