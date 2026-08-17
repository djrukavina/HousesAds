package com.housesads.data.repository

import com.housesads.data.local.FavoriteAdDao
import com.housesads.data.local.HiddenAdDao
import com.housesads.data.local.HiddenAdEntity
import com.housesads.data.local.ListingDao
import com.housesads.data.local.ListingEntity
import com.housesads.data.local.toAd
import com.housesads.data.local.toFavoriteEntity
import com.housesads.data.model.Ad
import com.housesads.data.remote.AdDto
import com.housesads.data.remote.ScraperClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.withContext

class AdRepository(
    private val listingDao: ListingDao,
    private val favoriteAdDao: FavoriteAdDao,
    private val hiddenAdDao: HiddenAdDao,
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

    suspend fun deleteAd(ad: Ad) {
        withContext(Dispatchers.IO) {
            listingDao.deleteById(ad.id)
            favoriteAdDao.deleteById(ad.id)
            hiddenAdDao.hide(HiddenAdEntity(ad.id))
            runCatching { scraperClient.hideAd(ad.id) }
        }
    }

    suspend fun refresh(): List<Ad> {
        return withContext(Dispatchers.IO) {
            val oldIds = listingDao.getIds().toSet()
            val hiddenIds = hiddenAdDao.getIds().toSet()
            val remote = scraperClient.fetchAds()
            hiddenIds.forEach { id ->
                if (remote.any { it.id == id }) {
                    runCatching { scraperClient.hideAd(id) }
                }
            }
            val visible = remote.filter { it.id !in hiddenIds }
            val now = System.currentTimeMillis()
            listingDao.replaceAll(visible.map { it.toEntity(now) })
            if (oldIds.isEmpty()) {
                emptyList()
            } else {
                visible.filter { it.id !in oldIds }.map { dto ->
                    dto.toEntity(now).toAd(isFavorite = false)
                }
            }
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
