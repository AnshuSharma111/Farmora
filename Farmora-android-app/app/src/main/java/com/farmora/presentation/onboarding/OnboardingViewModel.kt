package com.farmora.presentation.onboarding

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.farmora.data.model.Crop
import com.farmora.data.model.SelectedCrop
import com.farmora.data.model.Language
import com.farmora.data.model.SelectedLanguage
import com.farmora.data.repository.CropRepository
import com.farmora.data.repository.LanguageRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject
import com.farmora.data.model.UserLocation

data class OnboardingUiState(
    val currentStep: Int = 0,
    val totalSteps: Int = 3, // Can be expanded for more questions
    val selectedCrops: List<SelectedCrop> = emptyList(),
    val searchQuery: String = "",
    val searchSuggestions: List<Crop> = emptyList(),
    val isLoading: Boolean = false,
    val canProceed: Boolean = false,
    // Language selection state
    val selectedLanguage: SelectedLanguage? = null,
    val languages: List<Language> = emptyList(),
    val languageSearchQuery: String = "",
    val filteredLanguages: List<Language> = emptyList(),
    // Location state
    val userLocation: UserLocation? = null,
    val isLocationPermissionGranted: Boolean = false,
    val isLocationLoading: Boolean = false,
    val locationError: String? = null
)

@HiltViewModel
class OnboardingViewModel @Inject constructor(
    private val cropRepository: CropRepository,
    private val languageRepository: LanguageRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(OnboardingUiState())
    val uiState: StateFlow<OnboardingUiState> = _uiState.asStateFlow()

    init {
        loadLanguages()
    }

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

    // Language functions
    private fun loadLanguages() {
        viewModelScope.launch {
            try {
                val languages = languageRepository.getLanguages()
                _uiState.value = _uiState.value.copy(
                    languages = languages,
                    filteredLanguages = languages
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    languages = emptyList(),
                    filteredLanguages = emptyList()
                )
            }
        }
    }

    fun updateLanguageSearchQuery(query: String) {
        _uiState.value = _uiState.value.copy(languageSearchQuery = query)

        val filteredLanguages = if (query.isBlank()) {
            _uiState.value.languages
        } else {
            _uiState.value.languages.filter { language ->
                language.language.contains(query, ignoreCase = true)
            }
        }

        _uiState.value = _uiState.value.copy(filteredLanguages = filteredLanguages)
    }

    fun selectLanguage(language: Language) {
        val selectedLanguage = SelectedLanguage(
            name = language.language,
            code = language.code
        )
        _uiState.value = _uiState.value.copy(
            selectedLanguage = selectedLanguage,
            canProceed = updateCanProceed()
        )
    }

    // Location functions
    fun updateLocationPermissionStatus(isGranted: Boolean) {
        _uiState.value = _uiState.value.copy(
            isLocationPermissionGranted = isGranted,
            canProceed = updateCanProceed()
        )
    }

    fun setLocationLoading(isLoading: Boolean) {
        _uiState.value = _uiState.value.copy(isLocationLoading = isLoading)
    }

    fun setUserLocation(latitude: Double, longitude: Double, address: String? = null) {
        val location = UserLocation(latitude, longitude, address)
        _uiState.value = _uiState.value.copy(
            userLocation = location,
            isLocationLoading = false,
            locationError = null,
            canProceed = updateCanProceed()
        )
    }

    fun setLocationError(error: String) {
        _uiState.value = _uiState.value.copy(
            locationError = error,
            isLocationLoading = false
        )
    }

    fun clearLocationError() {
        _uiState.value = _uiState.value.copy(locationError = null)
    }

    private fun updateCanProceed(): Boolean {
        return when (_uiState.value.currentStep) {
            0 -> _uiState.value.selectedCrops.isNotEmpty()
            1 -> _uiState.value.selectedLanguage != null
            2 -> _uiState.value.isLocationPermissionGranted && _uiState.value.userLocation != null
            else -> false
        }
    }

    fun nextStep() {
        val currentStep = _uiState.value.currentStep
        if (currentStep < _uiState.value.totalSteps - 1) {
            val newStep = currentStep + 1
            _uiState.value = _uiState.value.copy(
                currentStep = newStep,
                canProceed = updateCanProceed()
            )
        }
    }

    fun previousStep() {
        val currentStep = _uiState.value.currentStep
        if (currentStep > 0) {
            val newStep = currentStep - 1
            _uiState.value = _uiState.value.copy(
                currentStep = newStep,
                canProceed = updateCanProceed()
            )
        }
    }

    fun clearSearch() {
        _uiState.value = _uiState.value.copy(
            searchQuery = "", searchSuggestions = emptyList()
        )
    }

    fun submitOnboarding(): OnboardingData {
        return OnboardingData(
            selectedCrops = _uiState.value.selectedCrops,
            selectedLanguage = _uiState.value.selectedLanguage,
            userLocation = _uiState.value.userLocation
        )
    }
}

data class OnboardingData(
    val selectedCrops: List<SelectedCrop>,
    val selectedLanguage: SelectedLanguage?,
    val userLocation: UserLocation?
)
