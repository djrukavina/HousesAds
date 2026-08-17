package com.housesads.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Transaction
import kotlinx.coroutines.flow.Flow

@Dao
interface ListingDao {
    @Query("SELECT * FROM listings ORDER BY postedAtMillis DESC")
    fun observeAll(): Flow<List<ListingEntity>>

    @Query("SELECT id FROM listings")
    suspend fun getIds(): List<String>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertAll(items: List<ListingEntity>)

    @Query("DELETE FROM listings WHERE id = :id")
    suspend fun deleteById(id: String)

    @Query("DELETE FROM listings")
    suspend fun deleteAll()

    @Transaction
    suspend fun replaceAll(items: List<ListingEntity>) {
        deleteAll()
        if (items.isNotEmpty()) {
            upsertAll(items)
        }
    }
}
