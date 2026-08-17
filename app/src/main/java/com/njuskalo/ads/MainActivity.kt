package com.njuskalo.ads

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.lifecycle.viewmodel.compose.viewModel
import com.njuskalo.ads.ui.ads.AdListRoute
import com.njuskalo.ads.ui.ads.AdListViewModel
import com.njuskalo.ads.ui.ads.AdListViewModelFactory
import com.njuskalo.ads.ui.theme.NjuskaloAdsTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val app = application as NjuskaloAdsApp
        setContent {
            NjuskaloAdsTheme {
                val viewModel: AdListViewModel = viewModel(
                    factory = AdListViewModelFactory(
                        app.container.adRepository,
                        app.container.settingsStore,
                    ),
                )
                AdListRoute(viewModel = viewModel)
            }
        }
    }
}
