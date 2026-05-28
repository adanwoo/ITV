package com.example.tvplayer.data

data class Channel(
    val id: Int,
    val name: String,
    val url: String,
    val group: String? = null
)
