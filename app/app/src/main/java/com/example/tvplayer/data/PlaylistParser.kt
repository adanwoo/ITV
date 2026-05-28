package com.example.tvplayer.data

import android.content.Context
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.runBlocking
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL

object PlaylistParser {
    private const val PLAYLIST_URL = "https://itv.19860519.xyz/output/tv.txt"
    private val client = OkHttpClient.Builder()
        .connectTimeout(10, java.util.concurrent.TimeUnit.SECONDS)
        .readTimeout(10, java.util.concurrent.TimeUnit.SECONDS)
        .build()
    
    private var channels = mutableListOf<Channel>()
    
    suspend fun loadPlaylist(): List<Channel> {
        return try {
            val request = Request.Builder()
                .url(PLAYLIST_URL)
                .header("User-Agent", "IPTVPlayer/1.0")
                .build()
            
            val response = client.newCall(request).execute()
            if (!response.isSuccessful) {
                throw Exception("HTTP ${response.code}")
            }
            
            val body = response.body?.string() ?: ""
            parseTxt(body)
        } catch (e: Exception) {
            e.printStackTrace()
            emptyList()
        }
    }
    
    private fun parseTxt(content: String): List<Channel> {
        val lines = content.lines()
        val channelsList = mutableListOf<Channel>()
        var currentGroup: String? = null
        var idCounter = 0
        
        for (line in lines) {
            val trimmed = line.trim()
            if (trimmed.isEmpty()) continue
            
            if (trimmed.startsWith("#")) {
                // 分类行
                currentGroup = trimmed.drop(1).trim()
            } else {
                // 频道行
                val parts = trimmed.split(",", limit = 2)
                val name = parts[0].trim()
                val url = if (parts.size > 1) parts[1].trim() else trimmed
                if (url.isNotEmpty() && (url.startsWith("http://") || url.startsWith("https://"))) {
                    channelsList.add(Channel(
                        id = idCounter++,
                        name = name,
                        url = url,
                        group = currentGroup
                    ))
                }
            }
        }
        
        channels = channelsList.toMutableList()
        return channels
    }
    
    fun getChannels(): List<Channel> = channels
    
    fun getChannelById(id: Int): Channel? = channels.find { it.id == id }
}
