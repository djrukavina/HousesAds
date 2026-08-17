package com.housesads.ui.ads

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.housesads.data.model.Ad
import com.housesads.data.model.WatchFilter
import com.housesads.data.repository.AdRepository
import com.housesads.data.settings.SettingsStore
import com.housesads.notify.NewAdNotifier
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

class AdListViewModel(
    application: Application,
    private val adRepository: AdRepository,
    private val settingsStore: SettingsStore,
) : AndroidViewModel(application) {

    private val watchFilter = MutableStateFlow(WatchFilter.ALL)
    private val isRefreshing = MutableStateFlow(false)
    private val errorMessage = MutableStateFlow<String?>(null)
    private val scraperBaseUrl = MutableStateFlow(settingsStore.scraperBaseUrl)
    private val showServerDialog = MutableStateFlow(false)

    val uiState: StateFlow<AdListUiState> = combine(
        combine(
            adRepository.observeFeed(),
            watchFilter,
            isRefreshing,
        ) { ads, filter, refreshing ->
            Triple(ads, filter, refreshing)
        },
        combine(
            errorMessage,
            scraperBaseUrl,
            showServerDialog,
        ) { error, url, dialog ->
            Triple(error, url, dialog)
        },
    ) { feed, extras ->
        val (ads, filter, refreshing) = feed
        val (error, url, dialog) = extras
        AdListUiState(
            ads = ads.filterBy(filter),
            watchFilter = filter,
            isLoading = false,
            isRefreshing = refreshing,
            errorMessage = error,
            scraperBaseUrl = url,
            showServerDialog = dialog,
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = AdListUiState(),
    )

    init {
        refresh(userInitiated = false)
        viewModelScope.launch {
            while (isActive) {
                delay(30_000)
                refresh(userInitiated = false)
            }
        }
    }

    fun selectFilter(filter: WatchFilter) {
        watchFilter.value = filter
    }

    fun toggleFavorite(ad: Ad) {
        viewModelScope.launch {
            adRepository.toggleFavorite(ad)
        }
    }

    fun deleteAd(ad: Ad) {
        viewModelScope.launch {
            adRepository.deleteAd(ad)
        }
    }

    fun refresh(userInitiated: Boolean = true) {
        viewModelScope.launch {
            if (userInitiated) isRefreshing.value = true
            errorMessage.value = null
            runCatching { adRepository.refresh() }
                .onSuccess { newAds ->
                    if (newAds.isNotEmpty()) {
                        NewAdNotifier.show(getApplication(), newAds)
                    }
                }
                .onFailure { error ->
                    errorMessage.value = error.message ?: "Sinkronizacija nije uspjela"
                }
            isRefreshing.value = false
        }
    }

    fun openServerDialog() {
        showServerDialog.value = true
    }

    fun dismissServerDialog() {
        showServerDialog.value = false
    }

    fun saveScraperUrl(url: String) {
        settingsStore.scraperBaseUrl = url
        scraperBaseUrl.value = settingsStore.scraperBaseUrl
        showServerDialog.value = false
        refresh()
    }
}

private fun List<Ad>.filterBy(filter: WatchFilter): List<Ad> = when (filter) {
    WatchFilter.ALL -> this
    WatchFilter.FAVORITES -> filter { it.isFavorite }
    WatchFilter.ZAGREB_HOUSES,
    WatchFilter.ZAGREB_APARTMENTS,
    WatchFilter.COAST_HOUSES,
    -> filter { it.watchId == filter.watchId }
}

class AdListViewModelFactory(
    private val application: Application,
    private val adRepository: AdRepository,
    private val settingsStore: SettingsStore,
) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(AdListViewModel::class.java)) {
            return AdListViewModel(application, adRepository, settingsStore) as T
        }
        throw IllegalArgumentException("Unknown ViewModel: ${modelClass.name}")
    }
}
