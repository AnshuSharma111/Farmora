package com.farmora.presentation.home

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ExitToApp
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.farmora.domain.model.NetworkStatus
import com.farmora.presentation.auth.AuthviewModel
import com.farmora.ui.theme.Blue100
import com.farmora.ui.theme.Blue50
import com.farmora.ui.theme.Blue600
import com.farmora.ui.theme.Blue800
import com.farmora.ui.theme.Gray100
import com.farmora.ui.theme.Gray600
import com.farmora.ui.theme.Gray700
import com.farmora.ui.theme.Green100
import com.farmora.ui.theme.Green600
import com.farmora.ui.theme.Green700
import com.farmora.ui.theme.Green800
import com.farmora.ui.theme.Orange100
import com.farmora.ui.theme.Orange800
import com.farmora.ui.theme.Warning

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onSignOut: () -> Unit,
    authViewModel: AuthviewModel = hiltViewModel()
) {
    val uiState by authViewModel.uiState.collectAsState()

    // Handle sign out navigation
    LaunchedEffect(uiState.isLoggedIn) {
        if (!uiState.isLoggedIn && !uiState.isLoading) {
            onSignOut()
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        Blue100,
                        Blue50,
                        Color.White
                    )
                )
            )
    ) {
        Column(
            modifier = Modifier.fillMaxSize()
        ) {
            // Top App Bar
            TopAppBar(
                title = {
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "🌱",
                            fontSize = 24.sp,
                            modifier = Modifier.padding(end = 8.dp)
                        )
                        Text(
                            text = "Farmora",
                            fontWeight = FontWeight.Bold,
                            color = Green700
                        )
                    }
                },
                actions = {
                    IconButton(
                        onClick = {
                            authViewModel.signOut()
                        }
                    ) {
                        Icon(
                            imageVector = Icons.Default.ExitToApp,
                            contentDescription = "Sign Out",
                            tint = Green600
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color.White
                )
            )


            // Main Content
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                item {
                    // Welcome Card
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = Color.White
                        ),
                        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
                    ) {
                        Column(
                            modifier = Modifier.padding(24.dp)
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Person,
                                    contentDescription = "User",
                                    tint = Blue600,
                                    modifier = Modifier
                                        .size(48.dp)
                                        .clip(RoundedCornerShape(24.dp))
                                        .background(Blue100)
                                        .padding(12.dp)
                                )

                                Column(
                                    modifier = Modifier.padding(start = 16.dp)
                                ) {
                                    Text(
                                        text = "Welcome back!",
                                        style = MaterialTheme.typography.headlineSmall,
                                        color = Blue800,
                                        fontWeight = FontWeight.Bold
                                    )
                                    uiState.user?.let { user ->
                                        Text(
                                            text = user.name.ifEmpty { user.email },
                                            style = MaterialTheme.typography.bodyLarge,
                                            color = Blue600
                                        )
                                    }
                                }
                            }
                        }
                    }
                }

            }
        }
    }
}
