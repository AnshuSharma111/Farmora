package com.farmora.data.model

import kotlinx.serialization.Serializable

@Serializable
data class User (
    val id: String = "",
    val email: String = "",
    val name: String = "",
    val avatar: String? = null,
    val isEmailVerified: Boolean = false,
    val createdAt: String = "",
    val updatedAt: String = ""
)