package com.housesads.ui.ads

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.housesads.data.model.Ad
import com.housesads.data.model.WatchFilter

@Composable
fun AdListRoute(
    viewModel: AdListViewModel,
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    AdListScreen(
        uiState = uiState,
        onToggleFavorite = viewModel::toggleFavorite,
        onSelectFilter = viewModel::selectFilter,
        onRefresh = viewModel::refresh,
        onOpenServerDialog = viewModel::openServerDialog,
        onDismissServerDialog = viewModel::dismissServerDialog,
        onSaveServerUrl = viewModel::saveScraperUrl,
        onDeleteAd = viewModel::deleteAd,
        onOpenAd = { ad ->
            if (ad.url.isNotBlank()) {
                context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(ad.url)))
            }
        },
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AdListScreen(
    uiState: AdListUiState,
    onToggleFavorite: (Ad) -> Unit,
    onSelectFilter: (WatchFilter) -> Unit,
    onRefresh: () -> Unit,
    onOpenServerDialog: () -> Unit,
    onDismissServerDialog: () -> Unit,
    onSaveServerUrl: (String) -> Unit,
    onDeleteAd: (Ad) -> Unit,
    onOpenAd: (Ad) -> Unit,
    modifier: Modifier = Modifier,
) {
    var pendingDelete by remember { mutableStateOf<Ad?>(null) }
    Scaffold(
        modifier = modifier.fillMaxSize(),
        topBar = {
            TopAppBar(
                title = { Text("HousesAds") },
                actions = {
                    IconButton(onClick = onRefresh) {
                        Icon(Icons.Filled.Refresh, contentDescription = "Osvježi")
                    }
                    IconButton(onClick = onOpenServerDialog) {
                        Icon(Icons.Filled.Settings, contentDescription = "Adresa scrapera")
                    }
                },
            )
        },
    ) { innerPadding ->
        PullToRefreshBox(
            isRefreshing = uiState.isRefreshing,
            onRefresh = onRefresh,
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding),
        ) {
            Column(modifier = Modifier.fillMaxSize()) {
                LazyRow(
                    modifier = Modifier.fillMaxWidth(),
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    items(WatchFilter.entries.toList(), key = { it.name }) { filter ->
                        FilterChip(
                            selected = uiState.watchFilter == filter,
                            onClick = { onSelectFilter(filter) },
                            label = { Text(filter.label) },
                        )
                    }
                }
                uiState.errorMessage?.let { message ->
                    Text(
                        text = message,
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp),
                    )
                }
                when {
                    uiState.isLoading -> {
                        Box(
                            modifier = Modifier.fillMaxSize(),
                            contentAlignment = Alignment.Center,
                        ) {
                            CircularProgressIndicator()
                        }
                    }

                    uiState.ads.isEmpty() -> {
                        Box(
                            modifier = Modifier.fillMaxSize(),
                            contentAlignment = Alignment.Center,
                        ) {
                            Text(
                                text = emptyMessage(uiState.watchFilter),
                                style = MaterialTheme.typography.bodyLarge,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                modifier = Modifier.padding(24.dp),
                            )
                        }
                    }

                    else -> {
                        LazyColumn(
                            modifier = Modifier.fillMaxSize(),
                            contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                            verticalArrangement = Arrangement.spacedBy(12.dp),
                        ) {
                            items(
                                items = uiState.ads,
                                key = { it.id },
                            ) { ad ->
                                AdCard(
                                    ad = ad,
                                    onToggleFavorite = { onToggleFavorite(ad) },
                                    onOpen = { onOpenAd(ad) },
                                    onDelete = { pendingDelete = ad },
                                )
                            }
                        }
                    }
                }
            }
        }
    }

    pendingDelete?.let { ad ->
        AlertDialog(
            onDismissRequest = { pendingDelete = null },
            title = { Text("Obriši oglas") },
            text = { Text("Oglas se briše s telefona i iz zajedničke baze. Više se neće vratiti.\n\n${ad.title}") },
            confirmButton = {
                TextButton(
                    onClick = {
                        onDeleteAd(ad)
                        pendingDelete = null
                    },
                ) {
                    Text("Obriši")
                }
            },
            dismissButton = {
                TextButton(onClick = { pendingDelete = null }) {
                    Text("Odustani")
                }
            },
        )
    }

    if (uiState.showServerDialog) {
        ServerUrlDialog(
            currentUrl = uiState.scraperBaseUrl,
            onDismiss = onDismissServerDialog,
            onSave = onSaveServerUrl,
        )
    }
}

@Composable
private fun ServerUrlDialog(
    currentUrl: String,
    onDismiss: () -> Unit,
    onSave: (String) -> Unit,
) {
    var value by remember { mutableStateOf(currentUrl) }
    LaunchedEffect(currentUrl) {
        value = currentUrl
    }
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Adresa scrapera") },
        text = {
            OutlinedTextField(
                value = value,
                onValueChange = { value = it },
                label = { Text("GitHub JSON ili lokalni API") },
                singleLine = true,
            )
        },
        confirmButton = {
            TextButton(onClick = { onSave(value) }) {
                Text("Spremi")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Odustani")
            }
        },
    )
}

private fun emptyMessage(filter: WatchFilter): String = when (filter) {
    WatchFilter.FAVORITES -> "Nema spremljenih favorita"
    else -> "Nema oglasa. Pričekaj GitHub scrape ili pritisni osvježi."
}
