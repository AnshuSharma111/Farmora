package com.farmora.domain.usecase

import com.farmora.domain.model.AuthResult
import com.farmora.domain.repository.AuthRepository
import javax.inject.Inject

class SignUpUseCase @Inject constructor(
    private val authRepository: AuthRepository
) {
    suspend operator fun invoke(email: String, password: String, name: String): AuthResult {
        return authRepository.signUp(email, password, name)
    }
}

class SignInUseCase @Inject constructor(
    private val authRepository: AuthRepository
) {
    suspend operator fun invoke(email: String, password: String): AuthResult {
        return authRepository.signIn(email, password)
    }
}

class SignInWithGoogleUseCase @Inject constructor(
    private val authRepository: AuthRepository
) {
    suspend operator fun invoke(): AuthResult {
        return authRepository.signInWithGoogle()
    }
}

class SignOutUseCase @Inject constructor(
    private val authRepository: AuthRepository
) {
    suspend operator fun invoke(): AuthResult {
        return authRepository.signOut()
    }
}

class GetCurrentUserUseCase @Inject constructor(
    private val authRepository: AuthRepository
) {
    suspend operator fun invoke() = authRepository.getCurrentUser()
}

class IsUserLoggedInUseCase @Inject constructor(
    private val authRepository: AuthRepository
) {
    suspend operator fun invoke() = authRepository.isUserLoggedIn()
}