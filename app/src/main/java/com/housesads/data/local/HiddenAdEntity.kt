package com.housesads.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "hidden_ads")
data class HiddenAdEntity(
    @PrimaryKey val id: String,
)
