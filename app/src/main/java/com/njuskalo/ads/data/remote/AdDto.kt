package com.njuskalo.ads.data.remote

import com.google.gson.annotations.SerializedName

data class AdsResponse(
    @SerializedName("ads") val ads: List<AdDto> = emptyList(),
)

data class AdDto(
    @SerializedName("id") val id: String,
    @SerializedName("title") val title: String,
    @SerializedName("priceEur") val priceEur: Double?,
    @SerializedName("location") val location: String?,
    @SerializedName("category") val category: String?,
    @SerializedName("watchId") val watchId: String?,
    @SerializedName("source") val source: String?,
    @SerializedName("description") val description: String?,
    @SerializedName("imageUrl") val imageUrl: String?,
    @SerializedName("url") val url: String,
    @SerializedName("postedAtMillis") val postedAtMillis: Long?,
)
