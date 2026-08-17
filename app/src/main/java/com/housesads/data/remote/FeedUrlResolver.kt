package com.housesads.data.remote

object FeedUrlResolver {
    fun resolve(baseUrl: String, cacheBustMillis: Long = System.currentTimeMillis()): String {
        val configured = baseUrl.trim().trimEnd('/')
        return if (configured.endsWith(".json", ignoreCase = true)) {
            "$configured?t=$cacheBustMillis"
        } else {
            "$configured/ads"
        }
    }
}
