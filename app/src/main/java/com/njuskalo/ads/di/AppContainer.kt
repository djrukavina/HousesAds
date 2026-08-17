package com.njuskalo.ads.di

import android.content.Context
import com.njuskalo.ads.data.local.AdDatabase
import com.njuskalo.ads.data.remote.ScraperClient
import com.njuskalo.ads.data.repository.AdRepository
import com.njuskalo.ads.data.settings.SettingsStore

class AppContainer(context: Context) {
    val settingsStore = SettingsStore(context)
    private val database: AdDatabase = AdDatabase.create(context)
    private val scraperClient = ScraperClient(settingsStore)
    val adRepository: AdRepository = AdRepository(
        listingDao = database.listingDao(),
        favoriteAdDao = database.favoriteAdDao(),
        scraperClient = scraperClient,
    )
}
