package com.farmora.domain.model

sealed class AuthResult {
    data object Loading : AuthResult()
    data class Success(val user: com.farmora.data.model.User) : AuthResult()
    data class Error(val message: String) : AuthResult()
}

sealed class NetworkStatus {
    data object Available : NetworkStatus()
    data object Unavailable : NetworkStatus()
    data object Unknown : NetworkStatus()
}
