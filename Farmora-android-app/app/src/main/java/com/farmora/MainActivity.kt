package com.farmora

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.farmora.navigation.FarmoraNavigation
import com.farmora.presentation.components.GlobalOfflineBannerWrapper
import com.farmora.ui.theme.FarmoraTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            FarmoraTheme {
                GlobalOfflineBannerWrapper(content = { FarmoraNavigation() })
            }
        }
    }
}
