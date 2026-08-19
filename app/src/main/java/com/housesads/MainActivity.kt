package com.housesads

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.lifecycle.viewmodel.compose.viewModel
import com.housesads.ui.ads.AdListRoute
import com.housesads.ui.ads.AdListViewModel
import com.housesads.ui.ads.AdListViewModelFactory
import com.housesads.ui.theme.HousesAdsTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val app = application as HousesAdsApp
        setContent {
            HousesAdsTheme {
                val viewModel: AdListViewModel = viewModel(
                    factory = AdListViewModelFactory(
                        app,
                        app.container.adRepository,
                        app.container.settingsStore,
                    ),
                )
                AdListRoute(viewModel = viewModel)
            }
        }
    }
}
