package com.iptv.player

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.widget.ProgressBar
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {

    private lateinit var progressBar: ProgressBar
    private val mainHandler = Handler(Looper.getMainLooper())
    private var retryCount = 0
    private val MAX_RETRIES = 3

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        progressBar = findViewById(R.id.progressBar)
        loadChannels()
    }

    private fun loadChannels() {
        progressBar.visibility = ProgressBar.VISIBLE
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val success = DataManager.loadChannels(this@MainActivity)
                withContext(Dispatchers.Main) {
                    progressBar.visibility = ProgressBar.GONE
                    if (success && DataManager.allChannels.isNotEmpty()) {
                        startActivity(Intent(this@MainActivity, PlayerActivity::class.java))
                        finish()
                    } else {
                        if (retryCount < MAX_RETRIES) {
                            retryCount++
                            Toast.makeText(
                                this@MainActivity,
                                "加载失败，重试中... ($retryCount/$MAX_RETRIES)",
                                Toast.LENGTH_SHORT
                            ).show()
                            mainHandler.postDelayed({ loadChannels() }, 3000)
                        } else {
                            Toast.makeText(
                                this@MainActivity,
                                "加载频道列表失败，请检查网络",
                                Toast.LENGTH_LONG
                            ).show()
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e("MainActivity", "Error", e)
                withContext(Dispatchers.Main) {
                    progressBar.visibility = ProgressBar.GONE
                    Toast.makeText(this@MainActivity, "发生错误: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        mainHandler.removeCallbacksAndMessages(null)
    }
}
