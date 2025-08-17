package com.farmora.data.model

import kotlinx.serialization.Serializable

@Serializable
data class Language(
    val language: String,
    val code: String
)

data class SelectedLanguage(
    val name: String,
    val code: String
)
