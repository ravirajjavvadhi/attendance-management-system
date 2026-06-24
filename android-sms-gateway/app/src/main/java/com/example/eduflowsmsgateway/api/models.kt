package com.example.eduflowsmsgateway.api

import com.google.gson.annotations.SerializedName

data class RegisterDeviceRequest(
    @SerializedName("pairing_token") val pairingToken: String,
    @SerializedName("device_uuid") val deviceUuid: String
)

data class RegisterDeviceResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("token_type") val tokenType: String,
    @SerializedName("device_id") val deviceId: Int
)

data class HeartbeatRequest(
    @SerializedName("device_uuid") val deviceUuid: String,
    @SerializedName("battery_percentage") val batteryPercentage: Int,
    @SerializedName("signal_strength") val signalStrength: Int,
    @SerializedName("sim_operator") val simOperator: String?
)

data class PendingSmsResponse(
    @SerializedName("id") val id: Int,
    @SerializedName("recipient_name") val recipientName: String?,
    @SerializedName("recipient_phone") val recipientPhone: String,
    @SerializedName("message") val message: String
)

data class SmsStatusUpdateRequest(
    @SerializedName("device_uuid") val deviceUuid: String,
    @SerializedName("sms_id") val smsId: Int,
    @SerializedName("status") val status: String,
    @SerializedName("error_message") val errorMessage: String? = null
)
