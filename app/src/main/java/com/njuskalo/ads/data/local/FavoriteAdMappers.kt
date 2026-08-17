package com.njuskalo.ads.data.local

import com.njuskalo.ads.data.model.Ad

fun FavoriteAdEntity.toAd(): Ad = Ad(
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
    isFavorite = true,
)

fun Ad.toFavoriteEntity(savedAtMillis: Long = System.currentTimeMillis()): FavoriteAdEntity =
    FavoriteAdEntity(
        id = id,
        title = title,
        priceEur = priceEur,
        location = location,
        category = category,
        description = description,
        imageUrl = imageUrl,
        url = url,
        postedAtMillis = postedAtMillis,
        savedAtMillis = savedAtMillis,
        watchId = watchId,
        source = source,
    )

fun ListingEntity.toAd(isFavorite: Boolean): Ad = Ad(
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
