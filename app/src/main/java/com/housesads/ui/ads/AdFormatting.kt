package com.housesads.ui.ads

import java.text.NumberFormat
import java.util.Locale

fun sourceLabel(source: String): String? = when (source.lowercase(Locale.ROOT)) {
    "njuskalo" -> "Njuškalo"
    "index" -> "Index"
    else -> source.takeIf { it.isNotBlank() }
}

fun openLabel(source: String): String = when (source.lowercase(Locale.ROOT)) {
    "njuskalo" -> "Otvori na Njuškalu"
    "index" -> "Otvori na Indexu"
    else -> "Otvori originalni oglas"
}

fun formatPrice(priceEur: Double?): String {
    if (priceEur == null) return "Po dogovoru"
    val formatted = NumberFormat.getNumberInstance(Locale.forLanguageTag("hr-HR")).apply {
        maximumFractionDigits = 0
        minimumFractionDigits = 0
    }.format(priceEur)
    return "$formatted €"
}
