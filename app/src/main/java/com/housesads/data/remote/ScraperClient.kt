package com.housesads.data.remote

import com.google.gson.Gson
import com.housesads.data.settings.SettingsStore
import okhttp3.OkHttpClient
import okhttp3.Request
import java.util.concurrent.TimeUnit

class ScraperClient(
    private val settingsStore: SettingsStore,
    private val gson: Gson = Gson(),
    private val httpClient: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build(),
) {
    fun fetchAds(): List<AdDto> {
        val configured = settingsStore.scraperBaseUrl.trimEnd('/')
        val url = if (configured.endsWith(".json")) {
            "$configured?t=${System.currentTimeMillis()}"
        } else {
            "$configured/ads"
        }
        val request = Request.Builder()
            .url(url)
            .header("Accept", "application/json")
            .header("Cache-Control", "no-cache")
            .build()
        httpClient.newCall(request).execute().use { response ->
            val body = response.body?.string().orEmpty()
            if (!response.isSuccessful) {
                error("Scraper HTTP ${response.code}: ${body.take(200)}")
            }
            return gson.fromJson(body, AdsResponse::class.java).ads
        }
    }
}
