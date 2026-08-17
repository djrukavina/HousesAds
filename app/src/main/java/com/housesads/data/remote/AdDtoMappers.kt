package com.housesads.data.remote

import com.housesads.data.local.ListingEntity
import com.housesads.data.model.Ad

fun AdDto.toEntity(fetchedAtMillis: Long): ListingEntity = ListingEntity(
    id = id,
    title = title,
    priceEur = priceEur,
    location = location.orEmpty(),
    category = category.orEmpty(),
    watchId = watchId.orEmpty(),
    source = source.orEmpty(),
    description = description.orEmpty(),
    imageUrl = imageUrl,
    url = url,
    postedAtMillis = postedAtMillis ?: fetchedAtMillis,
    fetchedAtMillis = fetchedAtMillis,
)

fun AdDto.toAd(isFavorite: Boolean = false): Ad = Ad(
    id = id,
    title = title,
    priceEur = priceEur,
    location = location.orEmpty(),
    category = category.orEmpty(),
    description = description.orEmpty(),
    imageUrl = imageUrl,
    url = url,
    postedAtMillis = postedAtMillis ?: 0L,
    watchId = watchId.orEmpty(),
    source = source.orEmpty(),
    isFavorite = isFavorite,
)
