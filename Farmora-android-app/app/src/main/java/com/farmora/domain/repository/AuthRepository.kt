package com.farmora.domain.repository

import com.farmora.data.model.User
import com.farmora.domain.model.AuthResult
import com.farmora.domain.model.NetworkStatus
import kotlinx.coroutines.flow.Flow

interface AuthRepository {
    suspend fun signUp(email: String, password: String, name: String): AuthResult
    suspend fun signIn(email: String, password: String): AuthResult
    suspend fun signInWithGoogle(): AuthResult
    suspend fun signOut(): AuthResult
    suspend fun getCurrentUser(): User?
    suspend fun isUserLoggedIn(): Boolean
    fun getNetworkStatus(): Flow<NetworkStatus>
    suspend fun checkEmailVerification(): Boolean
    suspend fun sendEmailVerification(): AuthResult
}