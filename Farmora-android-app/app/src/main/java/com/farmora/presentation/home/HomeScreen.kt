package com.farmora.presentation.home

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.ArrowForward
import androidx.compose.material.icons.filled.Cloud
import androidx.compose.material.icons.filled.Launch
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material.icons.filled.Thermostat
import androidx.compose.material.icons.filled.TrendingUp
import androidx.compose.material.icons.outlined.CalendarToday
import androidx.compose.material.icons.outlined.Insights
import androidx.compose.material3.Badge
import androidx.compose.material3.BadgedBox
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.airbnb.lottie.LottieComposition
import com.airbnb.lottie.compose.LottieAnimation
import com.airbnb.lottie.compose.LottieCompositionSpec
import com.airbnb.lottie.compose.LottieConstants
import com.airbnb.lottie.compose.animateLottieCompositionAsState
import com.airbnb.lottie.compose.rememberLottieComposition
import com.farmora.R
import com.farmora.presentation.auth.AuthviewModel
import com.farmora.ui.theme.Gray400
import com.farmora.ui.theme.Orange50
import com.farmora.ui.theme.Orange700
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.delay
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onSignOut: () -> Unit, authViewModel: AuthviewModel
) {
    val uiState by authViewModel.uiState.collectAsState()
    var isRecording by remember { mutableStateOf(false) }
    var showDelayedText by remember { mutableStateOf(false) }

    // Animation states for fullscreen voice recording
    val expandAnimation = remember { Animatable(0f) }
    val collapseAnimation = remember { Animatable(0f) }

    // Multiple animatables for waveform effect
    val waveAnimation1 = remember { Animatable(0f) }
    val waveAnimation2 = remember { Animatable(0f) }
    val waveAnimation3 = remember { Animatable(0f) }
    val waveAnimation4 = remember { Animatable(0f) }
    val waveAnimation5 = remember { Animatable(0f) }

    // Floating animation for cards
    val cardFloatAnimation by animateFloatAsState(
        targetValue = if (isRecording) 5f else 0f, animationSpec = tween(300)
    )

    // Get current time
    val currentTime = remember {
        SimpleDateFormat("HH:mm", Locale.getDefault()).format(Date())
    }
    val currentDate = remember {
        SimpleDateFormat("EEEE, MMM dd", Locale.getDefault()).format(Date())
    }

    // Username from auth state or default
    val username = uiState.user?.name ?: "Farmer"

    // Lottie animation for voice waveform
    val composition by rememberLottieComposition(LottieCompositionSpec.RawRes(R.raw.lottieanim))
    val lottieProgress by animateLottieCompositionAsState(
        composition = composition,
        iterations = LottieConstants.IterateForever,
        isPlaying = isRecording
    )

    // Handle recording state changes with animations
    LaunchedEffect(isRecording) {
        if (isRecording) {
            // Reset delayed text state
            showDelayedText = false

            // Expand animation
            expandAnimation.animateTo(
                targetValue = 1f, animationSpec = tween(600)
            )

            // Show delayed text after 10 seconds
            delay(10000)
            if (isRecording) { // Check if still recording
                showDelayedText = true
            }
        } else {
            // Reset delayed text
            showDelayedText = false

            // Collapse animation
            collapseAnimation.animateTo(
                targetValue = 1f, animationSpec = tween(600)
            )
            // Reset collapse animation for next time
            collapseAnimation.snapTo(0f)
            // Reset expand animation
            expandAnimation.snapTo(0f)
        }
    }

    // Waveform animation for mic button when not in fullscreen mode
    LaunchedEffect(isRecording) {
        if (isRecording) {
            val job1 = async {
                waveAnimation1.animateTo(
                    targetValue = 1f, animationSpec = infiniteRepeatable(
                        animation = tween(600, easing = LinearEasing),
                        repeatMode = RepeatMode.Reverse
                    )
                )
            }
            val job2 = async {
                delay(100)
                waveAnimation2.animateTo(
                    targetValue = 1f, animationSpec = infiniteRepeatable(
                        animation = tween(800, easing = LinearEasing),
                        repeatMode = RepeatMode.Reverse
                    )
                )
            }
            val job3 = async {
                delay(200)
                waveAnimation3.animateTo(
                    targetValue = 1f, animationSpec = infiniteRepeatable(
                        animation = tween(700, easing = LinearEasing),
                        repeatMode = RepeatMode.Reverse
                    )
                )
            }
            val job4 = async {
                delay(150)
                waveAnimation4.animateTo(
                    targetValue = 1f, animationSpec = infiniteRepeatable(
                        animation = tween(650, easing = LinearEasing),
                        repeatMode = RepeatMode.Reverse
                    )
                )
            }
            val job5 = async {
                delay(250)
                waveAnimation5.animateTo(
                    targetValue = 1f, animationSpec = infiniteRepeatable(
                        animation = tween(750, easing = LinearEasing),
                        repeatMode = RepeatMode.Reverse
                    )
                )
            }
            awaitAll(job1, job2, job3, job4, job5)
        } else {
            waveAnimation1.animateTo(0f)
            waveAnimation2.animateTo(0f)
            waveAnimation3.animateTo(0f)
            waveAnimation4.animateTo(0f)
            waveAnimation5.animateTo(0f)
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        // Main Home Screen Content
        if (!isRecording) {
            Scaffold(
                topBar = {
                    TopAppBar(
                        title = {
                        Column {
                            Text(
                                text = "Hi, $username! 👋",
                                style = MaterialTheme.typography.headlineSmall.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = MaterialTheme.colorScheme.onBackground
                                )
                            )
                            Text(
                                text = "Welcome back to Farmora",
                                style = MaterialTheme.typography.bodySmall.copy(
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            )
                        }
                    }, navigationIcon = {
                        IconButton(onClick = { /* Profile click */ }) {
                            Icon(
                                imageVector = Icons.Default.AccountCircle,
                                contentDescription = "Profile",
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(32.dp)
                            )
                        }
                    }, actions = {
                        BadgedBox(
                            badge = {
                                Badge(
                                    containerColor = MaterialTheme.colorScheme.secondary
                                )
                            }) {
                            IconButton(onClick = { /* Notifications */ }) {
                                Icon(
                                    imageVector = Icons.Default.Notifications,
                                    contentDescription = "Notifications",
                                    tint = MaterialTheme.colorScheme.primary
                                )
                            }
                        }
                        IconButton(onClick = { /* Settings click */ }) {
                            Icon(
                                imageVector = Icons.Default.Settings,
                                contentDescription = "Settings",
                                tint = MaterialTheme.colorScheme.primary
                            )
                        }
                    }, colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = MaterialTheme.colorScheme.background
                    ), modifier = Modifier.padding(top = 8.dp) // Added top padding
                    )
                }, containerColor = MaterialTheme.colorScheme.background
            ) { paddingValues ->
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues)
                        .padding(horizontal = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    item { Spacer(modifier = Modifier.height(8.dp)) }

                    // Quick Stats Row
                    item {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            QuickStatCard(
                                title = "Crops",
                                value = "3",
                                icon = Icons.Outlined.Insights,
                                modifier = Modifier.weight(1f)
                            )
                            QuickStatCard(
                                title = "Tasks",
                                value = "12",
                                icon = Icons.Outlined.CalendarToday,
                                modifier = Modifier.weight(1f)
                            )
                            QuickStatCard(
                                title = "Yield",
                                value = "+15%",
                                icon = Icons.Default.TrendingUp,
                                modifier = Modifier.weight(1f)
                            )
                        }
                    }

                    // AI Query Card
                    item {
                        Card(
                            modifier = Modifier
                                .fillMaxWidth()
                                .shadow(
                                    elevation = cardFloatAnimation.dp,
                                    shape = RoundedCornerShape(20.dp)
                                )
                                .clickable { /* Navigate to AI chat */ },
                            colors = CardDefaults.cardColors(
                                containerColor = MaterialTheme.colorScheme.surface
                            ),
                            elevation = CardDefaults.cardElevation(defaultElevation = 8.dp),
                            shape = RoundedCornerShape(20.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(
                                        brush = Brush.linearGradient(
                                            colors = listOf(
                                                MaterialTheme.colorScheme.primary,
                                                MaterialTheme.colorScheme.primaryContainer
                                            )
                                        )
                                    )
                                    .padding(24.dp)
                            ) {
                                Column {
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Column(modifier = Modifier.weight(1f)) {
                                            Text(
                                                text = "Ask Farmora AI",
                                                style = MaterialTheme.typography.titleLarge.copy(
                                                    fontWeight = FontWeight.Bold,
                                                    color = MaterialTheme.colorScheme.onPrimary
                                                )
                                            )
                                            Spacer(modifier = Modifier.height(8.dp))
                                            Text(
                                                text = "Try 'Should I plant rice, given the weather next month?'",
                                                style = MaterialTheme.typography.bodyMedium.copy(
                                                    color = MaterialTheme.colorScheme.onPrimary.copy(
                                                        alpha = 0.9f
                                                    )
                                                ),
                                                maxLines = 2,
                                                overflow = TextOverflow.Ellipsis
                                            )
                                        }
                                        Icon(
                                            imageVector = Icons.Default.ArrowForward,
                                            contentDescription = "Go to AI Chat",
                                            tint = MaterialTheme.colorScheme.onPrimary,
                                            modifier = Modifier.size(24.dp)
                                        )
                                    }
                                }
                            }
                        }
                    }

                    // Weather Card
                    item {
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(
                                containerColor = MaterialTheme.colorScheme.surface
                            ),
                            elevation = CardDefaults.cardElevation(defaultElevation = 6.dp),
                            shape = RoundedCornerShape(20.dp)
                        ) {
                            Column(
                                modifier = Modifier.padding(24.dp)
                            ) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = "Weather Today",
                                        style = MaterialTheme.typography.titleLarge.copy(
                                            fontWeight = FontWeight.Bold,
                                            color = MaterialTheme.colorScheme.onSurface
                                        )
                                    )
                                    Text(
                                        text = currentTime,
                                        style = MaterialTheme.typography.bodyMedium.copy(
                                            color = MaterialTheme.colorScheme.onSurfaceVariant
                                        )
                                    )
                                }
                                Spacer(modifier = Modifier.height(16.dp))

                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    // Weather Info
                                    Column {
                                        Row(
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Icon(
                                                imageVector = Icons.Default.Cloud,
                                                contentDescription = "Weather",
                                                tint = MaterialTheme.colorScheme.primary,
                                                modifier = Modifier.size(20.dp)
                                            )
                                            Spacer(modifier = Modifier.width(8.dp))
                                            Text(
                                                text = "Rainy",
                                                style = MaterialTheme.typography.bodyLarge.copy(
                                                    fontWeight = FontWeight.Medium,
                                                    color = MaterialTheme.colorScheme.onSurface
                                                )
                                            )
                                        }
                                        Spacer(modifier = Modifier.height(8.dp))
                                        Text(
                                            text = currentDate,
                                            style = MaterialTheme.typography.bodyMedium.copy(
                                                color = MaterialTheme.colorScheme.onSurfaceVariant
                                            )
                                        )
                                    }

                                    // Temperature
                                    Row(
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Icon(
                                            imageVector = Icons.Default.Thermostat,
                                            contentDescription = "Temperature",
                                            tint = MaterialTheme.colorScheme.secondary,
                                            modifier = Modifier.size(20.dp)
                                        )
                                        Spacer(modifier = Modifier.width(4.dp))
                                        Text(
                                            text = "28°C",
                                            style = MaterialTheme.typography.headlineSmall.copy(
                                                fontWeight = FontWeight.Bold,
                                                color = MaterialTheme.colorScheme.onSurface
                                            )
                                        )
                                    }
                                }

                                Spacer(modifier = Modifier.height(16.dp))

                                // Additional weather info
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceEvenly
                                ) {
                                    WeatherInfoItem(
                                        "Humidity",
                                        "72%",
                                        MaterialTheme.colorScheme.primary
                                    )
                                    WeatherInfoItem(
                                        "Wind",
                                        "15 km/h",
                                        MaterialTheme.colorScheme.primary
                                    )
                                    WeatherInfoItem(
                                        "UV Index",
                                        "6",
                                        MaterialTheme.colorScheme.secondary
                                    )
                                }
                            }
                        }
                    }

                    // Latest Information Card
                    item {
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(
                                containerColor = MaterialTheme.colorScheme.surface
                            ),
                            elevation = CardDefaults.cardElevation(defaultElevation = 6.dp),
                            shape = RoundedCornerShape(20.dp)
                        ) {
                            Column(
                                modifier = Modifier.padding(24.dp)
                            ) {
                                Text(
                                    text = "Latest Information",
                                    style = MaterialTheme.typography.titleLarge.copy(
                                        fontWeight = FontWeight.Bold,
                                        color = MaterialTheme.colorScheme.onSurface
                                    )
                                )
                                Spacer(modifier = Modifier.height(16.dp))

                                NewsItem(
                                    title = "Government issues new scheme called 'Meri Saheli'",
                                    onClick = { /* Navigate to news detail */ })

                                Spacer(modifier = Modifier.height(12.dp))

                                NewsItem(
                                    title = "SC Judge Udit Verma overrules farmer's concern",
                                    onClick = { /* Navigate to news detail */ })
                            }
                        }
                    }

                    item { Spacer(modifier = Modifier.height(120.dp)) } // Space for FAB
                }
            }
        }

        // Fullscreen Voice Recording Overlay
        if (isRecording || expandAnimation.value > 0f) {
            VoiceRecordingOverlay(
                isRecording = isRecording,
                expandProgress = expandAnimation.value,
                collapseProgress = collapseAnimation.value,
                lottieProgress = lottieProgress,
                composition = composition,
                showDelayedText = showDelayedText,
                onStopRecording = { isRecording = false })
        }

        // Microphone Button (only show when not in fullscreen recording)
        if (!isRecording && expandAnimation.value == 0f) {
            // Fixed Microphone Button at Bottom Center
            Box(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(bottom = 32.dp)
            ) {
                // Extract colors outside Canvas context
                val waveColor = MaterialTheme.colorScheme.primary
                val micButtonPrimary = MaterialTheme.colorScheme.primary
                val micButtonContainer = MaterialTheme.colorScheme.primaryContainer
                val micIconColor = MaterialTheme.colorScheme.onPrimary

                // Waveform animation around the microphone when recording
                if (isRecording) {
                    Canvas(
                        modifier = Modifier
                            .size(140.dp)
                            .align(Alignment.Center)
                    ) {
                        val center = Offset(size.width / 2, size.height / 2)
                        val baseRadius = 40.dp.toPx()

                        val waves = listOf(
                            waveAnimation1.value,
                            waveAnimation2.value,
                            waveAnimation3.value,
                            waveAnimation4.value,
                            waveAnimation5.value
                        )

                        waves.forEachIndexed { index, wave ->
                            val radius = baseRadius + (wave * (15 + index * 8).dp.toPx())
                            val alpha = (1 - wave) * 0.4f

                            drawCircle(
                                color = waveColor.copy(alpha = alpha),
                                radius = radius,
                                center = center,
                                style = androidx.compose.ui.graphics.drawscope.Stroke(
                                    width = 2.dp.toPx(), cap = StrokeCap.Round
                                )
                            )
                        }
                    }
                }

                // Microphone Button
                Box(
                    modifier = Modifier
                        .size(80.dp)
                        .align(Alignment.Center)
                        .shadow(
                            elevation = 12.dp, shape = CircleShape
                        )
                        .clip(CircleShape)
                        .background(
                            brush = Brush.radialGradient(
                                colors = listOf(
                                    micButtonPrimary, micButtonContainer
                                )
                            )
                        )
                        .clickable {
                            isRecording = !isRecording
                            // TODO: Implement voice recording functionality
                        }, contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.Mic,
                        contentDescription = "Voice Assistant",
                        tint = micIconColor,
                        modifier = Modifier.size(32.dp)
                    )
                }
            }
        }
    }
}

@Composable
private fun QuickStatCard(
    title: String, value: String, icon: ImageVector, modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.height(100.dp), // Fixed height for consistency
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // Icon and Title in same row
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = title,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(24.dp)
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = title, style = MaterialTheme.typography.bodyMedium.copy(
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                )
            }
            Spacer(modifier = Modifier.height(8.dp))
            // Value below
            Text(
                text = value, style = MaterialTheme.typography.titleLarge.copy(
                    fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            )
        }
    }
}

@Composable
private fun WeatherInfoItem(
    label: String, value: String, color: Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = value, style = MaterialTheme.typography.titleMedium.copy(
                fontWeight = FontWeight.Bold, color = color
            )
        )
        Text(
            text = label, style = MaterialTheme.typography.bodySmall.copy(
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        )
    }
}

@Composable
private fun NewsItem(
    title: String, onClick: () -> Unit
) {
    Row(modifier = Modifier
        .fillMaxWidth()
        .clickable { onClick() }
        .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically) {
        Text(
            text = "•", style = MaterialTheme.typography.titleMedium.copy(
                color = MaterialTheme.colorScheme.primary
            ), modifier = Modifier.padding(end = 8.dp)
        )
        Text(
            text = title, style = MaterialTheme.typography.bodyMedium.copy(
                color = MaterialTheme.colorScheme.onSurface
            ), modifier = Modifier.weight(1f)
        )
        Icon(
            imageVector = Icons.Default.Launch,
            contentDescription = "Read more",
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(16.dp)
        )
    }
}

@Composable
fun VoiceRecordingOverlay(
    isRecording: Boolean,
    expandProgress: Float,
    collapseProgress: Float,
    lottieProgress: Float,
    composition: LottieComposition?,
    showDelayedText: Boolean,
    onStopRecording: () -> Unit
) {
    // Animated background for fullscreen green overlay expanding from mic button position
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.radialGradient(
                    colors = listOf(
                        MaterialTheme.colorScheme.primary,
                        MaterialTheme.colorScheme.primaryContainer,
                        MaterialTheme.colorScheme.primary
                    ),
                    // Position the gradient center at bottom center (where mic button is)
                    center = Offset(0.5f, 0.85f), // Bottom center position
                    radius = (expandProgress * 1500f).coerceAtLeast(1f)
                )
            )
            .graphicsLayer {
                // Scale animation for the entire overlay expanding from mic position
                scaleX = expandProgress
                scaleY = expandProgress
                alpha = expandProgress
            }, contentAlignment = Alignment.Center
    ) {
        // Show content when expansion is significant
        if (expandProgress > 0.3f) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
                modifier = Modifier
                    .fillMaxSize()
                    .padding(32.dp)
            ) {
                Spacer(modifier = Modifier.weight(1f))

                // Title Text
                Text(
                    text = "Listening...", style = MaterialTheme.typography.headlineMedium.copy(
                        fontWeight = FontWeight.Bold, color = Color.White
                    ), modifier = Modifier.graphicsLayer {
                            alpha = (expandProgress - 0.3f).coerceAtLeast(0f) / 0.7f
                            scaleX = expandProgress
                            scaleY = expandProgress
                        })

                Spacer(modifier = Modifier.height(32.dp))

                // Lottie Animation for Voice Waveform - Centered
                Box(
                    modifier = Modifier
                        .size(200.dp)
                        .graphicsLayer {
                            scaleX = expandProgress
                            scaleY = expandProgress
                            alpha = expandProgress
                        }, contentAlignment = Alignment.Center
                ) {
                    LottieAnimation(
                        composition = composition,
                        progress = { lottieProgress },
                        modifier = Modifier.fillMaxSize()
                    )
                }

                // Delayed Text - Appears 10 seconds after recording starts
                if (showDelayedText) {
                    Spacer(modifier = Modifier.height(24.dp))
                    Text(
                        text = "Is it a good time to sell my crops and will i get good returns",
                        style = MaterialTheme.typography.bodyLarge.copy(
                            color = Gray400
                        ),
                        modifier = Modifier.padding(horizontal = 16.dp)
                    )
                }

                Spacer(modifier = Modifier.weight(1f))

                // Stop Recording Instructions
                Text(
                    text = "Tap stop when finished",
                    style = MaterialTheme.typography.bodyLarge.copy(
                        color = Color.White.copy(alpha = 0.9f)
                    ),
                    modifier = Modifier.graphicsLayer {
                            alpha = (expandProgress - 0.5f).coerceAtLeast(0f) / 0.5f
                        })

                Spacer(modifier = Modifier.height(32.dp))

                // Stop Button with orange accent color
                Button(
                    onClick = onStopRecording,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Orange50, // Orange accent color
                        contentColor = Orange700 // Darker orange for better contrast
                    ),
                    modifier = Modifier
                        .height(56.dp)
                        .width(120.dp)
                        .graphicsLayer {
                            scaleX = (expandProgress - 0.4f).coerceAtLeast(0f) / 0.6f
                            scaleY = (expandProgress - 0.4f).coerceAtLeast(0f) / 0.6f
                            alpha = (expandProgress - 0.4f).coerceAtLeast(0f) / 0.6f
                            // Apply collapse animation
                            val collapseScale = 1f - collapseProgress
                            scaleX *= collapseScale
                            scaleY *= collapseScale
                            alpha *= collapseScale
                        },
                    shape = RoundedCornerShape(28.dp),
                    elevation = ButtonDefaults.buttonElevation(defaultElevation = 8.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Stop,
                            contentDescription = "Stop Recording",
                            tint = Orange700, // Darker orange for better contrast
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "Stop", style = MaterialTheme.typography.labelLarge.copy(
                                fontWeight = FontWeight.Bold,
                                color = Orange700 // Darker orange for better contrast
                            )
                        )
                    }
                }

                Spacer(modifier = Modifier.height(64.dp))
            }
        }
    }
}
