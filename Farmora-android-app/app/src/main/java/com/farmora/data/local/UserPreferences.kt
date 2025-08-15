package com.farmora.data.local

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.farmora.data.model.User
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "farmora_prefs")

@Singleton
class UserPreferences @Inject constructor(
    @ApplicationContext private val context: Context
){
    private val dataStore = context.dataStore

    companion object {
        private val USER_DATA_KEY = stringPreferencesKey("user_data")
        private val IS_LOGGED_IN_KEY = booleanPreferencesKey("is_logged_in")
        private val IS_FIRST_TIME_KEY = booleanPreferencesKey("is_first_time")
    }

    suspend fun saveUser(user: User) {
        dataStore.edit { preferences ->
            preferences[USER_DATA_KEY] = Json.encodeToString(user)
            preferences[IS_LOGGED_IN_KEY] = true
        }
    }

    suspend fun getUser(): User? {
        return try {
            val preferences = dataStore.data.map { preferences ->
                preferences[USER_DATA_KEY]?.let { userJson ->
                    Json.decodeFromString<User>(userJson)
                }
            }
            preferences.map { it }.collect { it }
        } catch (e: Exception) {
            null
        } as User?
    }

    val isLoggedIn: Flow<Boolean> = dataStore.data.map { preferences ->
        preferences[IS_LOGGED_IN_KEY] ?: false
    }

    val isFirstTime: Flow<Boolean> = dataStore.data.map { preferences ->
        preferences[IS_FIRST_TIME_KEY] ?: true
    }

    suspend fun setFirstTimeLaunch(isFirstTime: Boolean) {
        dataStore.edit { preferences ->
            preferences[IS_FIRST_TIME_KEY] = isFirstTime
        }
    }

    suspend fun clearUserData() {
        dataStore.edit { preferences ->
            preferences.clear()
        }
    }
}