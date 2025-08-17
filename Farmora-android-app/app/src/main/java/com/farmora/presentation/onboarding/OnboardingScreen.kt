package com.farmora.presentation.onboarding

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.farmora.presentation.onboarding.components.OnboardingProgressIndicator
import com.farmora.presentation.onboarding.screens.CropSelectionScreen
import com.farmora.presentation.onboarding.screens.LanguageSelectionScreen
import com.farmora.presentation.onboarding.screens.LocationPermissionScreen
import com.farmora.presentation.onboarding.screens.PlaceholderOnboardingScreen
import com.farmora.ui.theme.Green600
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OnboardingScreen(
    onComplete: (OnboardingData) -> Unit,
    modifier: Modifier = Modifier,
    viewModel: OnboardingViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val pagerState = rememberPagerState(pageCount = { uiState.totalSteps })
    val scope = rememberCoroutineScope()
    val keyboardController = LocalSoftwareKeyboardController.current

    val stepTitles = listOf(
        "Crops Information", "Farm Details", "Goals & Preferences"
    )

    // Sync pager state with viewmodel
    LaunchedEffect(uiState.currentStep) {
        if (pagerState.currentPage != uiState.currentStep) {
            pagerState.animateScrollToPage(uiState.currentStep)
        }
    }

    LaunchedEffect(pagerState.currentPage) {
        if (pagerState.currentPage != uiState.currentStep) {
            // Update viewmodel when user swipes
            if (pagerState.currentPage > uiState.currentStep) {
                viewModel.nextStep()
            } else {
                viewModel.previousStep()
            }
        }
    }

    Scaffold(topBar = {
        OnboardingProgressIndicator(
            currentStep = uiState.currentStep,
            totalSteps = uiState.totalSteps,
            stepTitles = stepTitles
        )
    }, bottomBar = {
        OnboardingBottomBar(
            currentStep = uiState.currentStep,
            totalSteps = uiState.totalSteps,
            canProceed = uiState.canProceed,
            onPrevious = {
                scope.launch {
                    keyboardController?.hide()
                    viewModel.previousStep()
                }
            },
            onNext = {
                scope.launch {
                    keyboardController?.hide()
                    if (uiState.currentStep == uiState.totalSteps - 1) {
                        // Last step - submit onboarding
                        val data = viewModel.submitOnboarding()
                        onComplete(data)
                    } else {
                        viewModel.nextStep()
                    }
                }
            })
    }) { paddingValues ->
        HorizontalPager(
            state = pagerState, modifier = modifier.padding(paddingValues)
        ) { page ->
            when (page) {
                0 -> CropSelectionScreen(
                    uiState = uiState,
                    onSearchQueryChange = viewModel::updateSearchQuery,
                    onSuggestionClick = viewModel::addCrop,
                    onRemoveCrop = viewModel::removeCrop,
                    onClearSearch = viewModel::clearSearch
                )
                1 -> LanguageSelectionScreen(
                    uiState = uiState,
                    onLanguageSearchChange = viewModel::updateLanguageSearchQuery,
                    onLanguageSelect = viewModel::selectLanguage
                )
                2 -> LocationPermissionScreen(
                    uiState = uiState,
                    viewModel = viewModel
                )
            }
        }
    }
}

@Composable
private fun OnboardingBottomBar(
    currentStep: Int,
    totalSteps: Int,
    canProceed: Boolean,
    onPrevious: () -> Unit,
    onNext: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        shadowElevation = 8.dp,
        color = MaterialTheme.colorScheme.surface
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Previous button with green accent to match Next button
            if (currentStep > 0) {
                OutlinedButton(
                    onClick = onPrevious,
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = Green600
                    ),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Green600)
                ) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Previous")
                }
            } else {
                Spacer(modifier = Modifier.weight(1f))
            }

            Spacer(modifier = Modifier.width(16.dp))

            // Next/Finish button with green accent
            Button(
                onClick = onNext,
                enabled = canProceed,
                modifier = Modifier.weight(1f),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Green600,
                    contentColor = androidx.compose.ui.graphics.Color.White,
                    disabledContainerColor = MaterialTheme.colorScheme.surfaceVariant,
                    disabledContentColor = MaterialTheme.colorScheme.onSurfaceVariant
                )
            ) {
                Text(
                    if (currentStep == totalSteps - 1) "Finish" else "Next"
                )
                if (currentStep < totalSteps - 1) {
                    Spacer(modifier = Modifier.width(8.dp))
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.ArrowForward,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
        }
    }
}
