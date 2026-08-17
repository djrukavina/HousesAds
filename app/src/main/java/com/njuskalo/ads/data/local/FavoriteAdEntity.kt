package com.njuskalo.ads.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "favorite_ads")
data class FavoriteAdEntity(
    @PrimaryKey val id: String,
    val title: String,
    val priceEur: Double?,
    val location: String,
    val category: String,
    val description: String,
    val imageUrl: String?,
    val url: String,
    val postedAtMillis: Long,
    val savedAtMillis: Long,
    val watchId: String = "",
    val source: String = "",
)
