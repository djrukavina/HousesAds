package com.housesads.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface FavoriteAdDao {
    @Query("SELECT id FROM favorite_ads")
    fun observeIds(): Flow<List<String>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(entity: FavoriteAdEntity)

    @Query("DELETE FROM favorite_ads WHERE id = :id")
    suspend fun deleteById(id: String)
}
