package com.housesads.ui.ads

import com.housesads.data.model.Ad
import com.housesads.data.model.WatchFilter
import org.junit.Assert.assertEquals
import org.junit.Test

class AdFeedFilterTest {

    private val ads = listOf(
        ad("1", watchId = "zagreb_houses", favorite = false),
        ad("2", watchId = "zagreb_apartments", favorite = true),
        ad("3", watchId = "coast_houses", favorite = false),
    )

    @Test
    fun filtersByWatchId() {
        val filtered = ads.filterBy(WatchFilter.ZAGREB_APARTMENTS)
        assertEquals(listOf("2"), filtered.map { it.id })
    }

    @Test
    fun filtersFavoritesOnly() {
        val filtered = ads.filterBy(WatchFilter.FAVORITES)
        assertEquals(listOf("2"), filtered.map { it.id })
    }

    private fun ad(id: String, watchId: String, favorite: Boolean) = Ad(
        id = id,
        title = "Oglas $id",
        priceEur = 100_000.0,
        location = "Zagreb",
        category = "Test",
        description = "",
        imageUrl = null,
        url = "https://example.test/$id",
        postedAtMillis = 0L,
        watchId = watchId,
        source = "njuskalo",
        isFavorite = favorite,
    )
}
