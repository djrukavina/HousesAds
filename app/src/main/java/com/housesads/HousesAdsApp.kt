package com.housesads

import android.app.Application
import androidx.work.Constraints
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.NetworkType
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.housesads.di.AppContainer
import com.housesads.notify.NewAdNotifier
import com.housesads.sync.AdSyncWorker
import java.util.concurrent.TimeUnit

class HousesAdsApp : Application() {
    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer(this)
        NewAdNotifier.createChannel(this)
        scheduleSync()
    }

    private fun scheduleSync() {
        val request = PeriodicWorkRequestBuilder<AdSyncWorker>(15, TimeUnit.MINUTES)
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build(),
            )
            .build()
        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "housesads-sync",
            ExistingPeriodicWorkPolicy.KEEP,
            request,
        )
    }
}
