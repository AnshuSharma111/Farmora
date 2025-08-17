package com.farmora.data.model

import kotlinx.serialization.Serializable

@Serializable
data class Crop(
    val name: String,
    val species: String
)

@Serializable
data class CropResponse(
    val description: String,
    val source: String,
    val plants: List<Crop>
)

data class SelectedCrop(
    val name: String,
    val id: String = java.util.UUID.randomUUID().toString()
)
