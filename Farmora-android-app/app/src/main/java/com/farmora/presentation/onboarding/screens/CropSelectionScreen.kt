package com.farmora.presentation.onboarding.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.farmora.presentation.onboarding.components.CropSearchField
import com.farmora.presentation.onboarding.components.SelectedCropsDisplay
import com.farmora.presentation.onboarding.OnboardingUiState

@Composable
fun CropSelectionScreen(
    uiState: OnboardingUiState,
    onSearchQueryChange: (String) -> Unit,
    onSuggestionClick: (com.farmora.data.model.Crop) -> Unit,
    onRemoveCrop: (String) -> Unit,
    onClearSearch: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 24.dp, vertical = 32.dp),
        verticalArrangement = Arrangement.spacedBy(32.dp)
    ) {
        // Header section with proper Material Design colors
        Column(
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "What do you grow?",
                style = MaterialTheme.typography.headlineMedium,
                color = MaterialTheme.colorScheme.onSurface,
                fontWeight = FontWeight.SemiBold
            )

            Text(
                text = "Select up to 5 crops to personalize your farming journey and get tailored insights.",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                lineHeight = MaterialTheme.typography.bodyLarge.lineHeight
            )
        }

        // Search field moved above selected crops
        CropSearchField(
            searchQuery = uiState.searchQuery,
            suggestions = uiState.searchSuggestions,
            isLoading = uiState.isLoading,
            onQueryChange = onSearchQueryChange,
            onSuggestionClick = onSuggestionClick,
            onClearSearch = onClearSearch,
            modifier = Modifier.fillMaxWidth()
        )

        // Selected crops display with enhanced spacing (now below search)
        SelectedCropsDisplay(
            selectedCrops = uiState.selectedCrops,
            onRemoveCrop = onRemoveCrop,
            modifier = Modifier.fillMaxWidth()
        )

        // Limit info card with proper theming
        if (uiState.selectedCrops.size >= 5) {
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.errorContainer
                ),
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "You've reached the maximum of 5 crops. Remove one to add another.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onErrorContainer,
                    modifier = Modifier.padding(20.dp),
                    textAlign = TextAlign.Center,
                    fontWeight = FontWeight.Medium
                )
            }
        }

        // Bottom spacing for comfortable scrolling
        Spacer(modifier = Modifier.height(80.dp))
    }
}
