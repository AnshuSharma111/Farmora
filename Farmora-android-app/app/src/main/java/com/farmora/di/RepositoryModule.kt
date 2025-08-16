package com.farmora.di

import com.farmora.data.remote.AppwriteAuthService
import com.farmora.domain.repository.AuthRepository
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindAuthRepository(
        appwriteAuthService: AppwriteAuthService
    ): AuthRepository

}