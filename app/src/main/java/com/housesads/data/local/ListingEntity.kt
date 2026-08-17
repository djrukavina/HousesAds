package com.housesads.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "listings")
data class ListingEntity(
    @PrimaryKey val id: String,
    val title: String,
    val priceEur: Double?,
    val location: String,
    val category: String,
    val watchId: String,
    val source: String,
    val description: String,
    val imageUrl: String?,
    val url: String,
    val postedAtMillis: Long,
    val fetchedAtMillis: Long,
)
