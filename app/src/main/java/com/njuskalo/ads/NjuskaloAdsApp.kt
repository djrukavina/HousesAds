package com.njuskalo.ads

import android.app.Application
import com.njuskalo.ads.di.AppContainer

class NjuskaloAdsApp : Application() {
    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer(this)
    }
}
