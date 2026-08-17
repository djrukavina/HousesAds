package com.njuskalo.ads.data.remote

import com.google.gson.Gson
import com.njuskalo.ads.data.settings.SettingsStore
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
        val base = settingsStore.scraperBaseUrl.trimEnd('/')
        val request = Request.Builder()
            .url("$base/ads")
            .header("Accept", "application/json")
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
