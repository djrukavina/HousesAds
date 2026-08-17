package com.housesads.data.sample

import com.housesads.data.model.Ad
import java.util.concurrent.TimeUnit

/**
 * Placeholder feed until scraped Njuškalo listings are wired in.
 */
object SampleAds {
    private val now = System.currentTimeMillis()

    val all: List<Ad> = listOf(
        Ad(
            id = "nj-1001",
            title = "VW Golf 7 1.6 TDI, 2018., 142.000 km",
            priceEur = 12_500.0,
            location = "Zagreb",
            category = "Auti",
            description = "Redovno servisiran, jedan vlasnik, zimski i ljetni set guma.",
            imageUrl = null,
            url = "https://www.njuskalo.hr/auti/golf-7-1001",
            postedAtMillis = now - TimeUnit.HOURS.toMillis(3),
        ),
        Ad(
            id = "nj-1002",
            title = "Dvosoban stan, 58 m², Split — Bačvice",
            priceEur = 189_000.0,
            location = "Split",
            category = "Nekretnine",
            description = "Svijetao stan blizu mora, 2. kat, lift, parkirno mjesto.",
            imageUrl = null,
            url = "https://www.njuskalo.hr/nekretnine/stan-split-1002",
            postedAtMillis = now - TimeUnit.HOURS.toMillis(8),
        ),
        Ad(
            id = "nj-1003",
            title = "iPhone 15 Pro 256 GB, jamstvo",
            priceEur = 890.0,
            location = "Rijeka",
            category = "Mobiteli",
            description = "Bez ogrebotina, originalna kutija i punjač, baterija 91 %.",
            imageUrl = null,
            url = "https://www.njuskalo.hr/mobiteli/iphone-15-pro-1003",
            postedAtMillis = now - TimeUnit.DAYS.toMillis(1),
        ),
        Ad(
            id = "nj-1004",
            title = "BMW 320d Touring, 2019.",
            priceEur = 18_900.0,
            location = "Osijek",
            category = "Auti",
            description = "Servisna knjiga, navigacija, koža, LED svjetla.",
            imageUrl = null,
            url = "https://www.njuskalo.hr/auti/bmw-320d-1004",
            postedAtMillis = now - TimeUnit.DAYS.toMillis(2),
        ),
        Ad(
            id = "nj-1005",
            title = "Trek FX 3 Disc, veličina L",
            priceEur = 450.0,
            location = "Zagreb",
            category = "Bicikli",
            description = "Malo korišten, hidrauličke disk kočnice, nosač prtljage.",
            imageUrl = null,
            url = "https://www.njuskalo.hr/bicikli/trek-fx-1005",
            postedAtMillis = now - TimeUnit.DAYS.toMillis(2),
        ),
        Ad(
            id = "nj-1006",
            title = "MacBook Air M2 13\", 16/512",
            priceEur = 980.0,
            location = "Zadar",
            category = "Računala",
            description = "Kupljen 2023., puno ciklusa ~180, originalna kutija.",
            imageUrl = null,
            url = "https://www.njuskalo.hr/racunala/macbook-air-1006",
            postedAtMillis = now - TimeUnit.DAYS.toMillis(4),
        ),
        Ad(
            id = "nj-1007",
            title = "Garaža 18 m², Novi Zagreb",
            priceEur = 22_000.0,
            location = "Zagreb",
            category = "Nekretnine",
            description = "Zatvorena garaža, struja, laka prilaznost, vlasnički list.",
            imageUrl = null,
            url = "https://www.njuskalo.hr/nekretnine/garaza-1007",
            postedAtMillis = now - TimeUnit.DAYS.toMillis(5),
        ),
        Ad(
            id = "nj-1008",
            title = "IKEA KALLAX 4x4 + kutije",
            priceEur = null,
            location = "Varaždin",
            category = "Namještaj",
            description = "Bijeli, odlično stanje, moguća dostava u okolici.",
            imageUrl = null,
            url = "https://www.njuskalo.hr/namjestaj/kallax-1008",
            postedAtMillis = now - TimeUnit.DAYS.toMillis(6),
        ),
    )
}
