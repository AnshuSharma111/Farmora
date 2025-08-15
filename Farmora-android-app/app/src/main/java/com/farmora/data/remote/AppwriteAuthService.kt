package com.farmora.data.remote

import android.content.Context
import com.farmora.constants.AppwriteConfig
import com.farmora.data.model.User
import com.farmora.domain.model.AuthResult
import com.farmora.domain.model.NetworkStatus
import com.farmora.domain.repository.AuthRepository
import dagger.hilt.android.qualifiers.ApplicationContext
import io.appwrite.Client
import io.appwrite.services.Account
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AppwriteAuthService @Inject constructor(
    @ApplicationContext private val context: Context
) : AuthRepository {

    private val client = Client(context)
        .setEndpoint(AppwriteConfig.APPWRITE_PUBLIC_ENDPOINT)
        .setProject(AppwriteConfig.APPWRITE_PROJECT_ID)

    private val account = Account(client)


    override suspend fun signUp(email: String, password: String, name: String): AuthResult {
        return try {
            val user = account.create(
                userId = io.appwrite.ID.unique(),
                email = email,
                password = password,
                name = name
            )

            AuthResult.Success(
                User(
                    id = user.id,
                    email = user.email,
                    name = user.name,
                    isEmailVerified = user.emailVerification,
                    createdAt = user.registration,
                    updatedAt = user.registration
                )
            )
        } catch (e: Exception) {
            AuthResult.Error(e.message ?: "Sign up failed")
        }
    }

    override suspend fun signIn(email: String, password: String): AuthResult {
        return try {
            val session = account.createEmailPasswordSession(email, password)
            val user = account.get()

            AuthResult.Success(
                User(
                    id = user.id,
                    email = user.email,
                    name = user.name,
                    isEmailVerified = user.emailVerification,
                    createdAt = user.registration,
                    updatedAt = user.registration
                )
            )
        } catch (e: Exception) {
            AuthResult.Error(e.message ?: "Sign in failed")
        }
    }


    override suspend fun signInWithGoogle(): AuthResult {
        return try {
            // This would require Google OAuth setup in Appwrite
            // For now, returning an error to implement later
            AuthResult.Error("Google sign-in not implemented yet")
        } catch (e: Exception) {
            AuthResult.Error(e.message ?: "Google sign in failed")
        }
    }



    override suspend fun signOut(): AuthResult {
        return try {
            account.deleteSession("current")
            AuthResult.Success(User())
        } catch (e: Exception) {
            AuthResult.Error(e.message ?: "Sign out failed")
        }
    }

    override suspend fun getCurrentUser(): User? {
        return try {
            val user = account.get()
            User(
                id = user.id,
                email = user.email,
                name = user.name,
                isEmailVerified = user.emailVerification,
                createdAt = user.registration,
                updatedAt = user.registration
            )
        } catch (e: Exception) {
            null
        }
    }


    override suspend fun isUserLoggedIn(): Boolean {
        return try {
            account.get()
            true
        } catch (e: Exception) {
            false
        }
    }

    override fun getNetworkStatus(): Flow<NetworkStatus> = flow {
        // Simple network check - in a real app, you'd use ConnectivityManager
        try {
            val user = account.get()
            emit(NetworkStatus.Available)
        } catch (e: Exception) {
            emit(NetworkStatus.Unavailable)
        }
    }

    override suspend fun checkEmailVerification(): Boolean {
        TODO("Not yet implemented")
    }

    override suspend fun sendEmailVerification(): AuthResult {
        TODO("Not yet implemented")
    }


//    override suspend fun checkEmailVerification(): Boolean {
//        return try {
//            val user = account.get()
//            user.emailVerification
//        } catch (e: Exception) {
//            false
//        }
//    }
//
//    override suspend fun sendEmailVerification(): AuthResult {
//        return try {
//            account.createVerification("${AppwriteConfig.GOOGLE_OAUTH_REDIRECT_URL}/verify")
//            AuthResult.Success(User())
//        } catch (e: Exception) {
//            AuthResult.Error(e.message ?: "Failed to send verification email")
//        }
//    }


}