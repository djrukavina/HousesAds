package com.housesads.data.remote

import org.junit.Assert.assertEquals
import org.junit.Test

class FeedUrlResolverTest {

    @Test
    fun jsonFeedGetsCacheBuster() {
        val url = FeedUrlResolver.resolve(
            baseUrl = "https://example.test/listings.json",
            cacheBustMillis = 42L,
        )
        assertEquals("https://example.test/listings.json?t=42", url)
    }

    @Test
    fun apiFeedUsesAdsEndpoint() {
        val url = FeedUrlResolver.resolve("http://192.168.0.10:8765")
        assertEquals("http://192.168.0.10:8765/ads", url)
    }
}
