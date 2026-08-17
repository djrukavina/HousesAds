package com.housesads.notify

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.housesads.MainActivity
import com.housesads.data.model.Ad

object NewAdNotifier {
    const val CHANNEL_ID = "new_listings"

    fun createChannel(context: Context) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val channel = NotificationChannel(
            CHANNEL_ID,
            "Novi oglasi",
            NotificationManager.IMPORTANCE_HIGH,
        ).apply {
            description = "Obavijesti kad se pojavi oglas koji odgovara tvojim filterima"
        }
        context.getSystemService(NotificationManager::class.java)
            .createNotificationChannel(channel)
    }

    fun show(context: Context, ads: List<Ad>) {
        if (ads.isEmpty()) return
        createChannel(context)
        val manager = NotificationManagerCompat.from(context)
        ads.take(5).forEachIndexed { index, ad ->
            val price = ad.priceEur?.let { "${it.toInt()} €" } ?: "Po dogovoru"
            val openIntent = if (ad.url.isNotBlank()) {
                Intent(Intent.ACTION_VIEW, Uri.parse(ad.url))
            } else {
                Intent(context, MainActivity::class.java)
            }
            val pending = PendingIntent.getActivity(
                context,
                ad.id.hashCode(),
                openIntent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
            )
            val notification = NotificationCompat.Builder(context, CHANNEL_ID)
                .setSmallIcon(android.R.drawable.ic_dialog_info)
                .setContentTitle("Novi oglas: ${ad.category}")
                .setContentText("${ad.title} · $price")
                .setStyle(NotificationCompat.BigTextStyle().bigText("${ad.title}\n$price · ${ad.location}"))
                .setContentIntent(pending)
                .setAutoCancel(true)
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .build()
            try {
                manager.notify(ad.id.hashCode() + index, notification)
            } catch (_: SecurityException) {
                return
            }
        }
    }
}
