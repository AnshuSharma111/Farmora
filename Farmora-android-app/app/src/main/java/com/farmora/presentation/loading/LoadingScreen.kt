package com.farmora.presentation.loading

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import com.farmora.R
import kotlinx.coroutines.delay

@Composable
fun LoadingScreen(
    onLoadingComplete: () -> Unit
) {
    // Display the loading screen for 2.5 seconds
    LaunchedEffect(Unit) {
        delay(2500) // 2.5 seconds
        onLoadingComplete()
    }

    Box(
        modifier = Modifier.fillMaxSize()
    ) {
        Image(
            painter = painterResource(id = R.drawable.farmora_loading),
            contentDescription = "Loading",
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop // This will cover the entire screen
        )
    }
}
