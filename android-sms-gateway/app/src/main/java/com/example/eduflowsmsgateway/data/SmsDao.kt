package com.example.eduflowsmsgateway.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface SmsDao {
    @JvmSuppressWildcards
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(smsList: List<SmsEntity>): List<Long>

    @JvmSuppressWildcards
    @Query("SELECT * FROM sms_queue WHERE status = 'PENDING'")
    suspend fun getPendingSms(): List<SmsEntity>

    @JvmSuppressWildcards
    @Query("UPDATE sms_queue SET status = :status WHERE id = :id")
    suspend fun updateStatus(id: Int, status: String): Int

    @Query("SELECT * FROM sms_queue")
    fun getAllSmsFlow(): Flow<List<SmsEntity>>

    @Query("SELECT COUNT(*) FROM sms_queue WHERE status = 'PENDING'")
    fun getPendingCountFlow(): Flow<Int>

    @Query("SELECT COUNT(*) FROM sms_queue WHERE status = 'SENT'")
    fun getSentCountFlow(): Flow<Int>

    @Query("SELECT COUNT(*) FROM sms_queue WHERE status = 'FAILED'")
    fun getFailedCountFlow(): Flow<Int>
}
