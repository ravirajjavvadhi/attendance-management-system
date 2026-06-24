package com.example.eduflowsmsgateway.data

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(entities = [SmsEntity::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun smsDao(): SmsDao
}
