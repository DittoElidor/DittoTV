package com.elidor.dittotv

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.view.KeyEvent
import android.view.WindowManager
import androidx.fragment.app.FragmentActivity
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView

class VideoPlayerActivity : FragmentActivity() {

    private var player: ExoPlayer? = null
    private lateinit var playerView: PlayerView
    private var relativePath: String? = null
    private val seekIncrementMs = 10000L

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setContentView(R.layout.activity_video_player)
        playerView = findViewById(R.id.player_view)
        playerView.controllerShowTimeoutMs = 3000
    }

    private fun initializePlayer() {
        player = ExoPlayer.Builder(this)
            .build()
            .also { exoPlayer ->
                playerView.player = exoPlayer

                val videoUrl = intent.getStringExtra("videoUrl")
                relativePath = intent.getStringExtra("relativePath")
                val startPosition = intent.getLongExtra("startPosition", 0L)

                val mediaItem = MediaItem.fromUri(videoUrl!!)
                exoPlayer.setMediaItem(mediaItem)
                exoPlayer.seekTo(startPosition)
                exoPlayer.playWhenReady = true
                exoPlayer.prepare()
            }
    }

    private fun releasePlayer() {
        player?.let {
            val resultIntent = Intent().apply {
                putExtra("relativePath", relativePath)
                putExtra("position", it.currentPosition)
                putExtra("duration", it.duration)
            }
            setResult(Activity.RESULT_OK, resultIntent)
            it.release()
        }
        player = null
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        player?.let {
            when (keyCode) {
                KeyEvent.KEYCODE_DPAD_RIGHT -> {
                    it.seekTo(it.currentPosition + seekIncrementMs)
                    return true
                }
                KeyEvent.KEYCODE_DPAD_LEFT -> {
                    it.seekTo(it.currentPosition - seekIncrementMs)
                    return true
                }
            }
        }
        return super.onKeyDown(keyCode, event)
    }

    override fun onResume() {
        super.onResume()
        if (player == null) {
            initializePlayer()
        }
    }

    override fun onPause() {
        super.onPause()
        releasePlayer()
    }
}
