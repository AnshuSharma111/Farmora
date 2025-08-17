package com.farmora.presentation.onboarding.navigation

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.farmora.presentation.onboarding.OnboardingScreen

sealed class OnboardingScreen(val route: String) {
    object Main : OnboardingScreen("onboarding_main")
}

@Composable
fun OnboardingNavigation(
    onComplete: () -> Unit,
    modifier: Modifier = Modifier,
    navController: NavHostController = rememberNavController()
) {
    NavHost(
        navController = navController,
        startDestination = OnboardingScreen.Main.route,
        modifier = modifier
    ) {
        composable(OnboardingScreen.Main.route) {
            OnboardingScreen(
                onComplete = { onboardingData ->
                    // Here you can handle the onboarding data
                    // For now, just complete the onboarding
                    onComplete()
                })
        }
    }
}
