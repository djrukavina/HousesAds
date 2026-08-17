package com.housesads.domain.sync

import com.housesads.data.remote.AdDto

data class FeedSyncPlan(
    val visibleAds: List<AdDto>,
    val newAds: List<AdDto>,
    val pendingHideIds: List<String>,
)

object FeedSyncPlanner {
    fun plan(
        remoteAds: List<AdDto>,
        previousIds: Set<String>,
        hiddenIds: Set<String>,
        isInitialSync: Boolean = previousIds.isEmpty(),
    ): FeedSyncPlan {
        val pendingHideIds = hiddenIds.filter { hiddenId ->
            remoteAds.any { it.id == hiddenId }
        }
        val visibleAds = remoteAds.filter { it.id !in hiddenIds }
        val newAds = if (isInitialSync) {
            emptyList()
        } else {
            visibleAds.filter { it.id !in previousIds }
        }
        return FeedSyncPlan(
            visibleAds = visibleAds,
            newAds = newAds,
            pendingHideIds = pendingHideIds,
        )
    }
}
