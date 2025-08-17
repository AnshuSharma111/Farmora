package com.farmora.data.repository

import android.content.Context
import com.farmora.data.model.Crop
import com.farmora.data.model.CropResponse
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.json.Json
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class CropRepository @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val json = Json { ignoreUnknownKeys = true }

    suspend fun getCrops(): List<Crop> = withContext(Dispatchers.IO) {
        try {
            val inputStream = context.assets.open("crops.json")
            val jsonString = inputStream.bufferedReader().use { it.readText() }
            val cropResponse = json.decodeFromString<CropResponse>(jsonString)
            cropResponse.plants
        } catch (e: Exception) {
            emptyList()
        }
    }

    suspend fun searchCrops(query: String): List<Crop> = withContext(Dispatchers.IO) {
        val allCrops = getCrops()
        if (query.isBlank()) return@withContext emptyList()

        allCrops.filter { crop ->
            crop.name.contains(query, ignoreCase = true)
        }.take(10) // Limit suggestions to 10 items
    }
}
