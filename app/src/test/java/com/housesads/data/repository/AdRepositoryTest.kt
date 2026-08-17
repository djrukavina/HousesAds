package com.housesads.data.repository

import com.housesads.data.local.FavoriteAdDao
import com.housesads.data.local.FavoriteAdEntity
import com.housesads.data.local.HiddenAdDao
import com.housesads.data.local.HiddenAdEntity
import com.housesads.data.local.ListingDao
import com.housesads.data.local.ListingEntity
import com.housesads.data.remote.AdDto
import com.housesads.data.remote.AdsRemoteDataSource
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

class AdRepositoryTest {

    private val dispatcher = StandardTestDispatcher()

    @Test
    fun refreshStoresVisibleAdsAndReturnsNewOnes() = runTest(dispatcher) {
        val listingDao = FakeListingDao(listOf(entity("old")))
        val hiddenDao = FakeHiddenAdDao()
        val remote = FakeRemoteDataSource(
            ads = listOf(
                dto("old"),
                dto("new"),
            ),
        )
        val repository = AdRepository(
            listingDao = listingDao,
            favoriteAdDao = FakeFavoriteAdDao(),
            hiddenAdDao = hiddenDao,
            remoteDataSource = remote,
            ioDispatcher = dispatcher,
        )

        val newAds = repository.refresh()
        dispatcher.scheduler.advanceUntilIdle()

        assertEquals(listOf("new"), newAds.map { it.id })
        assertEquals(listOf("old", "new"), listingDao.replaced.map { it.id })
    }

    @Test
    fun deleteAdHidesLocallyAndRemotely() = runTest(dispatcher) {
        val listingDao = FakeListingDao(listOf(entity("keep"), entity("drop")))
        val hiddenDao = FakeHiddenAdDao()
        val remote = FakeRemoteDataSource()
        val repository = AdRepository(
            listingDao = listingDao,
            favoriteAdDao = FakeFavoriteAdDao(),
            hiddenAdDao = hiddenDao,
            remoteDataSource = remote,
            ioDispatcher = dispatcher,
        )

        repository.deleteAd(
            com.housesads.data.model.Ad(
                id = "drop",
                title = "Drop",
                priceEur = 1.0,
                location = "Zagreb",
                category = "Test",
                description = "",
                imageUrl = null,
                url = "https://example.test/drop",
                postedAtMillis = 0L,
            ),
        )
        dispatcher.scheduler.advanceUntilIdle()

        assertEquals(listOf("drop"), hiddenDao.hiddenIds)
        assertEquals(listOf("drop"), remote.hiddenIds)
        assertEquals(listOf("keep"), listingDao.items.map { it.id })
    }

    private fun dto(id: String) = AdDto(
        id = id,
        title = id,
        priceEur = 100_000.0,
        location = "Zagreb",
        category = "Test",
        watchId = "zagreb_apartments",
        source = "njuskalo",
        description = "",
        imageUrl = null,
        url = "https://example.test/$id",
        postedAtMillis = 1L,
    )

    private fun entity(id: String) = ListingEntity(
        id = id,
        title = id,
        priceEur = 100_000.0,
        location = "Zagreb",
        category = "Test",
        watchId = "zagreb_apartments",
        source = "njuskalo",
        description = "",
        imageUrl = null,
        url = "https://example.test/$id",
        postedAtMillis = 1L,
        fetchedAtMillis = 1L,
    )
}

private class FakeListingDao(initial: List<ListingEntity> = emptyList()) : ListingDao {
    val items = initial.toMutableList()
    var replaced: List<ListingEntity> = emptyList()

    override fun observeAll(): Flow<List<ListingEntity>> = flowOf(items.toList())

    override suspend fun getIds(): List<String> = items.map { it.id }

    override suspend fun upsertAll(items: List<ListingEntity>) {
        this.items.addAll(items)
    }

    override suspend fun deleteById(id: String) {
        items.removeAll { it.id == id }
    }

    override suspend fun deleteAll() {
        items.clear()
    }

    override suspend fun replaceAll(items: List<ListingEntity>) {
        this.items.clear()
        this.items.addAll(items)
        replaced = items
    }
}

private class FakeHiddenAdDao : HiddenAdDao {
    val hiddenIds = mutableListOf<String>()

    override suspend fun getIds(): List<String> = hiddenIds.toList()

    override suspend fun hide(entity: HiddenAdEntity) {
        hiddenIds.add(entity.id)
    }
}

private class FakeFavoriteAdDao : FavoriteAdDao {
    override fun observeIds(): Flow<List<String>> = flowOf(emptyList())

    override suspend fun deleteById(id: String) = Unit

    override suspend fun upsert(entity: FavoriteAdEntity) = Unit
}

private class FakeRemoteDataSource(
    var ads: List<AdDto> = emptyList(),
) : AdsRemoteDataSource {
    val hiddenIds = mutableListOf<String>()

    override fun fetchAds(): List<AdDto> = ads

    override fun hideAd(listingId: String) {
        hiddenIds.add(listingId)
    }
}
