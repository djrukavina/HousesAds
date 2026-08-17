package com.housesads.data.repository

import com.housesads.data.local.FavoriteAdDao
import com.housesads.data.local.HiddenAdDao
import com.housesads.data.local.HiddenAdEntity
import com.housesads.data.local.ListingDao
import com.housesads.data.local.toAd
import com.housesads.data.local.toFavoriteEntity
import com.housesads.data.model.Ad
import com.housesads.data.remote.AdsRemoteDataSource
import com.housesads.data.remote.toAd
import com.housesads.data.remote.toEntity
import com.housesads.domain.sync.FeedSyncPlanner
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.withContext

class AdRepository(
    private val listingDao: ListingDao,
    private val favoriteAdDao: FavoriteAdDao,
    private val hiddenAdDao: HiddenAdDao,
    private val remoteDataSource: AdsRemoteDataSource,
    private val ioDispatcher: kotlinx.coroutines.CoroutineDispatcher = Dispatchers.IO,
) {
    fun observeFeed(): Flow<List<Ad>> = combine(
        listingDao.observeAll(),
        favoriteAdDao.observeIds(),
    ) { listings, favoriteIds ->
        val ids = favoriteIds.toSet()
        listings.map { listing -> listing.toAd(isFavorite = listing.id in ids) }
    }

    suspend fun toggleFavorite(ad: Ad) {
        if (ad.isFavorite) {
            favoriteAdDao.deleteById(ad.id)
        } else {
            favoriteAdDao.upsert(ad.toFavoriteEntity())
        }
    }

    suspend fun deleteAd(ad: Ad) {
        withContext(ioDispatcher) {
            listingDao.deleteById(ad.id)
            favoriteAdDao.deleteById(ad.id)
            hiddenAdDao.hide(HiddenAdEntity(ad.id))
            runCatching { remoteDataSource.hideAd(ad.id) }
        }
    }

    suspend fun refresh(): List<Ad> {
        return withContext(ioDispatcher) {
            val previousIds = listingDao.getIds().toSet()
            val hiddenIds = hiddenAdDao.getIds().toSet()
            val remote = remoteDataSource.fetchAds()
            val plan = FeedSyncPlanner.plan(
                remoteAds = remote,
                previousIds = previousIds,
                hiddenIds = hiddenIds,
            )
            plan.pendingHideIds.forEach { id ->
                runCatching { remoteDataSource.hideAd(id) }
            }
            val now = System.currentTimeMillis()
            listingDao.replaceAll(plan.visibleAds.map { it.toEntity(now) })
            plan.newAds.map { dto -> dto.toAd(isFavorite = false) }
        }
    }
}
