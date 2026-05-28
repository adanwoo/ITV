package com.example.tvplayer.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.tv.material3.*
import androidx.compose.ui.res.stringResource
import com.example.tvplayer.R

// 手机版主题
private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFFE50914),
    secondary = Color(0xFFB81C0C),
    tertiary = Color(0xFFE06D0D),
    background = Color(0xFF141414),
    surface = Color(0xFF1F1F1F),
    onPrimary = Color.White,
    onSecondary = Color.White,
    onBackground = Color.White,
    onSurface = Color.White
)

private val LightColorScheme = lightColorScheme(
    primary = Color(0xFFE50914),
    secondary = Color(0xFFB81C0C),
    tertiary = Color(0xFFE06D0D),
    background = Color(0xFFF5F5F5),
    surface = Color.White,
    onPrimary = Color.White,
    onSecondary = Color.White,
    onBackground = Color.Black,
    onSurface = Color.Black
)

@Composable
fun TVPlayerTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    MaterialTheme(
        colorScheme = colorScheme,
        content = content
    )
}

// 电视版主题
@Composable
fun TvTheme(
    content: @Composable () -> Unit
) {
    TvMaterialTheme(
        colorScheme = TvColorSchemes.dark,
        content = content
    )
}
