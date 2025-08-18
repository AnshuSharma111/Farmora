package com.farmora.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// Light Theme Color Scheme
private val LightColorScheme = lightColorScheme(
    primary = Green600,
    onPrimary = Color.White,
    primaryContainer = Green100,
    onPrimaryContainer = Green900,
    secondary = Orange500,
    onSecondary = Color.White,
    secondaryContainer = Orange100,
    onSecondaryContainer = Orange600,
    tertiary = Green300,
    onTertiary = Color.White,
    background = Green50,
    onBackground = Green900,
    surface = Color.White,
    onSurface = Green900,
    surfaceVariant = Green100,
    onSurfaceVariant = Green700,
    outline = Green300,
    outlineVariant = Green200,
    scrim = Color.Black.copy(alpha = 0.3f)
)

// Dark Theme Color Scheme
private val DarkColorScheme = darkColorScheme(
    primary = Green400,
    onPrimary = Green900,
    primaryContainer = Green700,
    onPrimaryContainer = Green100,
    secondary = Orange400,
    onSecondary = Orange600,
    secondaryContainer = Orange600,
    onSecondaryContainer = Orange100,
    tertiary = Green200,
    onTertiary = Green800,
    background = Color(0xFF121212),
    onBackground = Green100,
    surface = Color(0xFF1E1E1E),
    onSurface = Green100,
    surfaceVariant = Color(0xFF2D2D2D),
    onSurfaceVariant = Green300,
    outline = Green600,
    outlineVariant = Green700,
    scrim = Color.Black.copy(alpha = 0.5f)
)

@Composable
fun FarmoraTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    // Dynamic color is available on Android 12+
    dynamicColor: Boolean = false, // Disable dynamic colors to use our custom green theme
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}