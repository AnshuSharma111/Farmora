package com.farmora.presentation.auth.signup

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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Divider
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Snackbar
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.farmora.domain.model.NetworkStatus
import com.farmora.presentation.auth.AuthviewModel
import com.farmora.presentation.components.OfflineBanner
import com.farmora.ui.theme.*

@Composable
fun SignUpScreen(
    onNavigateToLogin: () -> Unit,
    onNavigateToHome: () -> Unit,
    authViewModel: AuthviewModel = hiltViewModel()
) {

    val uiState by authViewModel.uiState.collectAsState()
    var name by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }
    var isPasswordVisible by remember { mutableStateOf(false) }
    var isConfirmPasswordVisible by remember { mutableStateOf(false) }
    val context = LocalContext.current

    LaunchedEffect(uiState.isLoggedIn) {
        if (uiState.isLoggedIn) {
            onNavigateToHome()
        }
    }

    uiState.errorMessage?.let { message ->
        LaunchedEffect(message) {
            authViewModel.clearError()
        }
    }


    Box(contentAlignment = Alignment.Center,
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        Orange100,
                        Orange50,
                        Color.White
                    )
                )
            )
    ) {

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 16.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center
        ) {
            Spacer(modifier = Modifier.height(40.dp))


            Spacer(modifier = Modifier.height(24.dp))

//            Text(
//                text = "Join Farmora",
//                style = MaterialTheme.typography.headlineLarge,
//                color = Orange800,
//                fontWeight = FontWeight.Bold
//            )
//
//            Text(
//                text = "Start your smart farming journey today",
//                style = MaterialTheme.typography.bodyLarge,
//                color = Orange600,
//                textAlign = TextAlign.Center,
//                modifier = Modifier.padding(top = 8.dp, bottom = 32.dp)
//            )


            // Sign Up Form
            Column(
                modifier = Modifier.fillMaxWidth(),

            ) {
                Column(
                    modifier = Modifier.padding(12.dp)
                ) {
                    Column (modifier = Modifier.fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            text = "Get Started",
                            style = MaterialTheme.typography.headlineMedium,
                            color = Orange800,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(bottom = 4.dp)
                        )

                        Text(
                            text = "create your account now !",
                            style = MaterialTheme.typography.bodySmall,
                            color = Gray900,
                            fontWeight = FontWeight.Normal,
                            modifier = Modifier.padding(bottom = 24.dp)
                        )
                    }

                    // Name Field
                    OutlinedTextField(
                        value = name,
                        onValueChange = { name = it },
                        label = { Text("Full Name") },
                        shape = RoundedCornerShape(50.dp),
                        trailingIcon = {
                            Icon(
                                imageVector = Icons.Default.Person,
                                contentDescription = "Name Icon",
                                tint = Orange600
                            )
                        },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Text),
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Orange600,
                            focusedLabelColor = Orange600,
                            focusedTextColor = Gray800,
                            unfocusedTextColor = Gray700,
                            cursorColor = Orange600,
                        )
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    // Email Field
                    OutlinedTextField(
                        value = email,
                        onValueChange = { email = it },
                        label = { Text("Email Address") },
                        shape = RoundedCornerShape(50.dp),
                        trailingIcon = {
                            Icon(
                                imageVector = Icons.Default.Email,
                                contentDescription = "Email Icon",
                                tint = Orange600
                            )
                        },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Orange600,
                            focusedLabelColor = Orange600,
                            focusedTextColor = Gray800,
                            unfocusedTextColor = Gray700,
                            cursorColor = Orange600,
                        )
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    // Password Field
                    OutlinedTextField(
                        value = password,
                        onValueChange = { password = it },
                        label = { Text("Password") },
                        shape = RoundedCornerShape(50.dp),
                        trailingIcon = {
                            IconButton(onClick = { isPasswordVisible = !isPasswordVisible }) {
                                Icon(
                                    imageVector = if (isPasswordVisible) Icons.Default.Visibility else Icons.Default.VisibilityOff,
                                    contentDescription = if (isPasswordVisible) "Hide password" else "Show password",
                                    tint = Orange600
                                )
                            }
                        },
                        visualTransformation = if (isPasswordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Orange600,
                            focusedLabelColor = Orange600,
                            focusedTextColor = Gray800,
                            unfocusedTextColor = Gray700,
                            cursorColor = Orange600,
                        )
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    // Confirm Password Field
                    OutlinedTextField(
                        value = confirmPassword,
                        onValueChange = { confirmPassword = it },
                        label = { Text("Confirm Password") },
                        shape = RoundedCornerShape(50.dp),
                        trailingIcon = {
                            IconButton(onClick = { isConfirmPasswordVisible = !isConfirmPasswordVisible }) {
                                Icon(
                                    imageVector = if (isConfirmPasswordVisible) Icons.Default.Visibility else Icons.Default.VisibilityOff,
                                    contentDescription = if (isConfirmPasswordVisible) "Hide password" else "Show password",
                                    tint = Orange600
                                )
                            }
                        },
                        visualTransformation = if (isConfirmPasswordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Orange600,
                            focusedLabelColor = Orange600,
                            focusedTextColor = Gray800,
                            unfocusedTextColor = Gray700,
                            cursorColor = Orange600,
                            errorTextColor = Gray800,
                            errorBorderColor = Error,
                            errorLabelColor = Error,
                            errorCursorColor = Orange600
                        ),
                        isError = password.isNotEmpty() && confirmPassword.isNotEmpty() && password != confirmPassword
                    )

                    // Password validation feedback
                    if (password.isNotEmpty() && confirmPassword.isNotEmpty() && password != confirmPassword) {
                        Text(
                            text = "Passwords do not match",
                            color = Error,
                            style = MaterialTheme.typography.bodySmall,
                            modifier = Modifier.padding(start = 16.dp, top = 4.dp)
                        )
                    }

                    if (password.isNotEmpty() && password.length < 8) {
                        Text(
                            text = "Password must be at least 8 characters",
                            color = Warning,
                            style = MaterialTheme.typography.bodySmall,
                            modifier = Modifier.padding(start = 16.dp, top = 4.dp)
                        )
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    // Sign Up Button
                    Button(
                        onClick = {
                            authViewModel.signUp(email, password, confirmPassword, name)
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(50.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Orange600,
                            contentColor = Color.White,
                            disabledContainerColor = Orange100,
                            disabledContentColor = Color.White.copy(alpha = 0.6f)
                        ),
                        enabled = !uiState.isLoading &&
                                name.isNotBlank() &&
                                email.isNotBlank() &&
                                password.isNotBlank() &&
                                confirmPassword.isNotBlank() &&
                                password == confirmPassword &&
                                password.length >= 8
                    ) {
                        if (uiState.isLoading) {
                            CircularProgressIndicator(
                                color = Color.White,
                                modifier = Modifier.size(20.dp)
                            )
                        } else {
                            Text(
                                text = "Create Account",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Divider
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        HorizontalDivider(modifier = Modifier.weight(1f))
                        Text(
                            text = "OR",
                            modifier = Modifier.padding(horizontal = 16.dp),
                            color = Gray500,
                            style = MaterialTheme.typography.bodySmall
                        )
                        HorizontalDivider(modifier = Modifier.weight(1f))
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Google Sign Up Button
                    OutlinedButton(
                        onClick = {
                            authViewModel.signInWithGoogle()
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(50.dp),
                        colors = ButtonDefaults.outlinedButtonColors(
                            contentColor = Gray700
                        ),
                        enabled = !uiState.isLoading
                    ) {
                        Text(
                            text = "Sign up with Google",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Medium
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Sign In Link
            Row(
                horizontalArrangement = Arrangement.Center
            ) {
                Text(
                    text = "Already have an account? ",
                    color = Gray600
                )
                Text(
                    text = "Sign In",
                    color = Orange600,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.clickable { onNavigateToLogin() }
                )
            }

            Spacer(modifier = Modifier.height(32.dp))
        }

        // Error Snackbar
        uiState.errorMessage?.let { message ->
            Snackbar(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(16.dp),
                action = {
                    TextButton(onClick = { authViewModel.clearError() }) {
                        Text("Dismiss")
                    }
                }
            ) {
                Text(message)
            }
        }
    }

}