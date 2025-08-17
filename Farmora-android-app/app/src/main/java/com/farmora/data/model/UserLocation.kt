package com.farmora.data.model

data class UserLocation(
    val latitude: Double,
    val longitude: Double,
    val address: String? = null
)
