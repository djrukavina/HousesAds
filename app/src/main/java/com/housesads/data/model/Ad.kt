package com.housesads.data.model

data class Ad(
    val id: String,
    val title: String,
    val priceEur: Double?,
    val location: String,
    val category: String,
    val description: String,
    val imageUrl: String?,
    val url: String,
    val postedAtMillis: Long,
    val watchId: String = "",
    val source: String = "",
    val isFavorite: Boolean = false,
)

enum class WatchFilter(val label: String, val watchId: String?) {
    ALL("Svi", null),
    ZAGREB_HOUSES("Kuće Zagreb", "zagreb_houses"),
    ZAGREB_APARTMENTS("Stanovi Zagreb", "zagreb_apartments"),
    COAST_HOUSES("Otoci", "coast_houses"),
    FAVORITES("Favoriti", null),
}
