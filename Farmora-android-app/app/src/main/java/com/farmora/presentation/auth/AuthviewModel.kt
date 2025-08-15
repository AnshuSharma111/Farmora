package com.farmora.presentation.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.farmora.data.local.UserPreferences
import com.farmora.data.network.NetworkConnectivityManager
import com.farmora.domain.model.AuthResult
import com.farmora.domain.model.NetworkStatus
import com.farmora.domain.repository.AuthRepository
import com.farmora.domain.usecase.GetCurrentUserUseCase
import com.farmora.domain.usecase.IsUserLoggedInUseCase
import com.farmora.domain.usecase.SignInUseCase
import com.farmora.domain.usecase.SignInWithGoogleUseCase
import com.farmora.domain.usecase.SignOutUseCase
import com.farmora.domain.usecase.SignUpUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject


data class AuthUiState(
    val isLoading: Boolean = false,
    val isLoggedIn: Boolean = false,
    val user: com.farmora.data.model.User? = null,
    val errorMessage: String? = null,
    val networkStatus: NetworkStatus = NetworkStatus.Unknown,
    val isFirstTime: Boolean = true,
    val showLoginForm: Boolean = false
)

@HiltViewModel
class AuthviewModel @Inject constructor(
    private val signUpUseCase: SignUpUseCase,
    private val signInUseCase: SignInUseCase,
    private val signInWithGoogleUseCase: SignInWithGoogleUseCase,
    private val signOutUseCase: SignOutUseCase,
    private val getCurrentUserUseCase: GetCurrentUserUseCase,
    private val isUserLoggedInUseCase: IsUserLoggedInUseCase,
    private val authRepository: AuthRepository,
    private val userPreferences: UserPreferences,
    private val networkConnectivityManager: NetworkConnectivityManager
) : ViewModel(){
    private val _uiState = MutableStateFlow(AuthUiState())
    val uiState: StateFlow<AuthUiState> = _uiState.asStateFlow()

    init {
        checkAuthStatus()
        observeNetworkStatus()
    }

    private fun checkAuthStatus() {
        viewModelScope.launch {
            try {
                val isLoggedIn = isUserLoggedInUseCase()
                val user = if (isLoggedIn) getCurrentUserUseCase() else null
                val isFirstTime = userPreferences.isFirstTime.first()

                _uiState.update { currentState ->
                    currentState.copy(
                        isLoggedIn = isLoggedIn,
                        user = user,
                        isFirstTime = isFirstTime
                    )
                }

                if (user != null) {
                    userPreferences.saveUser(user)
                }
            } catch (e: Exception) {
                _uiState.update { it.copy(errorMessage = e.message) }
            }
        }
    }


    private fun observeNetworkStatus() {
        viewModelScope.launch {
            networkConnectivityManager.observeNetworkStatus().collect { status ->
                _uiState.update { it.copy(networkStatus = status) }
            }
        }
    }


    fun signUp(email: String, password: String, confirmPassword: String, name: String) {
        if (password != confirmPassword) {
            _uiState.update { it.copy(errorMessage = "Passwords do not match") }
            return
        }

        if (password.length < 8) {
            _uiState.update { it.copy(errorMessage = "Password must be at least 8 characters") }
            return
        }

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }

            when (val result = signUpUseCase(email, password, name)) {
                is AuthResult.Success -> {
                    userPreferences.saveUser(result.user)
                    userPreferences.setFirstTimeLaunch(false)
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            isLoggedIn = true,
                            user = result.user,
                            isFirstTime = false
                        )
                    }
                }
                is AuthResult.Error -> {
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            errorMessage = result.message
                        )
                    }
                }
                else -> {}
            }
        }
    }


    fun signIn(email: String, password: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }

            when (val result = signInUseCase(email, password)) {
                is AuthResult.Success -> {
                    userPreferences.saveUser(result.user)
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            isLoggedIn = true,
                            user = result.user
                        )
                    }
                }
                is AuthResult.Error -> {
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            errorMessage = result.message
                        )
                    }
                }
                else -> {}
            }
        }
    }


    fun signInWithGoogle() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }

            when (val result = signInWithGoogleUseCase()) {
                is AuthResult.Success -> {
                    userPreferences.saveUser(result.user)
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            isLoggedIn = true,
                            user = result.user
                        )
                    }
                }
                is AuthResult.Error -> {
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            errorMessage = result.message
                        )
                    }
                }
                else -> {}
            }
        }
    }


    fun signOut() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }

            when (val result = signOutUseCase()) {
                is AuthResult.Success -> {
                    userPreferences.clearUserData()
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            isLoggedIn = false,
                            user = null
                        )
                    }
                }
                is AuthResult.Error -> {
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            errorMessage = result.message
                        )
                    }
                }
                else -> {
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            errorMessage = "Unknown error occurred during logout"
                        )
                    }
                }
            }
        }
    }


    fun clearError() {
        _uiState.update { it.copy(errorMessage = null) }
    }

    fun continueToLogin() {
        _uiState.update { it.copy(showLoginForm = true) }
    }

    fun resetLoginForm() {
        _uiState.update { it.copy(showLoginForm = false) }
    }


}