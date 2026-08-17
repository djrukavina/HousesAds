package com.housesads.data.settings

import android.content.Context

class SettingsStore(context: Context) {
    private val prefs = context.applicationContext.getSharedPreferences(
        "houses_ads",
        Context.MODE_PRIVATE,
    )

    var scraperBaseUrl: String
        get() {
            val stored = prefs.getString(KEY_URL, DEFAULT_URL)?.trim().orEmpty()
            return if (stored.isBlank() || stored == LEGACY_URL) DEFAULT_URL else stored
        }
        set(value) {
            prefs.edit().putString(KEY_URL, value.trim()).apply()
        }

    companion object {
        const val DEFAULT_URL =
            "https://raw.githubusercontent.com/CurkovicDavid/NjuskaloAds/main/data/listings.json"
        private const val LEGACY_URL = "http://10.0.2.2:8765"
        private const val KEY_URL = "scraper_base_url"
    }
}
