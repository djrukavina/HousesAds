package com.housesads.data.model

fun listingAd(
    id: String,
    title: String,
    priceEur: Double?,
    location: String,
    category: String,
    description: String,
    imageUrl: String?,
    url: String,
    postedAtMillis: Long,
    watchId: String = "",
    source: String = "",
    isFavorite: Boolean = false,
): Ad = Ad(
    id = id,
    title = title,
    priceEur = priceEur,
    location = location,
    category = category,
    description = description,
    imageUrl = imageUrl,
    url = url,
    postedAtMillis = postedAtMillis,
    watchId = watchId,
    source = source,
    isFavorite = isFavorite,
)
