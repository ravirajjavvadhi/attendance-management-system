package com.example.eduflowsmsgateway

import android.content.Context
import androidx.room.Room
import com.example.eduflowsmsgateway.data.AppDatabase
import com.example.eduflowsmsgateway.data.SmsDao

object ServiceLocator {
    
    private var sessionManager: SessionManager? = null
    private var database: AppDatabase? = null

    fun provideSessionManager(context: Context): SessionManager {
        if (sessionManager == null) {
            sessionManager = SessionManager(context.applicationContext)
        }
        return sessionManager!!
    }

    fun provideAppDatabase(context: Context): AppDatabase {
        if (database == null) {
            database = Room.databaseBuilder(
                context.applicationContext,
                AppDatabase::class.java,
                "eduflow_sms.db"
            ).build()
        }
        return database!!
    }

    fun provideSmsDao(context: Context): SmsDao {
        return provideAppDatabase(context).smsDao()
    }
}
