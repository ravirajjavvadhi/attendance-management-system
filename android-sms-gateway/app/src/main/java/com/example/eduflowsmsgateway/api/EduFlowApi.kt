package com.example.eduflowsmsgateway.api

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST

interface EduFlowApi {

    @POST("api/v1/device/register")
    suspend fun registerDevice(
        @Body request: RegisterDeviceRequest
    ): Response<RegisterDeviceResponse>

    @POST("api/v1/device/heartbeat")
    suspend fun sendHeartbeat(
        @Header("Authorization") token: String,
        @Body request: HeartbeatRequest
    ): Response<Unit>

    @GET("api/v1/sms/pending")
    suspend fun getPendingSms(
        @Header("Authorization") token: String,
        @retrofit2.http.Query("device_uuid") deviceUuid: String
    ): Response<List<PendingSmsResponse>>

    @POST("api/v1/sms/status")
    suspend fun updateSmsStatus(
        @Header("Authorization") token: String,
        @Body request: SmsStatusUpdateRequest
    ): Response<Unit>
}
