package com.njuskalo.ads.ui.ads

import com.njuskalo.ads.data.model.Ad
import com.njuskalo.ads.data.model.WatchFilter

data class AdListUiState(
    val ads: List<Ad> = emptyList(),
    val watchFilter: WatchFilter = WatchFilter.ALL,
    val isLoading: Boolean = true,
    val isRefreshing: Boolean = false,
    val errorMessage: String? = null,
    val scraperBaseUrl: String = "",
    val showServerDialog: Boolean = false,
)
