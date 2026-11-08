package com.housesads.domain.sync

import com.housesads.data.remote.AdDto
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class FeedSyncPlannerTest {

    @Test
    fun initialSyncDoesNotNotify() {
        val remote = listOf(dto("a"), dto("b"))
        val plan = FeedSyncPlanner.plan(
            remoteAds = remote,
            previousIds = emptySet(),
            hiddenIds = emptySet(),
        )
        assertEquals(2, plan.visibleAds.size)
        assertTrue(plan.newAds.isEmpty())
    }

    @Test
    fun detectsNewAdsAfterInitialSync() {
        val remote = listOf(dto("a"), dto("b"), dto("c"))
        val plan = FeedSyncPlanner.plan(
            remoteAds = remote,
            previousIds = setOf("a", "b"),
            hiddenIds = emptySet(),
        )
        assertEquals(listOf("c"), plan.newAds.map { it.id })
    }

    @Test
    fun hidesLocallyDeletedAdsAndQueuesRemoteHide() {
        val remote = listOf(dto("a"), dto("b"))
        val plan = FeedSyncPlanner.plan(
            remoteAds = remote,
            previousIds = setOf("a", "b"),
            hiddenIds = setOf("b"),
        )
        assertEquals(listOf("a"), plan.visibleAds.map { it.id })
        assertEquals(listOf("b"), plan.pendingHideIds)
    }

    private fun dto(id: String) = AdDto(
        id = id,
        title = "Test $id",
        priceEur = 100_000.0,
        location = "Zagreb",
        category = "Stanovi",
        watchId = "zagreb_apartments",
        source = "njuskalo",
        description = "",
        imageUrl = null,
        url = "https://example.test/$id",
        postedAtMillis = 1L,
    )
}
