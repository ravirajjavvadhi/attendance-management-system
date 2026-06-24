package com.example.eduflowsmsgateway.di

import android.content.Context
import com.example.eduflowsmsgateway.SessionManager
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideSessionManager(@ApplicationContext context: Context): SessionManager {
        return SessionManager(context)
    }

    @Provides
    @Singleton
    fun provideAppDatabase(@ApplicationContext context: Context): com.example.eduflowsmsgateway.data.AppDatabase {
        return androidx.room.Room.databaseBuilder(
            context,
            com.example.eduflowsmsgateway.data.AppDatabase::class.java,
            "eduflow_sms.db"
        ).build()
    }

    @Provides
    fun provideSmsDao(database: com.example.eduflowsmsgateway.data.AppDatabase): com.example.eduflowsmsgateway.data.SmsDao {
        return database.smsDao()
    }
}
