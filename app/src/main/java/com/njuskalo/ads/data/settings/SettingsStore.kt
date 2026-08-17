package com.njuskalo.ads.data.settings

import android.content.Context

class SettingsStore(context: Context) {
    private val prefs = context.applicationContext.getSharedPreferences(
        "njuskalo_ads",
        Context.MODE_PRIVATE,
    )

    var scraperBaseUrl: String
        get() = prefs.getString(KEY_URL, DEFAULT_URL)?.trim().orEmpty().ifBlank { DEFAULT_URL }
        set(value) {
            prefs.edit().putString(KEY_URL, value.trim()).apply()
        }

    companion object {
        const val DEFAULT_URL = "http://10.0.2.2:8765"
        private const val KEY_URL = "scraper_base_url"
    }
}
