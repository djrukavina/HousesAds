package com.housesads.data.local

import com.housesads.data.model.Ad
import com.housesads.data.model.listingAd

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

fun ListingEntity.toAd(isFavorite: Boolean): Ad = listingAd(
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
