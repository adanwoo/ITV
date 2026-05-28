package com.iptv.player

import android.os.Bundle
import android.view.GestureDetector
import android.view.MotionEvent
import android.view.View
import android.widget.TextView
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GestureDetectorCompat
import androidx.fragment.app.commit
import com.google.android.exoplayer2.ExoPlayer
import com.google.android.exoplayer2.MediaItem
import com.google.android.exoplayer2.PlaybackException
import com.google.android.exoplayer2.Player
import com.google.android.exoplayer2.ui.PlayerView
import com.iptv.player.databinding.ActivityPlayerBinding
import com.iptv.player.model.Channel
import com.iptv.player.utils.PlaylistLoader
import com.iptv.player.utils.PreferencesManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class PlayerActivity : AppCompatActivity() {
    private lateinit var binding: ActivityPlayerBinding
    private lateinit var player: ExoPlayer
    private var channels = listOf<Channel>()
    private var currentChannelIndex = -1
    private var isChannelListVisible = false
    private lateinit var gestureDetector: GestureDetectorCompat
    private val channelListFragment by lazy { ChannelListFragment() }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPlayerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        window.decorView.systemUiVisibility = (View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                or View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                or View.SYSTEM_UI_FLAG_FULLSCREEN)

        setupPlayer()
        setupGestures()
        loadPlaylist()
    }

    private fun setupPlayer() {
        player = ExoPlayer.Builder(this).build()
        binding.playerView.player = player
        player.addListener(object : Player.Listener {
            override fun onPlaybackStateChanged(playbackState: Int) {
                if (playbackState == Player.STATE_READY) {
                    hideMessage()
                }
            }
            override fun onPlayerError(error: PlaybackException) {
                showMessage("播放失败: ${error.message}")
            }
        })
    }

    private fun setupGestures() {
        gestureDetector = GestureDetectorCompat(this, object : GestureDetector.SimpleOnGestureListener() {
            override fun onSingleTapUp(e: MotionEvent): Boolean {
                toggleChannelList()
                return true
            }

            override fun onScroll(
                e1: MotionEvent?,
                e2: MotionEvent,
                distanceX: Float,
                distanceY: Float
            ): Boolean {
                if (e1 != null && Math.abs(e2.y - e1.y) > 100) {
                    // 垂直滑动切换频道
                    if (e2.y > e1.y) {
                        previousChannel()
                    } else {
                        nextChannel()
                    }
                    return true
                }
                return false
            }
        })
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        gestureDetector.onTouchEvent(event)
        return true
    }

    private fun loadPlaylist() {
        showMessage("加载节目单...")
        CoroutineScope(Dispatchers.IO).launch {
            val result = PlaylistLoader.loadFromUrl(BuildConfig.PLAYLIST_URL)
            withContext(Dispatchers.Main) {
                if (result.isSuccess) {
                    channels = result.getOrNull() ?: emptyList()
                    if (channels.isNotEmpty()) {
                        val lastIndex = PreferencesManager.getLastChannelIndex(this@PlayerActivity)
                        currentChannelIndex = if (lastIndex in channels.indices) lastIndex else 0
                        playChannel(currentChannelIndex)
                    } else {
                        showMessage("节目单为空")
                    }
                } else {
                    showMessage("加载失败: ${result.exceptionOrNull()?.message}")
                }
            }
        }
    }

    private fun playChannel(index: Int) {
        if (index !in channels.indices) return
        currentChannelIndex = index
        val channel = channels[currentChannelIndex]
        val mediaItem = MediaItem.Builder()
            .setUri(channel.url)
            .setMimeType("application/x-mpegURL")
            .build()
        player.setMediaItem(mediaItem)
        player.prepare()
        player.playWhenReady = true
        updateChannelName(channel.name)
        PreferencesManager.saveLastChannelIndex(this, currentChannelIndex)
        // 关闭频道列表
        if (isChannelListVisible) toggleChannelList()
    }

    private fun updateChannelName(name: String) {
        binding.tvChannelName.text = name
        binding.tvChannelName.visibility = View.VISIBLE
        // 3秒后隐藏
        binding.tvChannelName.postDelayed({
            if (::binding.isInitialized) binding.tvChannelName.visibility = View.GONE
        }, 3000)
    }

    private fun nextChannel() {
        if (channels.isEmpty()) return
        val next = (currentChannelIndex + 1) % channels.size
        playChannel(next)
    }

    private fun previousChannel() {
        if (channels.isEmpty()) return
        val prev = if (currentChannelIndex - 1 < 0) channels.size - 1 else currentChannelIndex - 1
        playChannel(prev)
    }

    private fun toggleChannelList() {
        if (channels.isEmpty()) return
        if (isChannelListVisible) {
            supportFragmentManager.commit {
                remove(channelListFragment)
            }
            binding.channelListContainer.visibility = View.GONE
            binding.overlay.visibility = View.GONE
            isChannelListVisible = false
        } else {
            if (!channelListFragment.isAdded) {
                supportFragmentManager.commit {
                    add(binding.channelListContainer.id, channelListFragment)
                }
            }
            channelListFragment.setChannels(channels, if (currentChannelIndex >= 0) channels[currentChannelIndex] else null)
            channelListFragment.setOnChannelSelectedListener { channel ->
                val newIndex = channels.indexOfFirst { it.name == channel.name }
                if (newIndex >= 0) playChannel(newIndex)
            }
            binding.channelListContainer.visibility = View.VISIBLE
            binding.overlay.visibility = View.VISIBLE
            isChannelListVisible = true
        }
    }

    private fun showMessage(msg: String) {
        binding.tvMessage.text = msg
        binding.tvMessage.visibility = View.VISIBLE
        binding.tvMessage.postDelayed({ hideMessage() }, 3000)
    }

    private fun hideMessage() {
        if (::binding.isInitialized) binding.tvMessage.visibility = View.GONE
    }

    override fun onStart() {
        super.onStart()
        if (::player.isInitialized) player.playWhenReady = true
    }

    override fun onStop() {
        super.onStop()
        if (::player.isInitialized) player.playWhenReady = false
    }

    override fun onDestroy() {
        super.onDestroy()
        if (::player.isInitialized) player.release()
    }
}
