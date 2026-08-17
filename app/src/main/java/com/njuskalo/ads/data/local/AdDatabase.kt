package com.njuskalo.ads.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(
    entities = [FavoriteAdEntity::class, ListingEntity::class],
    version = 2,
    exportSchema = false,
)
abstract class AdDatabase : RoomDatabase() {
    abstract fun favoriteAdDao(): FavoriteAdDao
    abstract fun listingDao(): ListingDao

    companion object {
        fun create(context: Context): AdDatabase =
            Room.databaseBuilder(
                context.applicationContext,
                AdDatabase::class.java,
                "njuskalo_ads.db",
            )
                .fallbackToDestructiveMigration(dropAllTables = true)
                .build()
    }
}
