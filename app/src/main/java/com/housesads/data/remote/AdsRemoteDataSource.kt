package com.housesads.data.remote

import com.google.gson.Gson
import com.housesads.BuildConfig
import com.housesads.data.settings.SettingsStore
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

interface AdsRemoteDataSource {
    fun fetchAds(): List<AdDto>
    fun hideAd(listingId: String)
}

class OkHttpAdsRemoteDataSource(
    private val settingsStore: SettingsStore,
    private val gson: Gson = Gson(),
    private val httpClient: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build(),
) : AdsRemoteDataSource {
    override fun fetchAds(): List<AdDto> {
        val url = FeedUrlResolver.resolve(settingsStore.scraperBaseUrl)
        val request = Request.Builder()
            .url(url)
            .header("Accept", "application/json")
            .header("Cache-Control", "no-cache")
            .build()
        httpClient.newCall(request).execute().use { response ->
            val body = response.body?.string().orEmpty()
            if (!response.isSuccessful) {
                error("Feed HTTP ${response.code}: ${body.take(200)}")
            }
            return gson.fromJson(body, AdsResponse::class.java).ads
        }
    }

    override fun hideAd(listingId: String) {
        val topic = BuildConfig.NTFY_HIDE_TOPIC.trim()
        if (topic.isEmpty() || listingId.isBlank()) return
        val request = Request.Builder()
            .url("https://ntfy.sh/$topic")
            .post(listingId.toRequestBody("text/plain; charset=utf-8".toMediaType()))
            .build()
        httpClient.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                error("Hide HTTP ${response.code}")
            }
        }
    }
}
