package com.farmora.data.repository

import android.content.Context
import com.farmora.data.model.Language
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.json.Json
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class LanguageRepository @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val json = Json { ignoreUnknownKeys = true }

    suspend fun getLanguages(): List<Language> = withContext(Dispatchers.IO) {
        try {
            val inputStream = context.assets.open("indian_languages.json")
            val jsonString = inputStream.bufferedReader().use { it.readText() }
            json.decodeFromString<List<Language>>(jsonString)
        } catch (e: Exception) {
            emptyList()
        }
    }

    suspend fun searchLanguages(query: String): List<Language> = withContext(Dispatchers.IO) {
        val allLanguages = getLanguages()
        if (query.isBlank()) return@withContext allLanguages

        allLanguages.filter { language ->
            language.language.contains(query, ignoreCase = true)
        }
    }
}
