package com.farmora.presentation.onboarding.screens

import android.Manifest
import android.content.Intent
import android.net.Uri
import android.provider.Settings
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.MyLocation
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.farmora.data.model.UserLocation
import com.farmora.presentation.onboarding.OnboardingUiState
import com.farmora.presentation.onboarding.OnboardingViewModel
import com.farmora.ui.theme.*
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationCallback
import com.google.android.gms.location.LocationRequest
import com.google.android.gms.location.LocationResult
import com.google.android.gms.location.LocationServices
import com.google.android.gms.location.Priority
import kotlinx.coroutines.tasks.await

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LocationPermissionScreen(
    uiState: OnboardingUiState,
    viewModel: OnboardingViewModel,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val fusedLocationClient = remember { LocationServices.getFusedLocationProviderClient(context) }
    var permissionDenied by remember { mutableStateOf(false) }

    // Permission launcher
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        viewModel.updateLocationPermissionStatus(isGranted)
        if (isGranted) {
            permissionDenied = false
            getCurrentLocation(fusedLocationClient, viewModel)
        } else {
            permissionDenied = true
        }
    }

    // Check if permission is already granted
    LaunchedEffect(Unit) {
        val hasPermission = ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == android.content.pm.PackageManager.PERMISSION_GRANTED

        viewModel.updateLocationPermissionStatus(hasPermission)
        if (hasPermission) {
            permissionDenied = false
            getCurrentLocation(fusedLocationClient, viewModel)
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 24.dp, vertical = 32.dp),
        verticalArrangement = Arrangement.spacedBy(32.dp)
    ) {
        // Header section
        Column(
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Surface(
                    modifier = Modifier.size(48.dp),
                    shape = RoundedCornerShape(12.dp),
                    color = Green100
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            imageVector = Icons.Default.LocationOn,
                            contentDescription = null,
                            tint = Green700,
                            modifier = Modifier.size(24.dp)
                        )
                    }
                }

                Text(
                    text = "Enable location access",
                    style = MaterialTheme.typography.headlineMedium,
                    color = MaterialTheme.colorScheme.onSurface,
                    fontWeight = FontWeight.SemiBold
                )
            }

            Text(
                text = "We need your location to provide personalized farming recommendations, weather updates, and region-specific agricultural insights tailored to your area.",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                lineHeight = MaterialTheme.typography.bodyLarge.lineHeight
            )
        }

        // Location status card
        LocationStatusCard(
            uiState = uiState,
            modifier = Modifier.fillMaxWidth()
        )

        // Permission/location handling
        when {
            uiState.isLocationPermissionGranted && uiState.userLocation != null -> {
                // Permission granted and location obtained - don't show anything extra
                // The user can proceed with the Next button
            }

            uiState.isLocationPermissionGranted && uiState.userLocation == null -> {
                // Permission granted but getting location
                if (uiState.isLocationLoading) {
                    LocationLoadingCard(modifier = Modifier.fillMaxWidth())
                } else {
                    LocationRequestCard(
                        onRequestLocation = {
                            getCurrentLocation(fusedLocationClient, viewModel)
                        },
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }

            else -> {
                // Permission not granted
                PermissionRequestCard(
                    onRequestPermission = {
                        permissionLauncher.launch(Manifest.permission.ACCESS_FINE_LOCATION)
                    },
                    onOpenSettings = {
                        val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                            data = Uri.fromParts("package", context.packageName, null)
                        }
                        context.startActivity(intent)
                    },
                    showSettingsOption = permissionDenied,
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }

        // Error handling
        uiState.locationError?.let { error ->
            ErrorCard(
                error = error,
                onDismiss = { viewModel.clearLocationError() },
                onRetry = {
                    viewModel.clearLocationError()
                    if (uiState.isLocationPermissionGranted) {
                        getCurrentLocation(fusedLocationClient, viewModel)
                    } else {
                        permissionLauncher.launch(Manifest.permission.ACCESS_FINE_LOCATION)
                    }
                },
                modifier = Modifier.fillMaxWidth()
            )
        }

        // Bottom spacing
        Spacer(modifier = Modifier.height(80.dp))
    }
}

@Composable
private fun LocationStatusCard(
    uiState: OnboardingUiState,
    modifier: Modifier = Modifier
) {
    val statusText = when {
        uiState.userLocation != null -> "Location Enabled"
        uiState.isLocationPermissionGranted -> "Permission Granted"
        else -> "Location Required"
    }

    val statusColor = when {
        uiState.userLocation != null -> Green600
        uiState.isLocationPermissionGranted -> Orange600
        else -> MaterialTheme.colorScheme.outline
    }

    // Only show the card when there's meaningful status to display
    // Don't show flickering states during transitions
    if (!uiState.isLocationLoading) {
        Card(
            modifier = modifier,
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f)
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(20.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Surface(
                    modifier = Modifier.size(40.dp),
                    shape = RoundedCornerShape(10.dp),
                    color = statusColor.copy(alpha = 0.2f)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            imageVector = if (uiState.userLocation != null) Icons.Default.CheckCircle else Icons.Default.LocationOn,
                            contentDescription = null,
                            tint = statusColor,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                }

                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Location Status",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = statusText,
                        style = MaterialTheme.typography.titleMedium,
                        color = statusColor,
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }
        }
    }
}

@Composable
private fun LocationSuccessCard(
    location: UserLocation,
    onRefreshLocation: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = Green50
        ),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.CheckCircle,
                    contentDescription = null,
                    tint = Green600,
                    modifier = Modifier.size(24.dp)
                )
                Text(
                    text = "Location Successfully Obtained",
                    style = MaterialTheme.typography.titleMedium,
                    color = Green800,
                    fontWeight = FontWeight.SemiBold
                )
            }

            Column(
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = "Coordinates: ${String.format("%.4f", location.latitude)}, ${String.format("%.4f", location.longitude)}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = Green700
                )

                location.address?.let { address ->
                    Text(
                        text = "Address: $address",
                        style = MaterialTheme.typography.bodyMedium,
                        color = Green700
                    )
                }
            }

            OutlinedButton(
                onClick = onRefreshLocation,
                colors = ButtonDefaults.outlinedButtonColors(
                    contentColor = Green600
                ),
            ) {
                Icon(
                    imageVector = Icons.Default.MyLocation,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("Refresh Location")
            }
        }
    }
}

@Composable
private fun LocationLoadingCard(
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = Orange50
        ),
        shape = RoundedCornerShape(16.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            CircularProgressIndicator(
                modifier = Modifier.size(24.dp),
                strokeWidth = 2.dp,
                color = Orange600
            )

            Text(
                text = "Getting your location...",
                style = MaterialTheme.typography.bodyLarge,
                color = Orange800,
                fontWeight = FontWeight.Medium
            )
        }
    }
}

@Composable
private fun LocationRequestCard(
    onRequestLocation: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        ),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Permission granted! Now let's get your location.",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center
            )

            Button(
                onClick = onRequestLocation,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Green600,
                    contentColor = Color.White
                )
            ) {
                Icon(
                    imageVector = Icons.Default.MyLocation,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("Get My Location")
            }
        }
    }
}

@Composable
private fun PermissionRequestCard(
    onRequestPermission: () -> Unit,
    onOpenSettings: () -> Unit,
    showSettingsOption: Boolean,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.3f)
        ),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Location permission is required to proceed with onboarding and provide personalized farming recommendations.",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurface,
                textAlign = TextAlign.Center
            )

            Row(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Button(
                    onClick = onRequestPermission,
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Green600,
                        contentColor = Color.White
                    )
                ) {
                    Text("Grant Permission")
                }

                if (showSettingsOption) {
                    OutlinedButton(
                        onClick = onOpenSettings,
                        modifier = Modifier.weight(1f),
                        colors = ButtonDefaults.outlinedButtonColors(
                            contentColor = MaterialTheme.colorScheme.onSurface
                        )
                    ) {
                        Icon(
                            imageVector = Icons.Default.Settings,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Settings")
                    }
                }
            }
        }
    }
}

@Composable
private fun ErrorCard(
    error: String,
    onDismiss: () -> Unit,
    onRetry: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.errorContainer
        ),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "Error: $error",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onErrorContainer
            )

            Row(
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                TextButton(onClick = onDismiss) {
                    Text("Dismiss")
                }
                Button(
                    onClick = onRetry,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Green600,
                        contentColor = Color.White
                    )
                ) {
                    Text("Retry")
                }
            }
        }
    }
}

private fun getCurrentLocation(
    fusedLocationClient: FusedLocationProviderClient,
    viewModel: OnboardingViewModel
) {
    viewModel.setLocationLoading(true)

    try {
        fusedLocationClient.lastLocation
            .addOnSuccessListener { location ->
                if (location != null) {
                    viewModel.setUserLocation(
                        latitude = location.latitude,
                        longitude = location.longitude
                    )
                } else {
                    // Request fresh location
                    val locationRequest = LocationRequest.Builder(
                        Priority.PRIORITY_HIGH_ACCURACY,
                        10000
                    ).build()

                    val locationCallback = object : LocationCallback() {
                        override fun onLocationResult(result: LocationResult) {
                            result.lastLocation?.let { loc ->
                                viewModel.setUserLocation(
                                    latitude = loc.latitude,
                                    longitude = loc.longitude
                                )
                            }
                            fusedLocationClient.removeLocationUpdates(this)
                        }
                    }

                    fusedLocationClient.requestLocationUpdates(
                        locationRequest,
                        locationCallback,
                        null
                    )
                }
            }
            .addOnFailureListener { exception ->
                viewModel.setLocationError("Failed to get location: ${exception.message}")
            }
    } catch (securityException: SecurityException) {
        viewModel.setLocationError("Location permission denied")
    } catch (exception: Exception) {
        viewModel.setLocationError("Error getting location: ${exception.message}")
    }
}
