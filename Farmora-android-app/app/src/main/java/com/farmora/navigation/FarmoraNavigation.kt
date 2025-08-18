package com.farmora.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.farmora.presentation.auth.AuthviewModel
import com.farmora.presentation.auth.login.LoginScreen
import com.farmora.presentation.auth.signup.SignUpScreen
import com.farmora.presentation.home.HomeScreen
import com.farmora.presentation.loading.LoadingScreen
import com.farmora.presentation.onboarding.navigation.OnboardingNavigation


sealed class Screen(val route: String) {
    object Loading : Screen("loading")
    object Login : Screen("login")
    object SignUp : Screen("signup")
    object Onboarding : Screen("onboarding")
    object Home : Screen("home")
}

@Composable
fun FarmoraNavigation(
    modifier: Modifier = Modifier,
    navController: NavHostController = rememberNavController(),
    authViewModel: AuthviewModel = hiltViewModel()
) {
    val uiState by authViewModel.uiState.collectAsState()

    // Start with loading screen
    val startDestination = Screen.Loading.route

    NavHost(navController = navController,
        startDestination = startDestination,
        modifier = modifier
    ) {
        composable(Screen.Loading.route) {
            LoadingScreen(
                onLoadingComplete = {
                    // Determine where to navigate after loading
                    val nextDestination = when {
                        uiState.isLoggedIn -> Screen.Home.route
                        else -> Screen.Login.route
                    }

                    navController.navigate(nextDestination) {
                        popUpTo(Screen.Loading.route) { inclusive = true }
                    }
                }
            )
        }

        composable(Screen.Login.route) {
            LoginScreen(
                modifier,
                onNavigateToSignUp = {
                    navController.navigate(Screen.SignUp.route)
                },
                onNavigateToHome = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                },
                authViewModel = authViewModel
            )
        }

        composable(Screen.SignUp.route) {
            SignUpScreen(
                onNavigateToLogin = {
                    navController.popBackStack()
                },
                onNavigateToOnboarding = {
                    navController.navigate(Screen.Onboarding.route) {
                        popUpTo(Screen.SignUp.route) { inclusive = true }
                    }
                },
                authViewModel = authViewModel
            )
        }

        composable(Screen.Onboarding.route) {
            OnboardingNavigation(
                onComplete = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Onboarding.route) { inclusive = true }
                    }
                }
            )
        }

        composable(Screen.Home.route) {
            HomeScreen(
                onSignOut = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                },
                authViewModel = authViewModel
            )
        }

    }

}