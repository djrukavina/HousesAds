package com.housesads.di

import android.content.Context
import com.housesads.data.local.AdDatabase
import com.housesads.data.remote.OkHttpAdsRemoteDataSource
import com.housesads.data.repository.AdRepository
import com.housesads.data.settings.SettingsStore

class AppContainer(context: Context) {
    val settingsStore = SettingsStore(context)
    private val database: AdDatabase = AdDatabase.create(context)
    private val remoteDataSource = OkHttpAdsRemoteDataSource(settingsStore)
    val adRepository: AdRepository = AdRepository(
        listingDao = database.listingDao(),
        favoriteAdDao = database.favoriteAdDao(),
        hiddenAdDao = database.hiddenAdDao(),
        remoteDataSource = remoteDataSource,
    )
}
