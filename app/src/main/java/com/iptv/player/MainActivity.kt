package com.iptv.player

import android.content.Intent
import android.os.Bundle
import android.view.KeyEvent
import android.view.View
import android.widget.ProgressBar
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    
    private lateinit var progressBar: ProgressBar
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        progressBar = findViewById(R.id.progressBar)
        
        loadChannels()
    }
    
    private fun loadChannels() {
        progressBar.visibility = View.VISIBLE
        
        lifecycleScope.launch {
            val success = DataManager.loadChannels(this@MainActivity)
            progressBar.visibility = View.GONE
            
            if (success && DataManager.allChannels.isNotEmpty()) {
                // 启动播放界面
                val intent = Intent(this@MainActivity, PlayerActivity::class.java)
                startActivity(intent)
                finish()
            } else {
                Toast.makeText(
                    this@MainActivity,
                    "加载频道列表失败，请检查网络连接",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }
    
    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        // 按返回键退出应用
        if (keyCode == KeyEvent.KEYCODE_BACK) {
            finish()
            return true
        }
        return super.onKeyDown(keyCode, event)
    }
}
