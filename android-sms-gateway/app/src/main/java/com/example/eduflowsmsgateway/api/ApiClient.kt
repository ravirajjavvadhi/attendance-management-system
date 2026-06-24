package com.example.eduflowsmsgateway.api

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object ApiClient {
    // Note: In a real app, this might come from a config or user input.
    // Ensure this matches the deployed Vercel backend or local IP.
    private const val BASE_URL = "https://attendance-management-system-afk0.onrender.com/"

    private val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    val apiService: EduFlowApi by lazy {
        retrofit.create(EduFlowApi::class.java)
    }
}
