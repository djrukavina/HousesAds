package com.housesads.sync

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.housesads.HousesAdsApp

class AdSyncWorker(
    context: Context,
    params: WorkerParameters,
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val app = applicationContext as? HousesAdsApp ?: return Result.retry()
        return try {
            app.container.adRepository.refresh()
            Result.success()
        } catch (_: Exception) {
            Result.retry()
        }
    }
}
