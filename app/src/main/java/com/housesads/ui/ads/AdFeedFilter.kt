package com.housesads.ui.ads

import com.housesads.data.model.Ad
import com.housesads.data.model.WatchFilter

fun List<Ad>.filterBy(filter: WatchFilter): List<Ad> = when (filter) {
    WatchFilter.ALL -> this
    WatchFilter.FAVORITES -> filter { it.isFavorite }
    WatchFilter.ZAGREB_HOUSES,
    WatchFilter.ZAGREB_APARTMENTS,
    WatchFilter.COAST_HOUSES,
    -> filter { it.watchId == filter.watchId }
}
