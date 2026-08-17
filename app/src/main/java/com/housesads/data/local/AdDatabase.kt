package com.housesads.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(
    entities = [FavoriteAdEntity::class, ListingEntity::class, HiddenAdEntity::class],
    version = 3,
    exportSchema = false,
)
abstract class AdDatabase : RoomDatabase() {
    abstract fun favoriteAdDao(): FavoriteAdDao
    abstract fun listingDao(): ListingDao
    abstract fun hiddenAdDao(): HiddenAdDao

    companion object {
        fun create(context: Context): AdDatabase =
            Room.databaseBuilder(
                context.applicationContext,
                AdDatabase::class.java,
                "houses_ads.db",
            )
                .fallbackToDestructiveMigration(dropAllTables = true)
                .build()
    }
}
