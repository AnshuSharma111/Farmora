package com.farmora.presentation.onboarding

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.farmora.data.model.Crop
import com.farmora.data.model.SelectedCrop
import com.farmora.data.repository.CropRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class OnboardingUiState(
    val currentStep: Int = 0,
    val totalSteps: Int = 3, // Can be expanded for more questions
    val selectedCrops: List<SelectedCrop> = emptyList(),
    val searchQuery: String = "",
    val searchSuggestions: List<Crop> = emptyList(),
    val isLoading: Boolean = false,
    val canProceed: Boolean = false
)

@HiltViewModel
class OnboardingViewModel @Inject constructor(
    private val cropRepository: CropRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(OnboardingUiState())
    val uiState: StateFlow<OnboardingUiState> = _uiState.asStateFlow()

    fun updateSearchQuery(query: String) {
        _uiState.value = _uiState.value.copy(searchQuery = query)

        if (query.isNotBlank() && query.length >= 2) {
            searchCrops(query)
        } else {
            _uiState.value = _uiState.value.copy(searchSuggestions = emptyList())
        }
    }

    private fun searchCrops(query: String) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            try {
                val suggestions = cropRepository.searchCrops(query)
                _uiState.value = _uiState.value.copy(
                    searchSuggestions = suggestions, isLoading = false
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    searchSuggestions = emptyList(), isLoading = false
                )
            }
        }
    }

    fun addCrop(crop: Crop) {
        val currentCrops = _uiState.value.selectedCrops
        if (currentCrops.size < 5 && currentCrops.none { it.name == crop.name }) {
            val newCrop = SelectedCrop(name = crop.name)
            val updatedCrops = currentCrops + newCrop
            _uiState.value = _uiState.value.copy(
                selectedCrops = updatedCrops,
                searchQuery = "",
                searchSuggestions = emptyList(),
                canProceed = updatedCrops.isNotEmpty()
            )
        }
    }

    fun removeCrop(cropId: String) {
        val updatedCrops = _uiState.value.selectedCrops.filter { it.id != cropId }
        _uiState.value = _uiState.value.copy(
            selectedCrops = updatedCrops, canProceed = updatedCrops.isNotEmpty()
        )
    }

    fun nextStep() {
        val currentStep = _uiState.value.currentStep
        if (currentStep < _uiState.value.totalSteps - 1) {
            _uiState.value = _uiState.value.copy(currentStep = currentStep + 1)
        }
    }

    fun previousStep() {
        val currentStep = _uiState.value.currentStep
        if (currentStep > 0) {
            _uiState.value = _uiState.value.copy(currentStep = currentStep - 1)
        }
    }

    fun clearSearch() {
        _uiState.value = _uiState.value.copy(
            searchQuery = "", searchSuggestions = emptyList()
        )
    }

    fun submitOnboarding(): OnboardingData {
        // Return all collected data for final submission
        return OnboardingData(
            selectedCrops = _uiState.value.selectedCrops
        )
    }
}

data class OnboardingData(
    val selectedCrops: List<SelectedCrop>
    // Add more fields as you add more onboarding steps
)
