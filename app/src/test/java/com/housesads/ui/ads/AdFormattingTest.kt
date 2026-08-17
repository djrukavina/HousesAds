package com.housesads.ui.ads

import org.junit.Assert.assertEquals
import org.junit.Test

class AdFormattingTest {

    @Test
    fun formatPriceUsesNegotiableLabelWhenMissing() {
        assertEquals("Po dogovoru", formatPrice(null))
    }

    @Test
    fun sourceLabelMapsKnownSources() {
        assertEquals("Njuškalo", sourceLabel("njuskalo"))
        assertEquals("Index", sourceLabel("index"))
    }
}
