package com.farmora.presentation.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import com.farmora.domain.model.NetworkStatus
import com.farmora.presentation.auth.AuthviewModel

@Composable
fun GlobalOfflineBannerWrapper(
    content: @Composable () -> Unit,
    authViewModel: AuthviewModel = hiltViewModel()
) {
    val uiState by authViewModel.uiState.collectAsState()

    Column(modifier = Modifier.fillMaxSize()) {
        // Global offline banner that appears at the top and pushes content down
        OfflineBanner(
            isVisible = uiState.networkStatus == NetworkStatus.Unavailable
        )

        // Main content below the banner
        content()
    }
}
