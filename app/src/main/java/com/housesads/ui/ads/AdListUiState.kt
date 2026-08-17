package com.housesads.ui.ads

import com.housesads.data.model.Ad
import com.housesads.data.model.WatchFilter

data class AdListUiState(
    val ads: List<Ad> = emptyList(),
    val watchFilter: WatchFilter = WatchFilter.ALL,
    val isLoading: Boolean = true,
    val isRefreshing: Boolean = false,
    val errorMessage: String? = null,
    val scraperBaseUrl: String = "",
    val showServerDialog: Boolean = false,
)
