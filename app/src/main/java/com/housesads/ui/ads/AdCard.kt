package com.housesads.ui.ads

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.OpenInNew
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.outlined.Delete
import androidx.compose.material.icons.outlined.FavoriteBorder
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.housesads.data.model.Ad
import com.housesads.ui.theme.HousesAdsTheme
import java.text.NumberFormat
import java.util.Locale

@Composable
fun AdCard(
    ad: Ad,
    onToggleFavorite: () -> Unit,
    onOpen: () -> Unit = {},
    onDelete: () -> Unit = {},
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceContainerLow,
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            verticalAlignment = Alignment.Top,
        ) {
            Box(
                modifier = Modifier
                    .size(88.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(MaterialTheme.colorScheme.primaryContainer),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = ad.category.take(1).ifBlank { "O" },
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.onPrimaryContainer,
                )
            }
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = listOfNotNull(
                        ad.category.takeIf { it.isNotBlank() },
                        sourceLabel(ad.source),
                    ).joinToString(" · ").ifBlank { "OGLAS" }.uppercase(Locale.forLanguageTag("hr-HR")),
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.primary,
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = ad.title,
                    style = MaterialTheme.typography.titleMedium,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = formatPrice(ad.priceEur),
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.secondary,
                )
                Spacer(modifier = Modifier.height(6.dp))
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    Icon(
                        imageVector = Icons.Filled.LocationOn,
                        contentDescription = null,
                        modifier = Modifier.size(14.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Text(
                        text = ad.location,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                if (ad.url.isNotBlank()) {
                    TextButton(
                        onClick = onOpen,
                        modifier = Modifier.padding(start = 0.dp, top = 2.dp),
                    ) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Outlined.OpenInNew,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp),
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = openLabel(ad.source),
                            textDecoration = TextDecoration.Underline,
                        )
                    }
                }
            }
            Column {
                IconButton(onClick = onToggleFavorite) {
                    Icon(
                        imageVector = if (ad.isFavorite) {
                            Icons.Filled.Favorite
                        } else {
                            Icons.Outlined.FavoriteBorder
                        },
                        contentDescription = if (ad.isFavorite) {
                            "Ukloni iz favorita"
                        } else {
                            "Spremi u favorite"
                        },
                        tint = if (ad.isFavorite) {
                            MaterialTheme.colorScheme.primary
                        } else {
                            MaterialTheme.colorScheme.onSurfaceVariant
                        },
                    )
                }
                IconButton(onClick = onDelete) {
                    Icon(
                        imageVector = Icons.Outlined.Delete,
                        contentDescription = "Obriši oglas",
                        tint = MaterialTheme.colorScheme.error,
                    )
                }
            }
        }
    }
}

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

@Preview(showBackground = true)
@Composable
private fun AdCardPreview() {
    HousesAdsTheme {
        AdCard(
            ad = Ad(
                id = "preview",
                title = "Trosoban stan, novogradnja, 82 m²",
                priceEur = 289_000.0,
                location = "Zagreb",
                category = "Stanovi Zagreb",
                description = "",
                imageUrl = null,
                url = "https://www.njuskalo.hr/nekretnine/oglas-1",
                postedAtMillis = 0L,
                source = "njuskalo",
                isFavorite = true,
            ),
            onToggleFavorite = {},
            modifier = Modifier.padding(16.dp),
        )
    }
}
