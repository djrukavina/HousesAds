package com.njuskalo.ads.data.repository

import com.njuskalo.ads.data.local.FavoriteAdDao
import com.njuskalo.ads.data.local.ListingDao
import com.njuskalo.ads.data.local.ListingEntity
import com.njuskalo.ads.data.local.toAd
import com.njuskalo.ads.data.local.toFavoriteEntity
import com.njuskalo.ads.data.model.Ad
import com.njuskalo.ads.data.remote.AdDto
import com.njuskalo.ads.data.remote.ScraperClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.withContext

class AdRepository(
    private val listingDao: ListingDao,
    private val favoriteAdDao: FavoriteAdDao,
    private val scraperClient: ScraperClient,
) {
    fun observeFeed(): Flow<List<Ad>> = combine(
        listingDao.observeAll(),
        favoriteAdDao.observeIds(),
    ) { listings, favoriteIds ->
        val ids = favoriteIds.toSet()
        listings.map { listing -> listing.toAd(isFavorite = listing.id in ids) }
    }

    fun observeFavorites(): Flow<List<Ad>> =
        favoriteAdDao.observeAll().map { entities -> entities.map { it.toAd() } }

    suspend fun toggleFavorite(ad: Ad) {
        if (ad.isFavorite) {
            favoriteAdDao.deleteById(ad.id)
        } else {
            favoriteAdDao.upsert(ad.toFavoriteEntity())
        }
    }

    suspend fun refresh() {
        withContext(Dispatchers.IO) {
            val remote = scraperClient.fetchAds()
            val now = System.currentTimeMillis()
            listingDao.replaceAll(remote.map { it.toEntity(now) })
        }
    }
}

private fun AdDto.toEntity(fetchedAtMillis: Long): ListingEntity = ListingEntity(
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
